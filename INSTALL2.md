
## Setup:

### Flask Configure:
  * cd app/

  * cp settings-default.py settings.py
  (populate settings.py with own passwords)

##### Flask Run:
  * export FLASK_APP=app.py

  * set FLASK_RUN_PORT=80

  * python3 -m flask run --host=0.0.0.0 --port=80

### Docker:
  * docker build -t citeit_webservice:latest .

  * docker run -p 80:80 -e AMAZON_ACCESS_KEY=password -e AMAZON_SECRET_KEY=password citeit/citeit_webservice:latest