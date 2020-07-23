FROM python:3.8.3-alpine3.12
RUN apk add --no-cache gcc musl-dev libffi-dev openssl-dev

COPY app.py requirements.txt /opt/app/
COPY website /opt/app/website/
RUN addgroup --gid 1001 app &&\
    adduser --disabled-password --no-create-home --uid 1001 --ingroup app --shell /bin/bash app &&\
    chown app:app -R /opt/app/
    

COPY entrypoint.sh /opt/
RUN pip install --upgrade pip &&\
    pip install --upgrade -r /opt/app/requirements.txt &&\
    rm /opt/app/requirements.txt &&\
    chmod +x /opt/entrypoint.sh

WORKDIR /opt/app/
ENTRYPOINT ["/opt/entrypoint.sh"]
