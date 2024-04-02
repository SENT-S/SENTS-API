# Use an official Python runtime as a parent image
FROM python:3.11-bookworm

# Set the working directory in the container to /app
WORKDIR /app

# Add the current directory contents into the container at /app
ADD . /app

# Copy .env file
COPY .env .env

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make port 5000 available to the world outside this container
EXPOSE 100

# Run Gunicorn server when the container launches
CMD ["gunicorn", "-w", "4", "wsgi:app"]
