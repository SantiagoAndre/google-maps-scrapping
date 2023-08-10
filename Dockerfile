# Use selenium with chrome as base image
FROM selenium/standalone-chrome:latest

# Set working directory
WORKDIR /src

# Copy requirements
COPY requirements.txt /src/requirements.txt

# Switch to root to install dependencies
USER root

# Update, install system dependencies, get pip, and install python libraries
RUN apt-get update && \
    apt-get install -y \
    pkg-config \
    libcairo2-dev \
    curl \
    python3-distutils \
    build-essential \
    python3.8-dev && \
    curl https://bootstrap.pypa.io/get-pip.py | python3 && \
    pip3 install --no-cache-dir -r requirements.txt

# Clean up APT when done
RUN apt-get clean && rm -rf /var/lib/apt/lists/* 
