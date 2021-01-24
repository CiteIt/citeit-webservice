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
    PrimaryKeyConstraint, UniqueConstraint, Sequence, Index, ForeignKey, \
    Numeric, Boolean, null, orm, Unicode, func

from sqlalchemy_utils import EmailType, CountryType, ChoiceType, \
    IPAddressType, PasswordType, PhoneNumberType, TimezoneType, URLType, \
    PhoneNumber        

from datetime import datetime

import datetime
import hashlib
import settings
import pymysql
pymysql.install_as_MySQLdb

from sqlalchemy.ext.declarative import declarative_base


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = settings.SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

engine = create_engine(settings.SQLALCHEMY_DATABASE_URI)

Base = declarative_base()

class User(Base):
    __tablename__ = 'user'

    id = Column(BigInteger(), primary_key=True)
    email = Column(EmailType, nullable=False)
    first_name = Column(String(25), nullable=True)
    last_name = Column(String(35), nullable=True)
    fullname = Column(String(75), nullable=True)
    twitter = Column(String(35), nullable=True)
    country = Column(CountryType, nullable=True)
    _phone = Column(Unicode(20), nullable=True)
    timezone = Column(TimezoneType(backend='pytz'))
    password = Column(PasswordType(
        schemes=[
            'pbkdf2_sha512',
            'md5_crypt'
        ],
    
        deprecated=['md5_crypt']
    ))
    create_date = Column(DateTime(), default=datetime.datetime.now, nullable=False)
    update_date = Column(DateTime(), default=datetime.datetime.now, nullable=False, onupdate=datetime.datetime.now)

    phone = orm.composite(
        PhoneNumber,
        _phone,
        country, 
        nullable=True
    )

    __table_args__ = (
        PrimaryKeyConstraint('id', name='user_pk'),
        Index('user_email_unique', (email) , unique=True),        
    )

    def __repr__(self):
        return "<User(name='%s', fullname='%s', email='%s')>" % (
            self.name,
            self.fullname,
            self.email
        )

class Request(Base):
    __tablename__ = 'request'

    REQUEST_TYPES = [
        (u'post_url' , u'Post URL'),
        (u'post_demo' , u'Post Demo'),                                    # post_url, post_body
        (u'get_posts_cited_by' , u'Get Posts Cited by this URL/Domain'),  # url, start_date, end_date, (default to latest), citation_terms, context_terms, tags, document_terms, search_type, max_results
        (u'get_posts_citing' , u"Get Posts that Cite this URL"),          # url, start_date, end_date, (default to latest), citation_terms, context_terms, tags, document_terms, search_type, max_results
        (u'get_archives_of_url' , 'Get Archive of URL'),                  # url, start_date, end_date, max_results 
    ]
    SEARCH_TYPES = [
        (u'url' , u'URL'),
        (u'domain' , u'Domain (Strict)'),
        (u'domain_subdomains' , u'Domain (Subdomains)')
    ]

    id = Column(BigInteger(), primary_key=True)
    ip_address = Column(IPAddressType)
    request_type = Column(ChoiceType(REQUEST_TYPES))
    request_url = Column(URLType, nullable=False)
    create_date = Column(
        DateTime(timezone=True),
        nullable=True
    )
    end_date = Column(
        DateTime(timezone=True),
        nullable=True 
    )
    elapsed_time = Column(Numeric(precision=5), nullable=False)

    #search_type = Column(ChoiceTypes(SEARCH_TYPES))
    #citation_search_terms = Column(ARRAY(Unicode)), 
    #context_search_terms = Column(ARRAY(Unicode)), 
    #document_search_terms = Column(ARRAY(Unicode)),
    #tags= Column(ARRAY(Unicode)), 
    #max_results = Column(Integer(), nullable=True)

    __table_args__ = (
        PrimaryKeyConstraint('id', name='request_pk'),
        Index('request_ip_address_index', 'ip_address'),
        Index('request_request_url_index', request_url, mysql_length=200),
        Index('request_end_date_index', 'create_date')
    )

    def __repr__(self):
        return "<Request(id='%s', url='%s')>" % (
            self.id,
            self.cited_url
        )

class Domain(Base):
    __tablename__ = 'domain'

    id = Column(BigInteger(), Sequence('document_id_seq'))  
    domain_url = Column(URLType, nullable=False)
    owner_user = Column(BigInteger(), ForeignKey('user.id'), index=True, nullable=False )
    create_date = Column(
        DateTime(timezone=True),
        index=True,
        default=datetime.datetime.utcnow,
        nullable=False
    )

    __table_args__ = (
        PrimaryKeyConstraint('id', name='domain_pk'),
        Index('domain_domain_url_unique', 'domain_url', mysql_length=100, unique=True),
        Index('domain_owner_user_index', 'owner_user'),
    )

    def __repr__(self):
        return "<Domain (id='%s', domain_url='%s')>" % (
            self.id,
            self.domain_url
        )

