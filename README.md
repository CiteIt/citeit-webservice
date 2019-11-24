# CiteIt Web Citation Service

The CiteIt Web Citation Service allows web authors
to **demonstrate the context of their quotations** by helping them display the
500 characters of context before and after the quote they are citing.

## View Demo: ##
Demo site with video:
  * https://www.CiteIt.net/

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
