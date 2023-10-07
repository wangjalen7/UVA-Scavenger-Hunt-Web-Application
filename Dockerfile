# Use an official Python runtime as the base image
FROM python:3.9-slim

# Set environment variables
ENV PYTHONUNBUFFERED 1

# Create and set the working directory
WORKDIR /app

# Copy the current directory (your Django app) into the container at /app
ADD . /app/

# Install any needed packages specified in requirements.txt
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Specify the command to run on container start
CMD ["gunicorn", "ScavengerHuntApp.wsgi:application", "--bind", "0.0.0.0:8000"]
