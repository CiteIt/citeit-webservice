# -*- coding: utf-8 -*-

# Copyright (C) 2015-2019 Tim Langeman and contributors
# <see AUTHORS.txt file>
#
# This library is part of the CiteIt project:
# http://www.citeit.net/

# The code for this server library is released under the MIT License:
# http://www.opensource.org/licenses/mit-license

from lib.citeit_quote_context.tests.quote_hash_match import QuoteHashTest
from lib.citeit_quote_context.url import URL
from lib.citeit_quote_context.text_convert import TextConvert
from lib.citeit_quote_context.text_convert import html_to_text
from lib.citeit_quote_context.text_convert import levenshtein_distance
from lib.citeit_quote_context.text_convert import show_diff

import os
import csv
import requests


__author__ = 'Tim Langeman'
__email__ = "timlangeman@gmail.com"
__copyright__ = "Copyright (C) 2015-2019 Tim Langeman"
__license__ = "MIT"
__version__ = "0.3"

debug = True

def testHash(citing_url, js_hash, js_hashkey, debug=True):

    u = URL(citing_url)
    citations = u.citations()
    for quote in citations:
        cited_url = quote['cited_url']
        citing_quote = quote['citing_quote']
        citing_quote = html_to_text(citing_quote)
        citing_quote = TextConvert(citing_quote).escape()

    q = QuoteHashTest(
        quote['citing_quote'], # excerpt from citing document
        citing_url,      # url of the document that is doing the quoting
        cited_url,       # url of document that is being quoted
        js_hash, 
        js_hashkey 
    )

    computed_hashkey = citing_quote + "|" + citing_url + "|" + cited_url
    computed_hash =  q.hash_computed()

    quote_diff = show_diff(computed_hashkey, js_hashkey)
    debug("\n\nURL: " + citing_url, debug)

    if (js_hash == computed_hash):
      debug("Match >> " + js_hash, debug)
    else:
      debug("Miss >> " +  js_hash + " <> " + computed_hash, debug)
      debug("\n", debug)
      debug("JS:       " + js_hashkey + "\n\n", debug)
      debug("Computed: " + computed_hashkey, debug)

    debug("\n", debug)
    debug(">> Diff: (" + str(len(quote_diff)) + ") " + str(quote_diff), debug)

def debug(message, debug=False):
    if debug:
        print(message)


citing_url = 'http://demo.citeit.net/index.php/2017/02/12/the-captive-aliens-who-remain-our-shame/'
js_hashkey = "MenlikeJeffersonAdamsFranklinandWashingtonParkinsonwritesdevelopedamythaboutwhowasandwasnotapartoftheRevolutionarymovement;aboutwhohadaninterestandwhodidnotOtheresteemedadvocatesoftheRevolutionsuchasThomasPaineandtheMarquisdeLafayettejoinedtheeffortAccordingtoParkinsonthesemenchosetoprosecutetheAmericanwarforindependenceinawaythatputraceattheheartofthematterTheyusedactuallyhelpedfomentracialprejudiceastheprincipalmeansofcreatingunityacrossthethirteencoloniesinordertoprepareAmericanstodobattlewithGreatBritainThebasesentimentstheypromotedforpoliticalexpediencysurvivedthefightingandthenarrativethatdismissedblacksandNativepeoplesasalientoAmericaandconflatedwhiteandcitizenlivedattheheartoftherepublicithelpedcreatefordecadestocomeEffectivewarstoriesweredefinitelyrequiredbecausedespitethecolonistscomplaintsabouttyrannyandbeingreducedtoofallthingsslaverytheyweretheleasttaxedmostsociallymobilehighestlandowningarguablymostprosperouspeopleinthewesternworld|http://demo.citeit.net/index.php/2017/02/12/the-captive-aliens-who-remain-our-shame/|http://www.nybooks.com/articles/2017/01/19/american-revolution-captive-aliens-our-shame/"
hashkey = 'MenlikeJeffersonAdamsFranklinandWashingtonParkinsonwritesdevelopedamythaboutwhowasandwasnotapartoftheRevolutionarymovement;aboutwhohadaninterestandwhodidnotOtheresteemedadvocatesoftheRevolutionsuchasThomasPaineandtheMarquisdeLafayettejoinedtheeffortAccordingtoParkinsonthesemenchosetoprosecutetheAmericanwarforindependenceinawaythatputraceattheheartofthematterTheyusedactuallyhelpedfomentracialprejudiceastheprincipalmeansofcreatingunityacrossthethirteencoloniesinordertoprepareAmericanstodobattlewithGreatBritainThebasesentimentstheypromotedforpoliticalexpediencysurvivedthefightingandthenarrativethatdismissedblacksandNativepeoplesasalientoAmericaandconflatedwhiteandcitizenlivedattheheartoftherepublicithelpedcreatefordecadestocomeEffectivewarstoriesweredefinitelyrequiredbecausedespitethecolonistscomplaintsabouttyrannyandbeingreducedtoofallthingsslaverytheyweretheleasttaxedmostsociallymobilehighestlandowningarguablymostprosperouspeopleinthewesternworld|http://demo.citeit.net/index.php/2017/02/12/the-captive-aliens-who-remain-our-shame/|http://www.nybooks.com/articles/2017/01/19/american-revolution-captive-aliens-our-shame/'
js_hash = '41893361ac4313cfe17df4e6d29e5eb97ef48eb4c3e52ddf561c7a2dff987d7f'


