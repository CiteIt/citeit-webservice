# Copyright (C) 2015-2020 Tim Langeman and contributors
# <see AUTHORS.txt file>
#
# This library is part of the CiteIt project:
# http://www.citeit.net/

# The code for this server library is released under the MIT License:
# http://www.opensource.org/licenses/mit-license

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from sqlalchemy import create_engine, MetaData, Table, \
    Integer, BigInteger, LargeBinary, UnicodeText, String, Column, DateTime, \
    PrimaryKeyConstraint, UniqueConstraint, Sequence, Index, ForeignKey, Boolean

from sqlalchemy_utils import EmailType, CountryType, ChoiceType, \
    IPAddressType, PasswordType, URLType, PhoneNumberType, TimezoneType

from sqlalchemy.ext.declarative import declarative_base

from datetime import datetime
import settings

import pymysql
pymysql.install_as_MySQLdb

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = settings.SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


Base = declarative_base()


class Citation(Base):
    __tablename__ = 'citation'

    id = Column(BigInteger(), primary_key=True)
    request_id = Column(BigInteger(), ForeignKey('request.id'), index=True, nullable=False)
    sha256 = Column(String(64), nullable=False, index=True, unique=True)

    citing_url = Column(URLType, index=True, nullable=False)
    citing_url_canonical = Column(URLType, index=True, nullable=False)
    citing_quote = Column(UnicodeText(), index=True, nullable=False)
    citing_context_before = Column(UnicodeText)
    citing_context_after = Column(UnicodeText)

    cited_url = Column(URLType, nullable=False)
    cited_quote = Column(UnicodeText(), nullable=True)
    cited_context_before = Column(UnicodeText(), nullable=True)
    cited_context_after = Column(UnicodeText(), nullable=True)
    created = Column(
        DateTime(timezone=True),
        index=True,
        default=datetime.utcnow,
        nullable=False
    )

    __table_args__ = (
        PrimaryKeyConstraint('id', name='citation_pk'),
        UniqueConstraint('sha256', name='citation_sha256_unique'),
        Index('document_request_id_index', 'request_id'),
        Index('document_citing_url_index', 'citing_url'),
        Index('document_citing_url_canonical_index', 'citing_url_canonical'),
        Index('document_cited_url_index', 'cited_url'),
        Index('document_created_index', 'created')
    )

    def __repr__(self):
        return "<Citation(id='%s', citing_quote='%s', citing_url='%s')>" % (
            self.id,
            self.citing_quote,
            self.citing_url
        )


class Document(Base):
    __tablename__ = 'document'

    id = Column(BigInteger(), primary_key=True)
    current_record = Column(Boolean, nullable=False)
    request_id = Column(BigInteger(), ForeignKey('request.id'), index=True, nullable=False)
    domain_id = Column(BigInteger(), index=True, nullable=False)
    url = Column(URLType, index=True, nullable=False)
    content_type = Column(String(50), nullable=False)
    title = Column(String(256), nullable=True)
    body_binary = Column(LargeBinary, nullable=True)
    body_html = Column(UnicodeText, nullable=True)
    body_text = Column(UnicodeText, default='')
    encoding = Column(String(16), nullable=False)
    word_count = Column(Integer, nullable=False)
    character_count = Column(Integer, nullable=False)
    created = Column(
        DateTime(timezone=True),
        index=True,
        default=datetime.utcnow,
        nullable=False
    )
    updated = Column(
        DateTime(timezone=True),
        nullable=False,
        onupdate=datetime.utcnow
    )

    __table_args__ = (
        PrimaryKeyConstraint('id', name='document_pk'),
        Index('document_request_id_index', 'request_id'),
        Index('document_domain_id_index', 'domain_id'),
        Index('document_url_index', 'created')
        #info('mysql_partition': """
        #    PARTITION BY LIST COLUMNS(current_record)(
        #            PARTITION current VALUES IN(True),
        #            PARTITION past VALUES IN(False)
        #    )
        #""")
    )

    def __repr__(self):
        return "<Document (id='%s', title='%s', url='%s',  >" % (
            self.id,
            self.title,
            self.url,
        )


