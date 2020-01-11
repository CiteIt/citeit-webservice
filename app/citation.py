# Copyright (C) 2015-2020 Tim Langeman and contributors
# <see AUTHORS.txt file>
#
# This library is part of the CiteIt project:
# http://www.citeit.net/

# The code for this server library is released under the MIT License:
# http://www.opensource.org/licenses/mit-license

import json
import boto3
import settings
import os

__author__ = 'Tim Langeman'
__email__ = "timlangeman@gmail.com"
__copyright__ = "Copyright (C) 2015-2020 Tim Langeman"
__license__ = "MIT"
__version__ = "0.4"


class Citation:
    """ Filter list of citation data
        Save result locally in JSON format
        Upload JSON to Remote Storage (S3)
        Save Results to Database
    """

    def __init__(self, data):
        self.data = data

    def save(self, debug=False):
        self.json_save_local(debug)

    def save_all(self, debug=False):
        self.json_save_local(debug)
        self.json_upload(debug)
        self.db_save(debug)

    def db_save(self, debug=False):
        # Save Quote data to database, using SQLAlchemy
        if debug:
            print("Stub: saving to db ..")

    def file_key(self) :
        json_filename = ''.join([self.data['sha256'], '.json'])
        json_dir_path = os.path.join(settings.JSON_FILE_PATH, 'quote', 'sha256', settings.VERSION_NUM)
        shard = json_filename[:2]
        return ''.join(["quote/sha256/", settings.VERSION_NUM, "/", shard, "/", json_filename])

    def json_fields(self):
        # List of fields to be saved to json and uploaded to cloud
        return [
            'sha256',
            'citing_url', 'citing_quote',
            'citing_context_before', 'citing_context_after',
            'cited_url', 'cited_quote',
            'cited_context_before', 'cited_context_after',
        ]

    def json_data(self):
        # Save only specified fields to json
        output = {}
        for field in self.json_fields():
            data = self.data[field]
            # data = data.replace("u\'", "\'")  # Escape quotation backslash
            output[field] = data
        return output

    def json_file(self):
        return json.dumps(self.json_data(), outfile, indent=4, ensure_ascii=False)

    def json_filename(self):
        return ''.join([self.data['sha256'], '.json'])

    def json_localfilename(self):
        return ''.join([settings.JSON_FILE_PATH, self.json_filename()])

    def json_save_local(self, debug=False):
        # Save json file locally
        local_filename = ''.join([settings.JSON_FILE_PATH, self.json_filename()])
        with open(self.json_localfilename(), 'w', encoding='utf-8') as outfile:
            json.dump(self.json_data(), outfile)

        if debug:
            print("saving json locally")
            print(local_filename)

    def json_upload(self, debug=False):
        # Upload json file to cloud
        print("Saving JSON to Cloud ..")

        s3 = boto3.resource('s3')
        s3.meta.client.upload_file(
            self.json_localfilename(),
            settings.AMAZON_S3_BUCKET,
            self.file_key(),
            ExtraArgs={
                'ContentType': "application/json",
                'ACL': "public-read"
            }
        )
        if debug: # Output simple summary
            print(self.data['sha256'], ' ', self.data['citing_quote'])
