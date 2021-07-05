FROM alpine:3.12

ARG ansible_version

RUN apk add --no-cache \
    bash \
    python3 py3-pip

RUN apk add --no-cache \
    gcc libressl-dev musl-dev libffi-dev libxslt-dev make musl-dev openssl-dev python3-dev

RUN apk add --no-cache py-cryptography

RUN pip3 install --upgrade pip && \
    pip3 --no-cache-dir install \
    ansible==${ansible_version}

RUN apk --no-cache add g++

RUN pip3 --no-cache-dir install \
    opentelemetry-api \
    opentelemetry-sdk \
    opentelemetry-exporter-jaeger

COPY . /demo/

WORKDIR /demo