citing_url = 'http://demo.citeit.net/index.php/2017/02/12/mr-darcy-youre-no-colin-firth/'
js_hashkey = "RathertherealMrDarcywouldhavebeenpaleandpointychinnedandwouldhavehadalongnoseonanovalbeardlessfaceHishairstrangelywouldhavebeenwhiteAndhewouldhavebeenslightlyundernourishedwithslopingshouldersmoreballetdancerthanbeefcakeaccordingtooneoftheauthorsofanewstudy|http://demo.citeit.net/index.php/2017/02/12/mr-darcy-youre-no-colin-firth/|https://www.nytimes.com/2017/02/09/books/colin-firth-mr-darcy.html"
hashkey    = "RathertherealMrDarcywouldhavebeenpaleandpointychinnedandwouldhavehadalongnoseonanovalbeardlessfaceHishairstrangelywouldhavebeenwhiteAndhewouldhavebeenslightlyundernourishedwithslopingshouldersmoreballetdancerthanbeefcakeaccordingtooneoftheauthorsofanewstudy|http://demo.citeit.net/index.php/2017/02/12/mr-darcy-youre-no-colin-firth/|https://www.nytimes.com/2017/02/09/books/colin-firth-mr-darcy.html"
js_hash = 'be27e6f3396843ca50d566cbd966b4c8c9f3ad107db61eafc55e433fa63fdfa5'

