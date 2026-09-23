#silkpuller
#pulls lyrics from lrclib according to song files you have
#a python learning project
import requests
from pathlib import Path
from mutagen import File
import time
import os
import sys

#getting all the variables ready
replace = "false"
artists = 0
albums = 0
songs = 0
missing = 0
found = 0
timeout = 0
skipped = 0
replaced = 0
username = os.environ["USER"]

#check if running as root, if so then quit script
if username == "root":
    print("please do not run silkpuller as root")
    sys.exit(1)

#info and grabbing user options
print("make sure your music has the right metadata")
print("(artist, title, and album)")
print("folder structure must be artist>album>song")
print("what directory would you like to check?")
directory = input("~/")

pppp = input("replace pre-existing lyrics? (y/N) ")

#to replace or not to replace, that is the question
if pppp in ["y", "Y"]:
    replace = "true"
    answer = "will replace duplicate files"
elif pppp in ["n", "N"]:
    replace = "false"
    answer = "will not replace duplicate files"
else:
    answer = "defaulting to no replacing"
print(f"{answer}, ctrl+c in the next 5 seconds to cancel")
for i in range(1, 6):
    time.sleep(1)
    print(i)
print("continuing")
time.sleep(1)

#start of like the real thing I think
music_dir = Path(f"/home/{username}/{directory}")
for artist in music_dir.iterdir():
    artists += 1
    for folder in artist.iterdir():
        print(f"checking -- {artist.name} - {folder.name}")
        albums += 1
        time.sleep(.6)
        music2_dir = folder
        for file in sorted(music2_dir.iterdir()):
            #filters for only these filetypes
            if file.suffix in [".flac", ".mp3"]:
                songs += 1
                #metadata and stuff
                audio = File(file)
                title = audio['title'][0]
                track_artist = audio['artist'][0]
                album = audio['album'][0]
                duration = round(audio.info.length)
                #the lrclib docs said I needed a header
                headers = {"User-Agent": "silkpuller v0.2.0 https://github.com/silkerds/silkpuller"}
                #if no lyrics, or if lyrics but replace is on
                if file.with_suffix(".lrc") not in folder.iterdir() or file.with_suffix(".lrc") in folder.iterdir() and replace == "true":
                    if file.with_suffix(".lrc") not in folder.iterdir():
                        roger = "lyrics found"
                        whatdidido = "nonexisting"
                    elif file.with_suffix(".lrc") in folder.iterdir() and replace == "true":
                        roger = "replacing current lyrics"
                        whatdidido = "replace"
                    #does the request
                    status = (requests.get(
                        url='https://lrclib.net/api/get',
                        headers=headers, 
                        params={
                            'track_name': title,
                            'artist_name': track_artist,
                            'album_name': album, 
                            'duration': duration}))
                    #handles rate limits
                    while status.status_code == 429:
                        timeout += 1
                        time.sleep(int(status.headers["Retry-After"]))
                        status = (requests.get(
                            url='https://lrclib.net/api/get',
                            headers=headers, 
                            params={
                                'track_name': title,
                                'artist_name': track_artist,
                                'album_name': album, 
                                'duration': duration}))
                    #self explanatory
                    if status.status_code == 404:
                        roger = ("no lyrics found")
                        missing += 1
                    #writes the lyrics if they are found
                    elif status.status_code == 200:
                        data = status.json()
                        with open(file.with_suffix(".lrc"), "w") as f:
                            f.write(data["syncedLyrics"])
                        #if and elif decide what count to raise
                        if whatdidido == "nonexisting":
                            found += 1
                        elif whatdidido == "replace":
                            replaced += 1
                    #idk, crude way to handle unknown error codes
                    elif status.status_code not in [200, 404, 429]:
                        print("unknown error code, cancelling script")
                        sys.exit(1)
                #if replace is off it skips
                elif file.with_suffix(".lrc") in folder.iterdir() and replace == "false":
                    roger = ("lyrics already exist")
                    skipped += 1
                #results and waits as to not get rate limited
                print(f"{file.name} -- {roger}")
                time.sleep(.25)

#end stuff cuz why not
print("------------End Statistics.------------")
if artists != 0:
    print(f"artists checked -- {artists}")
    if albums != 0:
        print(f"albums checked -- {albums}")
        if songs != 0:
            print(f"songs checked -- {songs}")
            if found != 0:
                print(f"    found lyrics -- {found}")
            if replaced != 0:
                print(f"    replaced lyrics -- {replaced}")
            if skipped != 0:
                print(f"    skipped lyrics -- {skipped}")
            if missing != 0:
                print(f"    missing lyrics -- {missing}")
        else:
            print("no songs checked, are you using the right layout?")
else:
    print("no artists checked, are you using the right layout?")
print("----Thank you for using silkpuller!----")
sys.exit(0)
