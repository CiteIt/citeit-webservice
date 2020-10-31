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
    Boolean, null, orm, Unicode, func

from sqlalchemy_utils import EmailType, CountryType, ChoiceType, \
    IPAddressType, PasswordType, PhoneNumberType, TimezoneType   # URLType


from sqlalchemy_utils import PhoneNumber

from sqlalchemy.ext.declarative import declarative_base

import hashlib

from datetime import datetime
import settings

import pymysql
pymysql.install_as_MySQLdb

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = settings.SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

engine = create_engine(settings.SQLALCHEMY_DATABASE_URI)

Base = declarative_base()

################################# New: Database Connection Error
Base.metadata.drop_all(engine)

class Domain(Base):
    __tablename__ = 'domain'

    id = Column(BigInteger(), Sequence('document_id_seq'))  
    domain_url = Column(String(255), nullable=False)    #2048
    owner_user = Column(BigInteger(), ForeignKey('user.id'), nullable=False )

    __table_args__ = (
        PrimaryKeyConstraint('id', name='domain_pk'),
        #UniqueConstraint(func.md5(domain_url), name='domain_domain_url_unique'),
        #hashlib.sha256( domain_url.encode('ascii') + settings.HASH_SALT ).hexdigest()

        Index('domain_domain_url_unique', (domain_url) , unique=True),
        Index('domain_domain_url', 'domain_url', mysql_length=100),
        Index('domain_owner_user_index', 'owner_user'),
    )

    def __repr__(self):
        return "<Tag(id='%s', tag='%s')>" % (
            self.id,
            self.tag
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
    ip_address = Column(IPAddressType, nullable=False)
    request_type = Column(ChoiceType(REQUEST_TYPES))
    request_url = Column(String(2048), nullable=False)
    domain_id = Column(BigInteger(), nullable=True)
    user_agent = Column(String(8000), nullable=False)
    create_date = Column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False
    )

    __table_args__ = (
        PrimaryKeyConstraint('id', name='request_pk'),
        Index('request_ip_address_index', 'ip_address'),
        Index('request_url_index', request_url, mysql_length=200),
        Index('request_create_date_index', 'create_date')
    )

    def __repr__(self):
        return "<Request(id='%s', url='%s')>" % (
            self.id,
            self.url
        )


class Citation(Base):
    __tablename__ = 'citation'

    id = Column(BigInteger(), Sequence('citation_id_seq'))
    request_id = Column(BigInteger(), ForeignKey('request.id'), index=True, nullable=False)
    sha256 = Column(String(64), nullable=False, index=True, unique=True)

    citing_domain_id = Column(BigInteger(), ForeignKey('domain.id'), index=True, nullable=False)
    citing_document = Column(BigInteger(), ForeignKey('document.id'), nullable=False)
    citing_url = Column(String(2048), nullable=False)
    citing_url_canonical = Column(String(2048), nullable=False)
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
        default=datetime.utcnow,
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


class Document(Base):
    __tablename__ = 'document'

    id = Column(BigInteger(), Sequence('document_id_seq'))  
    request_id = Column(BigInteger(), ForeignKey('request.id'), index=True, nullable=False)
    domain_id = Column(BigInteger(), nullable=False)
    url = Column(String(2048), nullable=False)
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
        default=datetime.utcnow,
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
        Index('document_url_index', 'url', mysql_length=256),
        # Index('document_content_hash_unique_index', 'content_hash', 'domain_id' ),

        {  # Partitioning: https://groups.google.com/g/sqlalchemy/c/qCQFD2LNyTQ
        'info': {
            'mysql_partition': """
                 PARTITION BY RANGE Year(end_date)

                 (  PARTITION current_document VALUES LESS THAN (1900),
                    PARTITION archived_document VALUES LESS THAN (2050)
                 )
             """
        }
        }
    )

    def __repr__(self):
        return "<Document (id='%s', title='%s', url='%s',  >" % (
            self.id,
            self.title,
            self.url,
        )

class Tag(Base):
    __tablename__ = 'tag'

    id = Column(BigInteger(), Sequence('tag_id_seq'))
    tag = Column(String(100), unique=True, nullable=False)
    parent_id = Column(BigInteger(), ForeignKey('tag.id'), nullable=False)
    create_date = Column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False
    )

    __table_args__ = (
        PrimaryKeyConstraint('id', name='tag_pk'),
        UniqueConstraint('tag',name='citation_tag_unique'),
        Index('tag_parent_id_index', 'tag', 'parent_id'),
        Index('tag_created_index', 'create_date')
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
        Index('citation_tag_citation_id', 'citation_id', 'tag_id'),
        Index('citation_tag_tag_id', 'tag_id', 'citation_id')
    )

    def __repr__(self):
        return "<Tag(citation_id='%s', tag='%s')>" % (
            self.citation_id,
            self.tag_id,
        )


class User(Base):
    __tablename__ = 'user'

    id = Column(BigInteger, Sequence('user_id_seq') )
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
    create_date = Column(DateTime(), default=datetime.now, nullable=False)
    update_date = Column(DateTime(), default=datetime.now, nullable=False, onupdate=datetime.now)

    phone = orm.composite(
        PhoneNumber,
        _phone,
        country, 
        nullable=True
    )

    __table_args__ = (
        PrimaryKeyConstraint('id', name='user_pk'),
        UniqueConstraint('email', name='user_email_unique')
    )

    def __repr__(self):
        return "<User(email='%s', fullname='%s' )>" % (
            self.email,
            self.fullname
        )




Base.metadata.drop_all(engine)
Base.metadata.create_all(engine)
db.session.commit()


"""
# ADDITIONAL NATIVE DATABASE COMMANDS:

# CREATE FULLTEXT INDEX document_body_text
# ON Document(body_text);
"""


"""
#db.create_all()
print("Tables Created")

print("Creating Users")
#admin = User('admin', 'admin@example.com')
#guest = User('guest', 'guest@example.com')
#db.session.add(admin)
#db.session.add(guest)
#db.session.commit()
#users = User.query.all()
#print(users)


#from sqlalchemy import event

# standard decorator style
@event.listens_for(Document, 'before_insert')
def receive_before_insert(mapper, connection, target):
    "listen for the 'before_insert' event"

    # ... (event handling logic) ...
    
    update document
      set end_date = datetime.utcnow
    where url = url and end_date is null


db.drop_all()


admin = User('admin@example.com','test-pasw**d')

db.create_all() # In case user table doesn't exists already. Else remove it.

db.session.add(admin)

db.session.commit() # This is needed to write the changes to database

User.query.all()

User.query.filter_by(username='admin').first()
"""
