# Official Python image
FROM python:3.11.4-slim

# Set the working directory in the container
WORKDIR /usr/src/app

# Install the Infisical CLI
RUN apt-get update && apt-get install -y bash curl && curl -1sLf \
'https://dl.cloudsmith.io/public/infisical/infisical-cli/setup.deb.sh' | bash \
&& apt-get update && apt-get install -y infisical

# Copy the current directory contents into container
COPY . .

# Install from requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Start the program
ENTRYPOINT ["infisical", "run", "--projectId", "68c1acf7-5d47-425c-b608-46840bec9def", "--", "python", "main.py"]
