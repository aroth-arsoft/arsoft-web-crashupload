ARG RELEASE=3-alpine
FROM python:$RELEASE as builder

RUN apk add --no-cache libxml2-dev libxslt-dev build-base python3-dev

RUN pip wheel lxml --wheel-dir /src

ARG RELEASE=3-alpine
FROM python:$RELEASE

LABEL maintainer="docker@fastprotect.net"

ENV container=docker LANG=C.UTF-8

RUN apk add --no-cache libxml2 libxslt

ADD ./app/ /app/
COPY --from=builder /src/*.whl /tmp
RUN pip install /tmp/*.whl && rm -rf /tmp/*.whl && \
    pip install -r /app/requirements.txt && \
    adduser -S -s /bin/sh app

VOLUME /app/static/ /app/templates/

EXPOSE 8000
CMD ["/bin/sh", "/app/entrypoint.sh"]