citing_url = 'http://demo.citeit.net/index.php/2017/02/12/the-captive-aliens-who-remain-our-shame/'
js_hashkey = "MenlikeJeffersonAdamsFranklinandWashingtonParkinsonwritesdevelopedamythaboutwhowasandwasnotapartoftheRevolutionarymovement;aboutwhohadaninterestandwhodidnotOtheresteemedadvocatesoftheRevolutionsuchasThomasPaineandtheMarquisdeLafayettejoinedtheeffortAccordingtoParkinsonthesemenchosetoprosecutetheAmericanwarforindependenceinawaythatputraceattheheartofthematterTheyusedactuallyhelpedfomentracialprejudiceastheprincipalmeansofcreatingunityacrossthethirteencoloniesinordertoprepareAmericanstodobattlewithGreatBritainThebasesentimentstheypromotedforpoliticalexpediencysurvivedthefightingandthenarrativethatdismissedblacksandNativepeoplesasalientoAmericaandconflatedwhiteandcitizenlivedattheheartoftherepublicithelpedcreatefordecadestocomeEffectivewarstoriesweredefinitelyrequiredbecausedespitethecolonistscomplaintsabouttyrannyandbeingreducedtoofallthingsslaverytheyweretheleasttaxedmostsociallymobilehighestlandowningarguablymostprosperouspeopleinthewesternworld|http://demo.citeit.net/index.php/2017/02/12/the-captive-aliens-who-remain-our-shame/|http://www.nybooks.com/articles/2017/01/19/american-revolution-captive-aliens-our-shame/"
hashkey = 'MenlikeJeffersonAdamsFranklinandWashingtonParkinsonwritesdevelopedamythaboutwhowasandwasnotapartoftheRevolutionarymovement;aboutwhohadaninterestandwhodidnotOtheresteemedadvocatesoftheRevolutionsuchasThomasPaineandtheMarquisdeLafayettejoinedtheeffortAccordingtoParkinsonthesemenchosetoprosecutetheAmericanwarforindependenceinawaythatputraceattheheartofthematterTheyusedactuallyhelpedfomentracialprejudiceastheprincipalmeansofcreatingunityacrossthethirteencoloniesinordertoprepareAmericanstodobattlewithGreatBritainThebasesentimentstheypromotedforpoliticalexpediencysurvivedthefightingandthenarrativethatdismissedblacksandNativepeoplesasalientoAmericaandconflatedwhiteandcitizenlivedattheheartoftherepublicithelpedcreatefordecadestocomeEffectivewarstoriesweredefinitelyrequiredbecausedespitethecolonistscomplaintsabouttyrannyandbeingreducedtoofallthingsslaverytheyweretheleasttaxedmostsociallymobilehighestlandowningarguablymostprosperouspeopleinthewesternworld|http://demo.citeit.net/index.php/2017/02/12/the-captive-aliens-who-remain-our-shame/|http://www.nybooks.com/articles/2017/01/19/american-revolution-captive-aliens-our-shame/'
js_hash = '41893361ac4313cfe17df4e6d29e5eb97ef48eb4c3e52ddf561c7a2dff987d7f'


testHash(citing_url, js_hash, js_hashkey, debug)

URL:    http://demo.citeit.net/2019/11/28/first-french-post/
CependantselonlesecrétairegénéraldeForceouvrièrecheminotsPhilippeHerbeckinterrogéparLExpress«lebutcenestévidemmentpasdallerjusquàNoël»Ilestimedailleursquela«situationdupouvoirdachatdesFrançaisfaitquelagrèvenepourrapasdurertroissemaines»Ilmisepoursapartsurunemobilisationmassivelespremières72heurespourinciterlegouvernementàretirersonprojetderéformedesretraitesMaisilannonce«Nousnelâcheronspasjusquauretrait»Lebrasd


URL:    http://demo.citeit.net/2019/11/27/deutshe-wolfe-german-test/
Quote:  Überprüfen lässt sich das nicht, denn das Internet bleibt abgeschaltet. Der Sicherheit im Land werde alles geopfert, hieß es zur Begründung.
Key:    ÜberprüfenlässtsichdasnichtdenndasInternetbleibtabgeschaltetDerSicherheitimLandwerdeallesgeopferthießeszurBegründung


URL:    http://demo.citeit.net/2019/11/27/second-french-post/
Quote:  D'autant que, depuis que la RATP a lancé son appel à une grève interprofessionnelle reconductible et illimitée, elle a été rejointe par de nombreuses organisations
Key:    DautantquedepuisquelaRATPalancésonappelàunegrèveinterprofessionnellereconductibleetillimitéeelleaétérejointepardenombreusesorganisations


URL:    http://demo.citeit.net/2017/02/14/power-doesnt-always-corrupt/
Quote:  Power doesn't ­always corrupt, and you can see it in the case of, for example, Al Smith or Sam Rayburn. There, power cleanses. But what power always does is reveal, because when you're climbing, you have to conceal from people what it is you're really willing to do, what it is you want to do. But once you get enough power, once you're there, where you wanted to be all along, then you can see what the protagonist wanted to do all along, because now he's doing it.
Key:    Powerdoesnt­alwayscorruptandyoucanseeitinthecaseofforexampleAlSmithorSamRayburnTherepowercleansesButwhatpoweralwaysdoesisrevealbecausewhenyoureclimbingyouhavetoconcealfrompeoplewhatitisyourereallywillingtodowhatitisyouwanttodoButonceyougetenoughpoweronceyouretherewhereyouwantedtobeallalongthenyoucanseewhattheprotagonistwantedtodoallalongbecausenowhesdoingit



Powerdoesnt­alwayscorrupt