class Document(Base):
    __tablename__ = 'document'

    id = Column(BigInteger(), Sequence('document_id_seq'))  
    request_id = Column(BigInteger(), ForeignKey('request.id'), index=True, nullable=False)
    domain_id = Column(BigInteger(), nullable=False)
    document_url = Column(URLType, nullable=False)
    content_type = Column(String(50), nullable=False)
    title = Column(String(256), nullable=True)
    body_binary = Column(LargeBinary, nullable=True)
    body_html = Column(UnicodeText, nullable=True)
    body_text = Column(UnicodeText, default='')
    encoding = Column(String(16), nullable=False)
    language = Column(String(16), nullable=False)
    word_count = Column(Integer, nullable=False)
    content_hash = Column(String(64), nullable=False)
    create_date = Column(
        DateTime(timezone=True),
        index=True,
        default=datetime.datetime.utcnow,
        nullable=False
    )
    end_date = Column(
        DateTime(timezone=True),
        index=True,
        default=null,
        nullable=True
    )

    __table_args__ = (
        PrimaryKeyConstraint('id', name='document_pk'),
        Index('document_request_id_index', 'request_id'),
        Index('document_domain_id_index', 'domain_id'),
        Index('document_document_url_index', 'document_url', mysql_length=256),
        UniqueConstraint('content_hash', name='document_content_hash_unique' ),
    )

    def __repr__(self):
        return "<Document (id='%s', title='%s', url='%s',  >" % (
            self.id,
            self.title,
            self.document_url,
        )

class Citation(Base):
    __tablename__ = 'citation'

    id = Column(BigInteger(), Sequence('citation_id_seq'))
    request_id = Column(BigInteger(), ForeignKey('request.id'), index=True, nullable=False)
    sha256 = Column(String(64), nullable=False, index=True, unique=True)

    citing_domain_id = Column(BigInteger(), ForeignKey('domain.id'), index=True, nullable=False)
    citing_document = Column(BigInteger(), ForeignKey('document.id'), nullable=False)
    citing_url = Column(URLType, nullable=False)
    citing_url_canonical = Column(URLType, nullable=False)
    citing_quote = Column(UnicodeText(), nullable=False)
    citing_context_before = Column(UnicodeText)
    citing_context_after = Column(UnicodeText)

    cited_domain_id = Column(BigInteger(), ForeignKey('domain.id'), index=True, nullable=False)
    cited_document = Column(BigInteger(), ForeignKey('document.id'), nullable=False)
    cited_url = Column(String(2048), nullable=False)
    cited_quote = Column(String(2048), nullable=False)
    cited_context_before = Column(UnicodeText(), nullable=True)
    cited_context_after = Column(UnicodeText(), nullable=True)
    create_date = Column(
        DateTime(timezone=True),
        index=True,
        default=datetime.datetime.utcnow,
        nullable=False
    )

    __table_args__ = (
        PrimaryKeyConstraint('id', name='citation_pk'),
        UniqueConstraint('sha256', name='citation_sha256_unique'),
        Index('citation_request_id_index', 'request_id'),
        
        Index('citation_citing_domain_id_index', 'citing_domain_id'),
        Index('citation_citing_document_index', 'citing_document'),
        Index('citation_citing_url_index', 'citing_url', mysql_length=256),
        Index('citation_citing_url_canonical_index', 'citing_url_canonical', mysql_length=256),
        Index('citation_citing_quote_index', 'citing_quote', mysql_length=256),

        Index('citation_cited_domain_index', 'cited_domain_id'),
        Index('citation_cited_document_index', 'cited_document'),
        Index('citation_cited_url_index', 'cited_url', mysql_length=256),
        Index('citation_cited_quote_index', 'cited_quote', mysql_length=256),
        Index('citation_create_date_index', 'create_date')
    )

    def __repr__(self):
        return "<Citation(id='%s', citing_quote='%s', citing_url='%s')>" % (
            self.id,
            self.citing_quote,
            self.citing_url
        )

    def __init__(self, request_id, sha256, citing_url, citing_url_canonical, citing_quote, citing_context_before, citing_context_after, cited_url, cited_quote, cited_context_before, cited_context_after ):
        self.request_id = request_id 
        self.sha256 = sha256 
        self.citing_url = citing_url
        self.citing_url_canonical = citing_url_canonical
        self.citing_quote = citing_quote 
        self.citing_context_before = citing_context_before 
        self.citing_context_after = citing_context_after 
        self.cited_url = cited_url 
        self.cited_quote = cited_quote 
        self.cited_context_before = cited_context_before 
        self.cited_context_after = cited_context_after 


Base.metadata.drop_all(engine)
Base.metadata.create_all(engine)
#db.session.commit()