
import yt_dlp 
import requests



url = 'https://www.youtube.com/watch?v=VD4fMgZmh5Q&t=190s'  en
url = 'https://www.youtube.com/watch?v=qKoPA3M7x2o&t=645s'  en-US


languages = ['en-US' 'en', 'en-orig', 'en-en-US', 'es-en-US']  # 'en-US',


ydl = yt_dlp.YoutubeDL(
    {'writesubtitles': True,
    'allsubtitles': True,
    'writeautomaticsub': True
    }
)
res = ydl.extract_info(url, download=False)



res['requested_subtitles'].keys()

for l in res['requested_subtitles']:
    print("Language: " + l)


url = ''
    
try:
    u = res['requested_subtitles']['en-Ux']['url'] 
except KeyError: 
    pass


# print("URL: " + u)




response = requests.get(
    u,
    stream=True
)


text = response.text
print(text)

language_order = ['en-US', 'en', 'en-orig', 'en-en-US', 'en-CA' 'es-en-US', 'es', 'fr', 'de', 'ru']
for language in language_order:
    print("LANGUAGE: " + language + " ________________________________")


jQuery('ab1ee88ea187b3c38e1ceff00be7b0db046f1d25b384abd9aeecef955b2e6839')

	    jQuery('#' + player_popup_id)[0].contentWindow.postMessage(
    			'{"event":"command","func":"' + 'pauseVideo' + '","args":""}', '*'
	    );


jQuery('player_ab1ee88ea187b3c38e1ceff00be7b0db046f1d25b384abd9aeecef955b2e6839')

jQuery('player_2c5c74cd1248cb565310570b7e69774386b78b054d0e036090ee811a518a80b4');

document.getElementById('player_2c5c74cd1248cb565310570b7e69774386b78b054d0e036090ee811a518a80b4').tagName;



javascript:closePopup('09dbbfec1935838594a487a928c96fe06625689a3430ce0b8bbb2c53481b0711');

var sha256 = '09dbbfec1935838594a487a928c96fe06625689a3430ce0b8bbb2c53481b0711';


if (jQuery(player_popup_id).prop('tagName') == 'IFRAME') {
    jQuery('#' + player_popup_id)[0].contentWindow.postMessage(
        '{"event":"command","func":"' + 'pauseVideo' + '","args":""}', '*'
    );
}


var sha256 = '09dbbfec1935838594a487a928c96fe06625689a3430ce0b8bbb2c53481b0711';
var hidden_popup_id = 'hidden_'+ sha256; 
var player_popup_id = 'player_' + sha256;

var div_id = hidden_popup_id;
var div = document.getElementById(div_id);

jQuery(player_popup_id).length 
jQuery(player_popup_id).attr('src')


is("IFRAME") ('tagName') == 'IFRAME') {

var x = document.getElementById("player_09dbbfec1935838594a487a928c96fe06625689a3430ce0b8bbb2c53481b0711");
var y = (x.contentWindow || x.contentDocument);
if (y.document)y = y.document;
y.body.style.backgroundColor = "red";


