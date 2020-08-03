import boto3
import settings
import requests
import gzip
import os

from langdetect import detect


def fix_encoding(str):
    # If certain characters are found in the input, switch encoding
    output = str
    if ('â€™' in str) or ('â€' in str) or ('â€œ' in str):
        output = str.encode("Windows-1252").force_encoding("UTF-8")

    return output

def publish_file(url, text, local_path, remote_path, content_type, compression='gzip'):
    string_input = text
    local_path_input = local_path

    if compression:
        local_path_input = local_path + '.gz'
        string_input = gzip.compress(bytes(text, 'utf-8'))
        filetype = 'wb'
        # To decompress: string_input = gzip.decompress(string_input)

    save_file_locally(local_path_input, string_input, filetype)
    save_file_to_cloud(local_path_input, remote_path, content_type, compression)
    archive_url(url)

def save_file_locally(local_path, text_input, filetype='w'):
    # Create Local Directory if it doesn't exist
    dirname = os.path.dirname(local_path)
    if not os.path.exists(dirname):
        os.makedirs(dirname)

    # Save file locally
    with open(local_path, filetype) as the_file:
        the_file.write(text_input)

    print("**** Saved locally: " + local_path + " ******")

def save_file_to_cloud(local_path, remote_path, content_type, compression='gzip'):

    remote_path = remote_path.replace('https://', '')
    remote_path = remote_path.replace('http://', '')

    # Upload JSON to Amazon S3
    session = boto3.Session(
        aws_access_key_id=settings.AMAZON_ACCESS_KEY,
        aws_secret_access_key=settings.AMAZON_SECRET_KEY
    )

    s3 = session.resource('s3')
    s3.meta.client.upload_file(
        Filename=local_path,
        Bucket=settings.AMAZON_S3_BUCKET,
        Key=remote_path,
        ExtraArgs={'ContentType': content_type, 'ContentEncoding': compression, 'ACL': "public-read"},
    )

    print("------Publishing to Cloud: " + remote_path + "-----")

def archive_url(url):
    # submit url to archive.org
    if len(url) > 0:
        add_archive_job_to_queue(url)


def add_archive_job_to_queue(url):
    # r = requests.get('https://web.archive.org/save/?url='+ url)
    # r = requests.post('https://web.archive.org/save', data={'url': url})
    print("submit archive request to job queue")


def get_from_cache(filename):

    # Default return dict
    content_dict = {
       'text': '',      # unicode
       'unicode':  '',
       'content':  '',  # raw
       'encoding': '',
       'error': '',
       'language': '',
       'content_type': ''
    }

    # Get the Gzip version of the file
    filename, file_extension = os.path.splitext(filename)
    if (file_extension != '.gz'):
        filename = filename + '.gz'

    # Does a Parent Directory Exist for file Cache?
    dirname = os.path.dirname(filename)
    if not os.path.exists(dirname):
        os.makedirs(dirname)

    # Was this File already downloaded?  If so, return from cache.
    if os.path.exists(filename):
        with open(filename, 'r') as content_file:
            file_content = filename.read()

            # Unzip file contents:
            file_content = gzip.decompress(file_content)

            # Detect Encoding
            blob = open(file_content, 'rb').read()
            m = magic.open(magic.MAGIC_MIME_ENCODING)
            m.load()
            encoding = m.buffer(blob)

            # Get Language
            language = detect(file_content)

            # Get Content Type
            mime = magic.Magic(mime=True)
            content_type = mime.from_file(file_content)  # 'application/pdf'

            content_dict = {
                'text': file_content,        # unicode
                'unicode': file_content,
                'content': file_content,     # raw
                'encoding': encoding,
                'error':  '',
                'language': language,
                'content_type': content_type
            }

    return content_dict