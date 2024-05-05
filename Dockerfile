# Use Python 3.12 as the parent image
FROM python:3.12

# Set the working directory in the container to /app
WORKDIR /app

# Add the current directory contents into the container at /app
ADD src/ /app
ADD requirements.txt /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Set environment variables
ENV POSTGRES_DB=dbname
ENV POSTGRES_USR=dbusr
ENV POSTGRES_PASS=dbpass
ENV POSTGRES_HOST=dbhost
ENV POSTGRES_PORT=dbport

# Run monitor_service.py when the container launches
CMD ["python", "main.py"]