class Tag(Base):
    __tablename__ = 'tag'

    id = Column(BigInteger(), primary_key=True)
    tag = Column(String(100), unique=True, nullable=False)
    parent_id = Column(BigInteger(), ForeignKey('tag.id'), nullable=False)
    created = Column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False
    )

    __table_args__ = (
        PrimaryKeyConstraint('id', name='tag_pk'),
        UniqueConstraint('tag',name='unique_citation_tag'),
        Index('tag_parent_id_index' 'tag', 'parent_id'),
        Index('tag_created_index' 'created')
    )

    def __repr__(self):
        return "<Tag(id='%s', tag='%s')>" % (
            self.id,
            self.tag
        )

class CitationTag(Base):
    __tablename__ = 'citation_tag'

    citation_id = Column(BigInteger(), ForeignKey('citation.id'), nullable=False)
    tag_id = Column(BigInteger(), ForeignKey('tag.id'), nullable=False)

    __table_args__ = (
        PrimaryKeyConstraint('citation_id', 'tag_id', name='citation_tag_pk'),
        Index('citation_tag_citation_id', 'citation_id', 'citation_id'),
        Index('citation_tag_tag_id', 'tag_id')
    )

    def __repr__(self):
        return "<Tag(citation_id='%s', tag='%s')>" % (
            self.citation_id,
            self.tag_id,
        )


class Request(Base):
    REQUEST_TYPES = [
        (u'post-url', u'Post URL'),                                 # url
        (u'posts-cited-by', u'Get Posts Cited by this URL/Domain'), # url, start_date, end_date, (default to latest), citation_terms, context_terms, tags, document_terms, search_type, max_results
        (u'posts-citing', u'Get Posts that Cite this URL'),         # url, start_date, end_date, (default to latest), citation_terms, context_terms, tags, document_terms, search_type, max_results
        (u'archives-of-url', u'Get Archive of URL'),                # url, start_date, end_date, max_results
    ]
    SEARCH_TYPES = [
        (u'url', u'URL'),
        (u'domain', u'Domain (Strict)'),
        (u'domain-subdomains', u'Domain (Subdomains)')
    ]

    __tablename__ = 'request'

    id = Column(BigInteger(), Sequence('request_id_seq'))
    ip_address = Column(IPAddressType, index=True, nullable=False)
    request_type = Column(ChoiceType(REQUEST_TYPES))
    url = Column(URLType, index=True, nullable=False)
    user_agent = Column(String(8000), nullable=False)
    created = Column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False
    )

    __table_args__ = (
        PrimaryKeyConstraint('id', name='request_pk'),
        Index('request_ip_address_index', 'ip_address'),
        Index('request_created_index', 'created'),
        Index('request_url_index', 'url')
    )

    def __repr__(self):
        return "<Request(id='%s', url='%s')>" % (
            self.id,
            self.url
        )


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)     # Sequence('user_id_seq')
    email = Column(EmailType, nullable=False)
    first_name = Column(String(25), nullable=True)
    last_name = Column(String(35), nullable=True)
    fullname = Column(String(75), nullable=True)
    #phone = Column(PhoneNumberType, nullable=True)
    twitter = Column(String(35), nullable=True)
    country = Column(CountryType, nullable=True)
    timezone = Column(TimezoneType(backend='pytz'))
    password = Column(PasswordType(
        schemes=[
            'pbkdf2_sha512',
            'md5_crypt'
        ],

        deprecated=['md5_crypt']
    ))
    created = Column(DateTime(), default=datetime.now, nullable=False)
    updated_on = Column(DateTime(), default=datetime.now, nullable=False, onupdate=datetime.now)

    __table_args__ = (
        PrimaryKeyConstraint('id', name='user_pk'),
        UniqueConstraint('email', name='user_email_unique')
    )

    def __repr__(self):
        return "<User(email='%s', fullname='%s' )>" % (
            self.email,
            self.fullname
        )



"""

from sqlalchemy import event

# standard decorator style
@event.listens_for(Document, 'before_insert')
def receive_before_insert(mapper, connection, target):
    "listen for the 'before_insert' event"

    # ... (event handling logic) ...
    
    update document
      set current_record = False
    where url = url and current_record = True



admin = User('admin@example.com','test-pasw**d')

db.create_all() # In case user table doesn't exists already. Else remove it.

db.session.add(admin)

db.session.commit() # This is needed to write the changes to database

User.query.all()

User.query.filter_by(username='admin').first()
"""
