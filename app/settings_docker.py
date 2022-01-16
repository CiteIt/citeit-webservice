import os

VERSION_NUM = os.getenv('VERSION_NUM', '0.4')  # used to version the sha256 hash filename

AMAZON_ACCESS_KEY = os.getenv('AMAZON_ACCESS_KEY', aws_settings.AMAZON_ACCESS_KEY)      # 'ABCDEFGH123456789'
AMAZON_SECRET_KEY = os.getenv('AMAZON_SECRET_KEY', aws_settings.AMAZON_SECRET_KEY)      # 'alksdfj;2452lkjr;ajtsaljgfslakjfgassgf'
AMAZON_S3_BUCKET = os.getenv('AMAZON_S3_BUCKET', aws_settings.AMAZON_S3_BUCKET)         # 'read.citeit.net'
AMAZON_S3_ENDPOINT = os.getenv('AMAZON_S3_ENDPOINT', aws_settings.AMAZON_S3_ENDPOINT)   # 's3.amazonaws.com'
AMAZON_REGION_NAME = os.getenv('AMAZON_REGION_NAME', aws_settings.AMAZON_REGION_NAME)   # 'us-east-1'


DATABASE_TYPE = os.getenv('DATABASE_TYPE', database_settings.DATABASE_TYPE)
DATABASE_SERVER = os.getenv('DATABASE_SERVER', database_settings.DATABASE_TYPE)
DATABASE_NAME = os.getenv('DATABASE_NAME', database_settings.DATABASE_NAME)
DATABASE_USER = os.getenv('DATABASE_USER', database_settings.DATABASE_USER)
DATABASE_PASSWORD = os.getenv('DATABASE_PASSWORD', database_settings.DATABASE_PASSWORD)
DATABASE_PORT = = os.getenv('DATABASE_PORT', database_settings.DATABASE_PORT)


TWITTER_CONSUMER_KEY = os.getenv('DATABASE_NAME', database_settings.TWITTER_CONSUMER_KEY)
TWITTER_CONSUMER_SECRET = os.getenv('DATABASE_USER', database_settings.TWITTER_CONSUMER_SECRET)
TWITTER_ACCESS_TOKEN = os.getenv('DATABASE_PASSWORD', database_settings.TWITTER_ACCESS_TOKEN)
TWITTER_ACCESS_TOKEN_SECRET = = os.getenv('DATABASE_PORT', database_settings.TWITTER_ACCESS_TOKEN_SECRET)




JSON_FILE_PATH = '/tmp/'   # in Lambda, you need to save to /tmp folder

# Construct Database Connection String from Docker
SQLALCHEMY_DATABASE_URI='{database_type}://{user}:{password}@{server}/{database}'.format(
    database_type = os.getenv('DATABASE_TYPE'),
    server = os.getenv('DATABASE_SERVER'),
    user = os.getenv('DATABASE_USER'),
    password = os.getenv('DATABASE_PASSWORD'),
    database = os.getenv('DATABASE_NAME')
    database = os.getenv('DATABASE_PORT')    
)

# Number of URL lookups to make simulaneously:
# pool = Pool(processes=settings.NUM_DOWNLOAD_PROCESSES)
NUM_DOWNLOAD_PROCESSES = 5

# Remove the following Unicode code points from Hash
URL_ESCAPE_CODE_POINTS = set ([
    10, 20, 160
])

# Remove the following Unicode code points from Hash
TEXT_ESCAPE_CODE_POINTS = set ( [
  2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 34, 39, 96, 133, 160, 173, 699, 700, 701, 702, 703, 712, 713, 714, 715, 716, 717, 718, 719, 732, 733, 750, 757, 5760, 6158, 8203, 8192, 8193, 8194, 8195, 8196, 8197, 8198, 8199, 8200, 8201, 8202, 8204, 8205, 8211, 8212, 8213, 8216, 8217, 8219, 8220, 8221, 8226, 8232, 8233,  8239, 8287, 8288, 12288, 65279
])

# Remove the followning characters from Hash
ESCAPE_SPECIAL_CHARS = [
    '\u00e2\u0080\u009d',   # "â"
    '\u00e2\u0080\u009c',   # LEFT DOUBLE QUOTATION MARK

    '\u00e2\u0080\u0093',
    '\u00e2\u0080\u00a6',
    '\u00e2\u0080\u0098',   # LEFT SINGLE QUOTATION
    '\u00e2\u0080\u0099',   # RIGHT SINGLE QUOTATION
]


