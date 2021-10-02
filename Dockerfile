FROM python:3.6
LABEL vendor="CiteIt.net"
LABEL maintainer="Tim Langeman <timlangeman@gmail.com>"
LABEL org.label-schema.name="CiteIt.net webservice"
LABEL org.label-schema.description="CiteIt.net web service generates contextual JSON for quotations"
LABEL org.label-schema.url="https://www.CiteIt.net/"
LABEL org.label-schema.vcs-url="https://github.com/CiteIt/citeit-webservice" 
LABEL org.opencontainers.image.licenses="MIT"
LABEL org.label-schema.docker.schema-version="0.4.1"
LABEL org.label-schema.docker.cmd="docker run -d -p 80:80 citeit_webservice" 

ARG BUILD_DATE
LABEL org.label-schema.build_date=$BUILD_DATE

COPY . app
COPY app/settings_docker.py app/settings.py
WORKDIR app
RUN pip3 install -r requirements.txt


ENV AMAZON_ACCESS_KEY 'secret_access_key'
ENV AMAZON_SECRET_KEY 'secret_key'
ENV AMAZON_S3_BUCKET 'read.citeit.net'
ENV AMAZON_S3_ENDPOINT 's3.amazonaws.com'
ENV AMAZON_REGION_NAME 'us-east-1'
ENV VERSION_NUM '0.4'
ENV JSON_FILE_PATH '/var/www/citeit-webservice/json/'
ENV FLASK_APP app/app.py
ENV FLASK_RUN_PORT 80
ENV FLASK_RUN_PORT 443
EXPOSE 80 443
ENTRYPOINT ["python"]
CMD ["app/app.py"]
