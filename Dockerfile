FROM python:3.7-slim-buster

# SET LABELS: DOCUMENTATIONS 
LABEL vendor="CiteIt.net"
LABEL maintainer="Tim Langeman <timlangeman@gmail.com>"
LABEL org.label-schema.name="CiteIt.net webservice"
LABEL org.label-schema.description="CiteIt.net web service generates contextual JSON for quotations"
LABEL org.label-schema.url="https://www.CiteIt.net/"
LABEL org.label-schema.vcs-url="https://github.com/CiteIt/citeit-webservice" 
LABEL org.opencontainers.image.licenses="MIT"
LABEL org.label-schema.docker.schema-version="0.5"
LABEL org.label-schema.docker.cmd="docker run -d -p 80:80 citeit_webservice" 

# LABEL BUILD DATE (AUTOMATICALLY)
ARG BUILD_DATE
LABEL org.label-schema.build_date=$BUILD_DATE

# INSTALL UPDATES & REQUIREMENTS 
RUN apt-get upgrade 
COPY requirements.txt .
RUN pip install -r requirements.txt

# COPY APP
COPY . /citeit 
WORKDIR /citeit/app
RUN chmod 755 /citeit/app

#SET ENVIRONMENTAL VARIABLES
ENV AMAZON_ACCESS_KEY 'secret_access_key'
ENV AMAZON_SECRET_KEY 'secret_key'
ENV AMAZON_S3_BUCKET 'read.citeit.net'
ENV AMAZON_S3_ENDPOINT 's3.amazonaws.com'
ENV AMAZON_REGION_NAME 'us-east-1'
ENV VERSION_NUM 0.3
ENV JSON_FILE_PATH '/citeit/json/quote/sha256/0.3/'
ENV FLASK_RUN_PORT 80
ENV FLASK_APP app.py
ENV PATH /citeit/app:$PATH

EXPOSE 80
ENTRYPOINT [ "python" ]
CMD ["app.py", "--host=0.0.0.0", "-p 80"]

