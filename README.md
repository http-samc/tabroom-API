# Tabroom API
This API is designed to scrape [tabroom](https://www.tabroom.com/index/index.mhtml) in order to curate
information about high school debate, specifically National Circuit Public Forum.

There is a corresponding frontend at [tournaments.tech](http://tournaments.tech)
where you can index through any competitors on the circuit and view our rankings.

The site and API were coded by [Samarth Chitgopekar](https://www.smrth.dev) and the
ranking methodology (the OTR Score) was created by Adithya Vaidyanathan.

We created this resource in order to, for once and for all, bring a clear and concise
dataset to high school debate. Though perfection is hard to reach with data on this scale,
we can confidently say we are the most accurate ranking/results site.

## Usage
The primary purpose of this repository is to provide the raw JSON datasets for people looking
to create their own projects, as our frontend [tournaments.tech](http://tournaments.tech) already
provides a clean way to access anything you'd need **non-programatically**. With the datasets,
found in `data/` (archives are provided as zipfiles in the `releases` tab by year), you can make your
own projects or conduct any research you'd need. If you don't like how we rank debaters, by all means
you can use our raw data to make your own! Submit a PR if its groundbreaking :)

If you'd like to scrape the data yourself (which we do **not** reccommend, since Tabroom's resources are limited),
you should keep in mind that Tabroom's site is highly unstandardized. That is, tournaments publish varying amounts
of data in varying formats. The utilities in `utils/` do a great job at covering this range, but you *will need to know some Python in order to debug*!
This is by no means a plug and play solution. This is why its reccommended for you to let us handle everything,
we even post the results within ~3 hrs. of the final places being announced!

In the event you're still interested in scraping yourself, keep the following in mind:
1. The full API documentation is in `DOCS.md`. There are comments on every pertinent function. You need to read these to be able to scrape yourself.
2. Start off by cloning the most recent version of the repo, making sure that the tournament you want is in `data/tournInfo.json`. If not, add it.
3. Run `main.py`. Most times you'll get an output in `data/tournaments/{tournament name}.json`, but any errors will be logged. From there, read the docs and debug.

If you need any help, feel free to message me at [sam@chitgopekar.tech](mailto:sam@chitgopekar.tech).