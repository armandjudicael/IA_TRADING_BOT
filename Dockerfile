# Use the official Python 3.12 base image
FROM python:3.12-bullseye

# Set the working directory inside the container
WORKDIR /app

# Copy requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy your Python scripts and configuration files into the container
COPY ATTACK_THE_MARKET.py .
COPY Report_Processor.py .
COPY config-test.ini .
COPY config-prod.ini .
COPY config-preprod.ini .
COPY config.ini .

# Run your Python script when the container starts
CMD ["python", "ATTACK_THE_MARKET.py"]
