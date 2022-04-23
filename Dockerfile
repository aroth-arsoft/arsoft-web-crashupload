ARG RELEASE=3-alpine
# FROM python:$RELEASE as builder
#
# RUN apk add --no-cache libxml2-dev libxslt-dev build-base python3-dev
#
# RUN pip wheel lxml --wheel-dir /src
#FROM python:$RELEASE
FROM logiqx/python-lxml:3.9-alpine3.13 AS builder

ENV container=docker LANG=C.UTF-8

RUN apk add --no-cache mariadb-dev build-base

RUN pip wheel -w /wheels 'mysqlclient>=2.1.0'


FROM logiqx/python-lxml:3.9-alpine3.13

ENV container=docker LANG=C.UTF-8

LABEL maintainer="docker@fastprotect.net"

#RUN apk add --no-cache libxml2 libxslt
#RUN apk add --no-cache unixodbc mariadb-connector-odbc
RUN apk add --no-cache --repository=http://dl-cdn.alpinelinux.org/alpine/edge/testing mariadb-connector-odbc

# odbc-mariadb
COPY --from=builder /wheels/*.whl /tmp
RUN pip install /tmp/*.whl && rm -rf /tmp/*.whl && \
    adduser -S -s /bin/sh app

ADD ./app/requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt && \
    rm /tmp/requirements.txt

# add slighly modified patch from
# https://github.com/django/django/commit/0a4a5e5bacc354df3132d0fcf706839c21afb89d?diff=unified
# to fix https://code.djangoproject.com/ticket/32681
#   Exception while resolving variable 'subtitle' in template
ADD ./0a4a5e5bacc354df3132d0fcf706839c21afb89d.patch /tmp/0a4a5e5bacc354df3132d0fcf706839c21afb89d.patch
RUN apk add --no-cache patch && \
    cd /usr/local/lib/python3.9/site-packages && \
    patch -p1 -r /patch.rej -i /tmp/0a4a5e5bacc354df3132d0fcf706839c21afb89d.patch

ADD ./app/ /app/

EXPOSE 8000
CMD ["/bin/sh", "/app/entrypoint.sh"]
