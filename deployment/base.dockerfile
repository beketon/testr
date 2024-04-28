FROM python:3.11.9-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update && apt-get --no-install-recommends install libreoffice -y && \
    apt-get install -y libreoffice-java-common 
#    && apt-get clean
