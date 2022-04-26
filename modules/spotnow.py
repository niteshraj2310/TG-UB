from io import BytesIO
from PIL import Image, ImageFont, ImageDraw
from urllib.request import urlopen
import spotipy
import spotipy.util as util

username = "Jeel Patel"
# set SPOTIPY_CLIENT_SECRET & SPOTIPY_CLIENT_ID
token = util.prompt_for_user_token(username, 'user-read-currently-playing', redirect_uri="http://localhost:8000/callback")
spotify = spotipy.Spotify(auth=token)

# https://stackoverflow.com/a/66999827 # caching font in memory 
bold_url = 'https://github.com/googlefonts/roboto/blob/main/src/hinted/Roboto-Bold.ttf?raw=true'
regular_url = 'https://github.com/googlefonts/roboto/blob/main/src/hinted/Roboto-Regular.ttf?raw=true'
font_24 = ImageFont.truetype(urlopen(bold_url), size=25)
font_20 = ImageFont.truetype(urlopen(regular_url), size=20)

def get_details() -> tuple:
    current_track = spotify.current_user_playing_track()
    complete_percent = current_track["progress_ms"]/current_track["item"]["duration_ms"]
    current_track = current_track["item"]
    song_name = current_track["name"]
    artists = ", ".join([artist["name"] for artist in current_track["artists"]])
    album_name = current_track["album"]["name"]
    track_id = current_track["id"] # unique song identifier
    image = current_track["album"]["images"][1]["url"]
    link = current_track["external_urls"]["spotify"]
    return (song_name,artists,album_name,image,link,complete_percent,track_id)

def make_image(data,username) -> BytesIO:
    canvas = Image.new('RGB', (600,250))
    draw = ImageDraw.Draw(canvas)

    album_art = Image.open(urlopen(data[3])) # 300px image
    album_art = album_art.resize((round(album_art.size[0]*0.65), round(album_art.size[1]*0.65))) # resize to 200px
    canvas.paste(album_art, (25,25)) # paste at 25,25

    # Write text
    draw.text((240, 25), f"{username} is listening to", font=font_24, fill=(255,255,255))
    draw.text((240, 100), data[0], font=font_24, fill=(255,255,255))
    draw.text((240, 138), data[1], font=font_20, fill=(255,255,255))
    draw.text((240, 170), data[2], font=font_20, fill=(255,255,255))

    # draw completion line
    draw.line([(240,210),(540,210)],fill="grey",width=4)
    draw.line([(240,210),(240+(300*data[5]),210)],fill="white",width=4)

    file_bytes = BytesIO()
    canvas.save(file_bytes,format="png")

    return file_bytes

def spotnow(_,message):
    data = get_details()
    file = make_image(data,message.from_user.username)
    message.reply_photo(file,caption=f"[HERE]({data[4]})",quote=True)