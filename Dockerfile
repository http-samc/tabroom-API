# Official Python image
FROM python:3.11.4-slim

# Set the working directory in the container
WORKDIR /usr/src/app

# Set environment variables (not currently used by scraper, but good for future reference)
ENV API_URL="Your_API_URL_here"
ENV OPENAI_KEY="Your_OPENAI_KEY_here"

# Copy the current directory contents into container
COPY . .

# Install from requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Start the program
ENTRYPOINT ["python", "main.py"]
