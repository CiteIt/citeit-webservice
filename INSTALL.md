Instructions on Installing the CiteIt Flask project
====================================================

  * install python 3.x
  * http://docs.python-guide.org/en/latest/starting/installation/

  * The Pip package manager should be installed with Python
From the command line:

  * You can use pip to install the required python libraries:
    * pip install vitualenv

  * http://docs.python-guide.org/en/latest/dev/virtualenvs/
  * Use a Virtual Environment to house all your libraries
    * virtualenv venv

  * Activate to Virtual Environment
    * source venv/bin/activate

  * You should see the command prompt change to something like:
    * (venv) Your Computer:your_username $

  * Install the requirements listed in the requirements text file
    * pip install -r requirements.txt
    * pip install 'requests[security]'


Flask Local Setup
=====================

  export FLASK_APP=app
  flask run


Amazon Lambda Deployment:
====================================================

Documentation: https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-quick-start.html


cd aws-sam

sam build --use-container

cd sam-app

sam local start-api

sam package \
    --output-template-file packaged.yaml \
    --s3-bucket REPLACE_THIS_WITH_YOUR_S3_BUCKET_NAME


sam deploy \
    --template-file packaged.yaml \
    --stack-name sam-app \
    --capabilities CAPABILITY_IAM



Optional Tools:
==================
If you don't already have your own tool preferences, here's a few ideas
to get you started:

Github's Atom Editor
https://atom.io/

Desktop Git Client
https://desktop.github.com/
