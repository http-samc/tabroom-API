# Official Python image
FROM python:3.11.4-slim

# Set the working directory in the container
WORKDIR /usr/src/app

# Install the Infisical CLI
# RUN apt-get update && apt-get install -y bash curl && curl -1sLf \
# 'https://dl.cloudsmith.io/public/infisical/infisical-cli/setup.deb.sh' | bash \
# && apt-get update && apt-get install -y infisical

# Copy the current directory contents into container
COPY . .

# Arguments
ARG CLERK_KEY
ARG ENVIRONMENT
ARG MEILISEARCH_KEY
ARG MEILISEARCH_URL
ARG OPENAI_KEY
ARG REDIS_URL

# Environment Variables
ENV CLERK_KEY=${CLERK_KEY}
ENV ENVIRONMENT=${ENVIRONMENT}
ENV MEILISEARCH_KEY=${MEILISEARCH_KEY}
ENV MEILISEARCH_URL=${MEILISEARCH_URL}
ENV OPENAI_KEY=${OPENAI_KEY}
ENV REDIS_URL=${REDIS_URL}

# Install from requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Start the program
ENTRYPOINT [ "python", "main.py" ]
# ENTRYPOINT ["infisical", "run", "--env", "prod", "--projectId", "68c1acf7-5d47-425c-b608-46840bec9def", "--", "python", "main.py"]
