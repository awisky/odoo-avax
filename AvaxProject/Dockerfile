FROM odoo:14
MAINTAINER Agustin Wisky. <agustinwisky@gmail.com>

USER root

# Update aptitude with new repo
RUN apt-get clean

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        apt-utils \
        python3 \
        python3-dev \
        python3-wheel \
        chromium \
        git \
        wget

#Build Solidity compiler from source
RUN apt install -y build-essential cmake

RUN wget https://github.com/ethereum/solidity/releases/download/v0.8.4/solidity_0.8.4.tar.gz

RUN tar xvzf solidity_0.8.4.tar.gz && mv solidity_0.8.4 solidity

RUN apt-get update && \
      apt-get -y install sudo

RUN useradd -m docker && echo "docker:docker" | chpasswd && adduser docker sudo

RUN solidity/scripts/install_deps.sh
RUN solidity/scripts/build.sh

# Install Python3 and all the requirements.txt
COPY ./requirements.txt ./

RUN python3 -m pip install -r ./requirements.txt

RUN chown -R odoo /mnt/*
# Set default user when running the container
USER odoo