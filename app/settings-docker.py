import os

# AMAZON S3 Login information
AMAZON_ACCESS_KEY = os.getenv('AMAZON_ACCESS_KEY', '-1')
AMAZON_SECRET_KEY = os.getenv('AMAZON_SECRET_KEY', '-2') 
AMAZON_S3_BUCKET = os.getenv('AMAZON_S3_BUCKET', 'read.citeit.net')
AMAZON_S3_ENDPOINT = os.getenv('AMAZON_S3_ENDPOINT', 's3.amazonaws.com')
AMAZON_REGION_NAME = os.getenv('AMAZON_REGION_NAME', 'us-east-1')

VERSION_NUM = os.getenv('VERSION_NUM', 0.3)  # used to version the sha256 hash filename

JSON_FILE_PATH = os.getenv('JSON_FILE_PATH', '/home/citeit/json/')
SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI', 'postgresql://username:password@localhost/databasename') 

