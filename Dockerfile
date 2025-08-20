# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy your main Python script and any other necessary files
COPY requirements.txt .
COPY main.py .

# Define the entrypoint for the container. This will run your script.
ENTRYPOINT ["python", "/app/main.py"]