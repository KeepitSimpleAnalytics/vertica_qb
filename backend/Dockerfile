FROM python:3.10-slim

# Set the working directory to /code
WORKDIR /code

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy the entire 'app' directory into the container
COPY ./app /code/app