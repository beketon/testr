ARG image-tag=latest
FROM ghcr.io/beketon/testactions-base:$image-tag

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update && apt-get --no-install-recommends install libreoffice -y && \
    apt-get install -y libreoffice-java-common \
    && apt-get clean

COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt