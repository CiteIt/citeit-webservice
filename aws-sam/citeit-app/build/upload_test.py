# Copyright (C) 2015-2019 Tim Langeman and contributors
# <see AUTHORS.txt file>
#
# This library is part of the CiteIt project:
# http://www.citeit.net/

# The code for this server library is released under the MIT License:
# http://www.opensource.org/licenses/mit-license


import boto3
import settings

json_localfilename = '/Users/timlangeman/Documents/GitHub/CiteIt_Flask_API/aws-sam/citeit-app/build/test_upload.json'
file_key = 'test_upload_123.json'

s3 = boto3.resource('s3')
s3.meta.client.upload_file(
    json_localfilename,
    settings.AMAZON_S3_BUCKET,
    file_key,
    ExtraArgs={
        'ContentType': "application/json",
        'ACL': "public-read"
    }
)
