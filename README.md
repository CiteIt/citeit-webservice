# CiteIt Web Citation Service

The CiteIt Web Citation Service allows web authors
to **demonstrate the context of their quotations** by helping them display the
500 characters of context before and after the quote they are citing.

## View Demo: ##
Demo site with video:
  * https://www.CiteIt.net/
  
Sample API Calls:
  * https://www.citeit.net/sample-code/  

## Tools Used ##
  * **API Server**: [Python](https://www.python.org/) [Flask](http://flask.pocoo.org/) Server
  * **Database**: [SQL Alchemy](https://www.sqlalchemy.org/), 
                  ([Postgres](https://www.postgresql.org/) or Other Database)
  * **[jQuery Library](https://github.com/CiteIt/citeit-jquery)**: custom function to wrap &lt;blockquote&lt; and &lt;q&gt; tags
  * **[Wordpress Plugin](https://github.com/CiteIt/citeit-wordpress)**: 
    * adds buttons to Wordpress editor for blockquote and pre tags.
    * the working version was written before  Gutenberg.
    * (looking for help creating a Gutenberg version of the plugin)
    * Submits pages to API.
    
  * **Dependencies**: 
    * [Google Diff Match Patch](https://code.google.com/archive/p/google-diff-match-patch/):
        fuzzy text matching algorithm
    * [Beautiful Soup](https://www.crummy.com/software/BeautifulSoup/): used to convert html 
        to text and locate the canonical urls within html
    * [Flask](https://palletsprojects.com/p/flask/)
    * [SQL Alchemy](https://www.sqlalchemy.org/)
    * [boto3](https://github.com/boto/boto3)
    * Python [Requests](http://docs.python-requests.org/en/master/): HTTP for humans
    * [ftfy](http://ftfy.readthedocs.io/en/latest/): convert bad unicode to good unicode
              


## How CiteIt Works:

1. An author notifies the CiteIt Web Service that they have created a new
citation by sending a HTTP POST request with the URL of the author's page 
to api.citeit.net.

1. The CiteIt Web Service retrieves the author's page and locates all the
citations within the document, saving the urls and the text of each citation.

1. The CiteIt web service retrieves the pages for each cited URL and
compares the cited source text with the text from the author's citation.

1. If the service finds a match, it calculates the 500 characters before
and after each quotation.

1. The CiteIt web service saves the 500 characters before and after each
quotation to a json file and uploads each json file to the Amazon S3 Cloud.

1. After the author installs either the CiteIt Wordpress plugin
or the CiteIt jQuery library on their site, the plugin instructs subsequent
visitors to load the contextual json files from the Amazon S3 Cloud.

1. The CiteIt jQuery library, loads the contextual data from the json file
into hidden &lt;div&gt; elements created in the author's page, which display when
a reader clicks on an arrow above or below the quotation.

## Setup:

### Flask:
cd app/

cp settings-default.py settings.py

(populate settings.py with own passwords)

export FLASK_APP=app.py

set FLASK_RUN_PORT=80

python3 -m flask run --host=0.0.0.0 --port=80

### Docker:
docker build -t citeit_webservice:latest .

docker tag 9c08913ff568a479 citeit/citeit_webservice:latest
docker tag 9c08913ff568a479 citeit/citeit_webservice:v0.4.9
docker push citeit/citeit_webservice:v0.4.9
docker push citeit/citeit_webservice:latest


docker run -p 80:80 -e AMAZON_ACCESS_KEY=password -e AMAZON_SECRET_KEY=password citeit/citeit_webservice:latest
docker stop efb18851a652


### Docker with SSL using Lets Encrypt:

docker ps 

docker stop ID

docker system prune

    --publish 80:80 \

STEP 1:
docker run --detach \
    --name nginx-proxy \
    --publish 443:443 \
    --volume certs:/etc/nginx/certs \
    --volume vhost:/etc/nginx/vhost.d \
    --volume html:/usr/share/nginx/html \
	jwilder/nginx-proxy

STEP 2:
docker run --detach \
    --name nginx-proxy-letsencrypt \
    --volumes-from nginx-proxy \
    --volume /var/run/docker.sock:/var/run/docker.sock:ro \
    --volume acme:/etc/acme.sh \
    --env "DEFAULT_EMAIL=timlangeman@gmail.com" \
    jrcs/letsencrypt-nginx-proxy-companion

STEP 3:
docker run --detach \
  --name citeit_webservice \
  --name citeit_webservice \
  --env "VIRTUAL_HOST=api.citeit.net" \
  --env "LETSENCRYPT_HOST=api.citeit.net" \
	-e AMAZON_ACCESS_KEY=******************* \
	-e AMAZON_SECRET_KEY=*********************+*** \
citeit/citeit_webservice

### Test SSL port locally:

openssl s_client -connect localhost:443 -servername api.citeit.net

140346583314880:error:0200206F:system library:connect:Connection refused:../crypto/bio/b_sock2.c:110:
140346583314880:error:2008A067:BIO routines:BIO_connect:connect error:../crypto/bio/b_sock2.c:111:

netstat -ntlp | grep LISTEN

tcp        0      0 127.0.0.53:53           0.0.0.0:*               LISTEN      3921/systemd-resolv 
tcp        0      0 0.0.0.0:22              0.0.0.0:*               LISTEN      979/sshd            
tcp6       0      0 :::22                   :::*                    LISTEN      979/sshd


### Open SSL port

sudo apt install ufw
sudo ufw allow ssh
sudo ufw enable
sudo ufw status verbose

netstat -ntlp | grep LISTEN


## Inspiration:
I got this idea in 2015, while I was writing an article about hypertext pioneer
[Ted Nelson](https://en.wikipedia.org/wiki/Ted_Nelson).

  * https://www.openpolitics.com/articles/ted-nelson-philosophy-of-hypertext.html

Like the Web, CiteIt still follows the "[Worse is Better](https://www.dreamsongs.com/RiseOfWorseIsBetter.html)" approach because I don't have the technical ability or resources to implement the 
Ted's "Right Thing".

I hope CiteIt allows more people to get a glimpse of Ted's original proposal and 
inspires other programmers to built towards that vision.

-**[Tim Langeman](https://www.openpolitics.com/tim/)**

Akron, PA (USA)

## License ##
I want this form of expanding contextual citation to **become as widely adopted as possible**, so I'm releasing it under 
the **[MIT License](https://opensource.org/licenses/MIT)**.  I encourage you to build on top of my code.  You don't have to 
contribute back to this project, but there are advantages to cooperation.


## History:
Earlier versions of this concept were written for:
1. PHP: https://github.com/timlangeman/quote-context
1. Django: https://github.com/neotext/neotext-django-server
