# Copyright (C) 2015-2020 Tim Langeman and contributors
# <see AUTHORS.txt file>
#
# This library is part of the CiteIt project:
# http://www.citeit.net/

# The code for this server library is released under the MIT License:
# http://www.opensource.org/licenses/mit-license

from sqlalchemy import Column, Integer, String, Numeric, UnicodeText, DateTime
import datetime

from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    fullname = Column(String)
    password = Column(String)

    def __repr__(self):
        return "<User(name='%s', fullname='%s', password='%s')>" % (
            self.name,
            self.fullname,
            self.password
        )

class Request(Base):
    REQUEST_TYPES = [
        (u'post_url' = u'Post URL'),                                      # url
        (u'get_posts_cited_by' = u'Get Posts Cited by this URL/Domain'),  # url, start_date, end_date, (default to latest), citation_terms, context_terms, tags, document_terms, search_type, max_results
        (u'get_posts_citing' = u"Get Posts that Cite this URL"),          # url, start_date, end_date, (default to latest), citation_terms, context_terms, tags, document_terms, search_type, max_results
        (u'get_archives_of_url' = 'Get Archive of URL'),                  # url, start_date, end_date, max_results 
    SEARCH_TYPES = [
        (u'url' = u'URL'),
        (u'domain' = u'Domain (Strict)'),
        (u'domain_subdomains' = u'Domain (Subdomains)')
    ]

    id = Column(BigInteger(), primary_key=True)
    ip_address = Column(IPAddressType)
    request_type = Column(ChoiceTypes(REQUEST_TYPES))
    search_type = Column(ChoiceTypes(SEARCH_TYPES))
    request_date = Column(
        DateTime(timezone=True),
        default=datetime.datetime.utcnow,
        nullable=False
    )
    url = Column(String(2000), nullable=False)
    citation_search_terms = Column(ARRAY(Unicode)), 
    context_search_terms = Column(ARRAY(Unicode)), 
    document_search_terms = Column(ARRAY(Unicode)),
    tags= Column(ARRAY(Unicode)), 
    start_date = (
        DateTime(timezone=True),
        nullable=True
    )
    end_date = (
        DateTime(timezone=True),
        nullable=True 
    )
    max_results = Column(Integer(), nullable=True)
    elapsed_time = Column(Numeric(precision=5), nullable=False)

    def __repr__(self):
        return "<Request(id='%s', url='%s')>" % (
            self.id,
            self.cited_url
        )

class Document(Base):
    __tablename__ = 'citeit_document'
    
    id = Column(BigInteger(), primary_key=True)
    sha256 = Column(String(64), nullable=False, unique=True)
    domain_id = Column(Integer), nullable=False)
    url = Column(String(2000), nullable=False)
    title = Column(String(2000), nullable=False)
    document_text = Column(UnicodeText)
    encoding = Column(UnicodeText) 
    word_count(Integer, null=False)
    character_count(Integer, null=False)
    download_date = Column(
        DateTime(timezone=True),
        default=datetime.datetime.utcnow,
        nullable=False
    )

    def __repr__(self):
        return "<Document (id='%s', url='%s', title='%s'>" % (
            self.id,
            self.title
        )


class Quote(Base):
    __tablename__ = 'citeit_quote'

    id = Column(BigInteger(), primary_key=True)
    sha256 = Column(String(64), nullable=False, unique=True)
    citing_url = Column(String(2000), nullable=False)
    citing_url_canonical = Column(String(2000), nullable=False)
    citing_quote = Column(UnicodeText(), nullable=False)
    citing_quote_length = Column(Integer(), nullable=True)
    citing_quote_start_position = Column(Integer(), nullable=True)
    citing_quote_end_position = Column(Integer(), nullable=True)
    citing_context_start_position = Column(Integer(), nullable=True)
    citing_context_end_position = Column(Integer(), nullable=True)
    citing_context_before = Column(UnicodeText)
    citing_context_after = Column(UnicodeText)
    citing_text = Column(UnicodeText)
    citing_doc_type = Column(String(4), default='html', nullable=True)
    citing_raw = Column(UnicodeText, nullable=True)
    citing_archive_url = Column(String(2000))
    citing_cache_url = Column(String(2000))
    citing_download_date = Column(
        DateTime(timezone=True),
        default=datetime.datetime.utcnow,
        nullable=False
    )
    cited_url = Column(String(2000), nullable=False)
    cited_citeit_url = Column(String(2000), nullable=False)
    cited_quote = Column(UnicodeText(), nullable=True)
    cited_quote_length = Column(Integer(), nullable=True)
    cited_quote_start_position = Column(Integer(), nullable=True)
    cited_quote_end_position = Column(Integer(), nullable=True)
    cited_context_start_position = Column(Integer(), nullable=True)
    cited_context_end_position = Column(Integer(), nullable=True)
    cited_context_before = Column(UnicodeText(), nullable=True)
    cited_context_after = Column(UnicodeText(), nullable=True)
    cited_text = Column(UnicodeText(), nullable=True)
    cited_doc_type = Column(String(4), default='html', nullable=True)
    cited_raw = Column(UnicodeText(), nullable=True)
    cited_archive_url = Column(String(2000), nullable=False)
    cited_cache_url = Column(String(2000), nullable=False)
    cited_download_date = Column(
        DateTime(timezone=True),
        default=datetime.datetime.utcnow,
        nullable=False
    )
    create_date = Column(
        DateTime(timezone=True),
        default=datetime.datetime.utcnow,
        nullable=False
    )
    create_elapsed_time = Column(Numeric(precision=5), nullable=False)

    def __repr__(self):
        return "<Quote(id='%s', citing_text='%s')>" % (
            self.id,
            self.citing_text
        )

