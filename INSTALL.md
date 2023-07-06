# Instructions on Installing the CiteIt Flask project

  * install python 3.x
  * http://docs.python-guide.org/en/latest/starting/installation/

  * The Pip package manager should be installed with Python
	From the command line:

  * You can use pip to install the required python libraries:
    * pip install vitualenv

  * https://docs.python.org/3/library/venv.html
  * Use a Virtual Environment to house all your libraries
    * python3 -m venv venv

  * Activate to Virtual Environment
    * source venv/bin/activate

  * You should see the command prompt change to something like:
    * (venv) Your Computer:your_username $

  * Install the requirements listed in the requirements text file
    * apt-get install python-dev
    * apt-get install -y poppler-utils
    * apt-get install build-essential libpoppler-cpp-dev pkg-config python-dev

    * pip install -r requirements.txt

    
### Flask Configure:

  * cd app/

  * cp settings-default.py settings.py
  (populate settings.py with own passwords)


### Flask Run

  * export FLASK_APP=app.py

  * set FLASK_RUN_PORT=80

  * python3 -m flask run --host=0.0.0.0 --port=80

### Docker Setup:

  * docker build -t citeit_webservice:latest .
  * docker build -t citeit_webservice:v0.4.15 .
  
  
  
### Docker Build & Run:

  * docker build -t citeit_webservice:v0.4.15 .  
  * docker tag 6e0a24bfae542c40387f0faa1b645c2d4190530714e681650b1f8094e388e4da citeit/citeit_webservice:v0.4.14
  

  * docker run -p 80:80 -e AMAZON_ACCESS_KEY=password -e AMAZON_SECRET_KEY=password -d citeit/citeit_webservice:v0.4.14


### Docker Push:

  * docker push citeit/citeit_webservice:v0.4.14
  * docker push citeit/citeit_webservice:latest


### Docker Pull
  * docker pull citeit/citeit_webservice:v0.4.14



#### Docker Detached:  -d

  * docker run -p 80:80 -e AMAZON_ACCESS_KEY=password -e AMAZON_SECRET_KEY=password -d citeit/citeit_webservice:v0.4.14
  * docker run -p 80:80 -e AMAZON_ACCESS_KEY=password -e AMAZON_SECRET_KEY=password -d citeit/citeit_webservice:latest
  
  * (Amazon keys are stored in Password Manager)