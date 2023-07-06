#from yt_dlp import YoutubeDL
import yt_dlp

# @click.argument('link')
# @click.option('-c', '--categories', is_flag=True, help="Pass True if you want to get the categories of this transcript back")
# @apis.command()

def transcribe_from_link(link, categories: bool):
 
 ydl_opts = {
    'format': 'bestaudio/best',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
    'ffmpeg-location': './',
    'outtmpl': "./%(id)s.%(ext)s",
 }
 
 headers_auth_only = {'authorization': auth_key}
 headers = {
    "authorization": auth_key,
    "content-type": "application/json"
 }
 CHUNK_SIZE = 5242880
  
 
   _id = link.strip()
   def get_vid(_id):
       with yt_dlp.YoutubeDL(ydl_opts) as ydl:
           return ydl.extract_info(_id)
   meta = get_vid(_id)
   save_location = meta['id'] + ".mp3"
   duration = meta['duration']
   print('Saved mp3 to', save_location)
   def read_file(filename):
       with open(filename, 'rb') as _file:
           while True:
               data = _file.read(CHUNK_SIZE)
               if not data:
                   break
               yield data
  
   upload_response = requests.post(
       upload_endpoint,
       headers=headers_auth_only, data=read_file(save_location)
   )
   audio_url = upload_response.json()['upload_url']
   print('Uploaded to', audio_url)
   transcript_request = {
       'audio_url': audio_url,
       'iab_categories': 'True' if categories else 'False',
   }
 
   transcript_response = requests.post(transcript_endpoint, json=transcript_request, headers=headers)
   transcript_id = transcript_response.json()['id']
   polling_endpoint = transcript_endpoint + "/" + transcript_id
   print("Transcribing at", polling_endpoint)
   polling_response = requests.get(polling_endpoint, headers=headers)
   while polling_response.json()['status'] != 'completed':
       sleep(30)
       try:
           polling_response = requests.get(polling_endpoint, headers=headers)
       except:
           print("Expected wait time:", duration*2/5, "seconds")
           print("After wait time is up, call poll with id", transcript_id)
           return transcript_id
   _filename = transcript_id + '.txt'
   with open(_filename, 'w') as f:
       f.write(polling_response.json()['text'])
   print('Transcript saved to', _filename)
   

link = 'https://youtube.com/watch?v=0COfz2JmQYA&feature=shares&t=2009'
cat = True
transcript = transcribe_from_link(link, True)