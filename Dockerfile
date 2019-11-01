FROM python:3.6
LABEL maintainer="timlangeman@gmail.com"
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
EXPOSE 80
ENTRYPOINT ["python"]
CMD ["app/app.py"]
