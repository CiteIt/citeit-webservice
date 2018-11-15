# Copyright (C) 2015-2018 Tim Langeman and contributors
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


class Quote(Base):
    __tablename__ = 'citeit_quote'

    id = Column(Integer(), primary_key=True)
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
