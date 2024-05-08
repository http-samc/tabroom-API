import re
import os
import requests
from requests_cache import DO_NOT_CACHE, CachedSession
from langchain_openai.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
from typing import Tuple
from typing import List, TypedDict
from datetime import datetime
from shared.const import API_BASE
from ..utils.soup import get_soup
from ..utils.clean import clean_element
from ..utils.id import get_id

requests = CachedSession(expire_after=DO_NOT_CACHE)

NOW = datetime.now().isoformat() + "Z"
FLOW_MODEL = "ft:gpt-3.5-turbo-0613:debate-land::8OClXt5D"
PROG_MODEL = "ft:gpt-3.5-turbo-0613:debate-land::8Pi4BpVM"
FLOW_PROMPT = """
You are a coach for high school debate. You want to classify judge paradigms based on whether the judge is "lay" or "flow". Parents and non-technical people are lay, coaches, former debaters, etc. are considered flow.

Rank the given paradigms from 1 to 10, with 1 being a very lay judge and 10 being a very flow judge. Only give a number and nothing else.
"""
PROG_PROMPT = """
You are a coach for high school debate. You want to classify judge paradigms based on whether the judge is "progressive" or "traditional". Progressive judges will entertain progressive arugments, such as kritiks (K's) and Theory shells and things like using music in the debate round.
If they do not have any restrictions on progressive arguments and are completely accepting, they should be rated a 5.
If they will vote for progressive arguments, but have a few stipulations, they should be rated a 4.
If they know what progressive arguments are and state they may vote on them, but it isn't their preference, they should be rated a 3.
If progressive argumentation isn't mentioned in their paradigm, they should be given a 2 if they seem to be technical otherwise (for example, they talk about flowing, being a former coach or debater).
If they have no technical experience, they should be given a 1.

Rank the given paradigms from 1 to 5, with 1 being a very traditional judge (not receptive to progressive arguments) and 10 being a very progressive judge. Only give a number and nothing else.
"""
EMAIL_PATTERN = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
URL_PATTERN = r'\b(?<!@)(?:https?://)?[a-zA-Z0-9-]+(?:\.[a-zA-Z]{2,})+\b'


class Paradigm(TypedDict):
    hash: str
    text: str
    html: str
    links: List[str]
    emails: List[str]
    scraped_at: str


def scrape_paradigm(tab_tourn_id: int, tab_judge_id: int) -> Paradigm | None:
    """Gets a judge's paradigm and includes link information.

    Args:
        tab_tourn_id (int): The unique ID assigned to the tournament, visible in the `tourn_id` query parameter.
        tab_judge_id (int): The unique ID assigned to the judge, visible in the `judge_id` query parameter.

    Returns:
        Paradigm: All data from the judge's paradigm.
    """

    soup = get_soup(
        f'https://www.tabroom.com/index/tourn/postings/judge.mhtml?tourn_id={tab_tourn_id}&judge_id={tab_judge_id}')

    paradigm_elem = soup.find('div', class_='paradigm ltborderbottom')
    if not paradigm_elem:
        return None

    paradigm: Paradigm = {
        'html': str(paradigm_elem),
        'text': paradigm_elem.get_text(),
        'links': [],
        'emails': [],
        'scraped_at': NOW
    }

    paradigm['hash'] = get_id([paradigm['text']])

    paradigm['emails'] = list(
        set(re.findall(EMAIL_PATTERN, str(paradigm_elem))))
    paradigm['links'] = list(set(re.findall(URL_PATTERN, str(paradigm_elem))))

    return paradigm


def check_paradigm_cache(hash: str) -> bool:
    paradigm = requests.get(f"{API_BASE}/paradigms/{hash}")
    return True if paradigm.status_code == 200 else False


def classify_paradigm(text: str) -> Tuple[int, int] | None:
    """Classifies a paradigm's flow and progressive rating.

    Args:
        text (str): The paradigm's text

    Returns:
        Tuple[int, int]: The first index is the flow rating, the second index is the progressive rating.
    """

    # Trim token length
    # text_splitter = CharacterTextSplitter.from_huggingface_tokenizer(
    #     GPT2TokenizerFast.from_pretrained("gpt2"), chunk_size=1000, chunk_overlap=0
    # )

    # text = text_splitter.split_text(text)[0]
    if len(text) > 4000:
        text = text[0:4000]

    # Create new chat instance
    chat = ChatOpenAI(
        model=FLOW_MODEL, api_key=os.environ['OPENAI_KEY'], max_retries=1
    )

    # Get classification
    response = chat([
        SystemMessage(content=FLOW_PROMPT),
        HumanMessage(content=f"Classify the following:\n\n{text}"),
    ])

    # Return result
    flow_result = None

    try:
        flow_result = int(response.content)
    except Exception:
        pass

    # Create new chat instance
    chat = ChatOpenAI(
        model=PROG_MODEL, api_key=os.environ['OPENAI_KEY'], max_retries=1
    )

    # Get classification
    response = chat([
        SystemMessage(content=PROG_PROMPT),
        HumanMessage(content=f"Classify the following:\n\n{text}")
    ])

    # Return result
    prog_result = None

    try:
        prog_result = int(response.content)
    except Exception:
        pass

    if not prog_result or not flow_result:
        return None
    else:
        return (flow_result, prog_result)
