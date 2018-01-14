# Copyright (C) 2015-2018 Tim Langeman and contributors
# <see AUTHORS.txt file>
#
# This library is part of the CiteIt project:
# http://www.citeit.net/

# The code for this server library is released under the MIT License:
# http://www.opensource.org/licenses/mit-license

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

from models import Quote
from sqlalchemy import update
import settings
import json

from settings import AMAZON_ACCESS_KEY, AMAZON_SECRET_KEY, AMAZON_S3_BUCKET, AMAZON_S3_ENDPOINT
from settings import JSON_FILE_PATH, VERSION_NUM

__author__ = 'Tim Langeman'
__email__ = "timlangeman@gmail.com"
__copyright__ = "Copyright (C) 2015-2018 Tim Langeman"
__license__ = "MIT"
__version__ = "0.3"


class Citation:
    """ Find the canonical url within an html document
        Return it if it exists,
        if it does not, return the supplied URL

    """

    def __init__(self, data):
        self.data = data

    def save(self):
        """
            Save data to: database, local json file, upload json to cloud
        """
        # self.db_save()
        # self.json_save()
        # self.json_upload()
        return 1

    def db_save(self):
        """
            Save Quote data to database, using SQLAlchemy
        """
        print("saving to db ..")

        """
        engine = create_engine(settings.SQLALCHEMY_DATABASE_URI)
        Session = sessionmaker(bind=engine)
        q = Quote(**self.data)
        session = Session()

        # Check if record already exists:
        if not session.query(Quote).filter(Quote.sha256 == self.data['sha256']).count():
            session.add(q)
        else:
            update(Quote).where(Quote.sha256 == self.data['sha256']).values(**self.data)
        session.commit()
        """

    def json_fields(self):
        """
            List of fields to be saved to json and uploaded to cloud
        """
        return [
                'sha256',
                'citing_url', 'citing_quote',
                'citing_context_before', 'citing_context_before',
                'cited_url', 'cited_quote',
                'cited_context_before', 'cited_context_before'
        ]

    def json_data(self):
        """
            Save only specified fields to json
        """
        output = {}
        for field in self.json_fields():
            output[field] = self.data[field]
        return output

    def json_save(self):
        """
            Save json file locally
        """
        print("saving json locally")
        filename = ''.join([self.data['sha256'], '.json'])
        local_filename = ''.join([JSON_FILE_PATH, filename])

        with open(local_filename, 'w') as outfile:
            json.dump(self.json_data(), outfile, indent=4, ensure_ascii=False)

    def json_upload(self):
        """
            Upload json file to cloud
        """
        print("uploading json to cloud")
        return 1