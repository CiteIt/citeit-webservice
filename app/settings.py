import os
import logging


logging.basicConfig(filename="citeit-webservice.log", 
                    format='%(asctime)s %(message)s', 
                    filemode='w') 

logger=logging.getLogger() 
logger.setLevel(logging.DEBUG) 


# Webservice is versioned in JSON URL
# example: https://read.citeit.net/quote/sha256/0.4/d5/d588c1c9c4acfcd254acc4033b7888e98f21e426214b21f0e07673664e328e39.json

VERSION_NUM = os.getenv('VERSION_NUM', '0.4')  


#############################################################################################################################
# Certain Unicode characters can cause problems with the hash
# Remove the following Unicode code points from Hash

URL_ESCAPE_CODE_POINTS = set ([
    10, 20, 160
])

# Remove the following Unicode code points from Hash
TEXT_ESCAPE_CODE_POINTS = set ( [
    2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18
    , 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 39
    , 96, 160, 173, 699, 700, 701, 702, 703, 712, 713, 714, 715, 716
    , 717, 718, 719, 732, 733, 750, 757, 8211, 8212, 8213, 8216, 8217
    , 8219, 8220, 8221, 8226, 8203, 8204, 8205, 65279, 8232, 8233, 133
    , 5760, 6158, 8192, 8193, 8194, 8195, 8196, 8197, 8198, 8199, 8200
    , 8201, 8202, 8239, 8287, 8288, 12288
])

JSON_FILE_PATH = '/tmp/'   # in Lambda, you need to save to /tmp folder
SQLALCHEMY_DATABASE_URI = 'postgresql://username:password@localhost/database_name'

SAVE_DOWNLOADS_TO_FILE = False

#######################################################################################
# Set number of Quote lookups to make simulaneously from a given URL:
# Usage in: app/lib/citeit_quote_context/url.py
# pool = Pool(processes=settings.NUM_DOWNLOAD_PROCESSES)

NUM_DOWNLOAD_PROCESSES = 5

############################## Get default AWS Settings from file ##############################################################
# this settings file doesn't exist unless you create it by copying from aws_settings_default.py

try:
    import aws_settings # used when app is run directly from python
except ImportError:
    logger.debug('aws_settings failed to import', exc_info=True)

############################################################################################################################### 
# Get Amazon Settings from Docker Input, Default to AWS File Input, if it exist 
#
# Docker params are passed in at the command-line : 
#   docker run -p 80:80 
#		-e AMAZON_ACCESS_KEY= ************** 
#		-e AMAZON_SECRET_KEY= ************** 
#		citeit/citeit_webservice:latest


AMAZON_ACCESS_KEY = os.getenv('AMAZON_ACCESS_KEY', '')      # 'ABCDEFGH123456789'
AMAZON_SECRET_KEY = os.getenv('AMAZON_SECRET_KEY', '')      # 'alksdfj;2452lkjr;ajtsaljgfslakjfgassgf'
AMAZON_S3_BUCKET = os.getenv('AMAZON_S3_BUCKET', '')         # 'read.citeit.net'
AMAZON_S3_ENDPOINT = os.getenv('AMAZON_S3_ENDPOINT', '')   # 's3.amazonaws.com'
AMAZON_REGION_NAME = os.getenv('AMAZON_REGION_NAME', '')   # 'us-east-1'