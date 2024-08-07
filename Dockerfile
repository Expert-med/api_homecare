# Use the official Python image as the base image
FROM python:3.11.3

# Install any system dependencies
RUN apt-get update \
    && apt-get install -y libgl1-mesa-glx \
                          qt5-qmake \
                          qtbase5-dev \
                          qtbase5-dev-tools


# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file into the container at /app
COPY requirements.txt /app/

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . /app/

# Expose any ports your application needs to listen on (if applicable)
EXPOSE 8083

# Define the container startup command to execute entrypoint.sh script
# Set memory limit to 512MB for the container's main process
CMD ["python", "app.py"]