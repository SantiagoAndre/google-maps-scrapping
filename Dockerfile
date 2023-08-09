FROM selenium/standalone-chrome:latest
WORKDIR /src
COPY requirements.txt /src/requirements.txt
# Install pip
# Install pip & required dependencies
USER root
# Install pip, required dependencies, and python3-distutils
RUN apt-get update \
    && apt-get install -y curl python3-distutils \
    && curl https://bootstrap.pypa.io/get-pip.py | python3 \
    && pip3 install --no-cache-dir -r requirements.txt

# RUN /usr/local/bin/pip3 install --upgrade pip
# RUN /usr/local/bin/pip3 install --no-cache-dir -r /src/requirements.txt
# COPY . /src/

# RUN apt-get update && apt-get install -y xvfb


# # Set display port and dbus for Xvfb
# ENV DISPLAY=:99
# ENV DBUS_SESSION_BUS_ADDRESS=/dev/null

