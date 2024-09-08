#name of image from Dockerhub. Alpine is lightweight version of linux
FROM python:3.9-alpine3.13

#Define maintainer
LABEL maintainer="shaileshmamgain"

# we don't wanna buffer output for python
ENV PYTHONUNBUFFERED 1

# compy req from local to docker image
COPY ./requirements.txt /tmp/requirements.txt
COPY ./requirements.dev.txt /tmp/requirements.dev.txt
COPY ./app /app
#make app working dir
WORKDIR /app
#access port
EXPOSE 8000


#python run command and create new linux user (defaults to root user)
ARG DEV=false
RUN python -m venv /py && \
    /py/bin/pip install --upgrade pip && \
    apk add --update --no-cache postgresql-client jpeg-dev && \
    apk add --update --no-cache --virtual .tmp-build-deps \
        build-base postgresql-dev musl-dev zlib zlib-dev && \
    /py/bin/pip install -r /tmp/requirements.txt && \
    if [ $DEV = "true" ]; \
        then /py/bin/pip install -r /tmp/requirements.dev.txt ; \
    fi && \
    rm -rf /tmp && \
    apk del .tmp-build-deps && \
    adduser \
        --disabled-password \
        --no-create-home \
        django-user && \
        mkdir -p /vol/web/media && \
        mkdir -p /vol/web/static && \
        chown -R django-user:django-user /vol && \
        chmod -R 755 /vol

#add bin to path
ENV PATH="/py/bin:$PATH"

#at this point we switch to django user from root user
USER django-user