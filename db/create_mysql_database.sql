/* MYSQL Create Database */


CREATE TABLE IF NOT EXISTS  tag (
	id BIGINT NOT NULL AUTO_INCREMENT,
    tag VARCHAR(256) NOT NULL,
	created TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    PRIMARY KEY (id),
	UNIQUE KEY unique_email (tag)
);


CREATE TABLE IF NOT EXISTS  citation_tag (
    id BIGINT NOT NULL AUTO_INCREMENT,
    citation_id BIGINT NOT NULL,
	citation_tag_id BIGINT NOT NULL,
	created TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    PRIMARY KEY (id),
	UNIQUE KEY unique_email (citation_id)
);

CREATE TABLE IF NOT EXISTS  requests (
    id BIGINT NOT NULL AUTO_INCREMENT,
    request_url VARCHAR(2083) NOT NULL,
	request_type CHAR(1) NOT NULL,   
	duration TIME,
	created TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
	user_agent VARCHAR(8000),
	ip_source INT UNSIGNED NOT NULL,
	PRIMARY KEY (id)
);


CREATE TABLE IF NOT EXISTS  document (
    id BIGINT NOT NULL AUTO_INCREMENT,
	request_id BIGINT,
    document_url VARCHAR(2083) NOT NULL,
	unique_url_hash CHAR(32),
	title VARCHAR(100),
	body_html MEDIUMTEXT,
	body_text MEDIUMTEXT,
	content_type VARCHAR(50),
	encoding CHAR(2),
	language VARCHAR(10),
	created TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
	updated TIMESTAMP ON UPDATE CURRENT_TIMESTAMP NOT NULL,
    PRIMARY KEY (id),
	UNIQUE KEY unique_url_hash (unique_url_hash)
);


CREATE TABLE IF NOT EXISTS  citation (
    id BIGINT NOT NULL AUTO_INCREMENT,
	sha256 CHAR(64) NOT NULL,
    citing_url VARCHAR(2083) NOT NULL,
	citing_quote MEDIUMTEXT NOT NULL,
	citing_context_before VARCHAR(500),
	citing_context_after VARCHAR(500),
	cited_url VARCHAR(2083) NOT NULL,
	cited_quote MEDIUMTEXT NOT NULL,
	cited_context_before VARCHAR(500),
	cited_context_after VARCHAR(500),
	created TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
	updated TIMESTAMP ON UPDATE CURRENT_TIMESTAMP NOT NULL,
    PRIMARY KEY (id),
	UNIQUE KEY unique_sha256 (sha256)
);


/*
	Request Types:
	D = Document
	I = Index

*/
