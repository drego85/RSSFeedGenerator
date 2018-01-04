#!/usr/bin/python
# This file is part of RSS Generator Feed.
#
# Copyright(c) 2017 Andrea Draghetti
# https://www.andreadraghetti.it
#
# This file may be licensed under the terms of of the
# GNU General Public License Version 3 (the ``GPL'').
#
# Software distributed under the License is distributed
# on an ``AS IS'' basis, WITHOUT WARRANTY OF ANY KIND, either
# express or implied. See the GPL for the specific language
# governing rights and limitations.
#
# You should have received a copy of the GPL along with this
# program. If not, go to http://www.gnu.org/licenses/gpl.html
# or write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.

import sys
import pytz
import Config
import base64
import datetime
import requests
from bs4 import BeautifulSoup
from podgen import Podcast, Episode, Media

# User Agent MSIE 11.0 (Win 10)
headerdesktop = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; MATBJS; rv:11.0) like Gecko",
                 "Accept-Language": "it"}
timeoutconnection = 120

puntatearray = []
risorseaudioarray = []

rssfile = Config.outputpath + "pascal.xml"


def load_analyzed_case():
    try:
        with open("pascal_analyzed.txt", "r") as f:
            for line in f:
                if line[-1] == "\n":
                    if line != "\n":
                        puntatearray.append(line[:-1])
                else:
                    if line != "":
                        puntatearray.append(line)
    except IOError as e:
        print "I/O error on read Keywords File({0}): {1}".format(e.errno, e.strerror)
        sys.exit()
    except Exception as e:
        print str(e)
        print "Unexpected error on read Keywords File:", sys.exc_info()[0]
        raise


def save_analyzed_case(casehash):
    try:
        with open("pascal_analyzed.txt", "r+") as f:
            file_data = f.read()
            f.seek(0, 0)
            f.write(casehash + "\n" + file_data)

    except IOError as e:
        print "I/O error on write Last Analyzed File({0}): {1}".format(e.errno, e.strerror)
    except:
        print "Unexpected error on write Last Analyzed File:", sys.exc_info()[0]
        raise


def load_puntate(url):
    response = requests.post(url, headers=headerdesktop, timeout=timeoutconnection)
    soup = BeautifulSoup(response.text, "html.parser")

    nuovapuntata = False

    for div in soup.find_all("div", attrs={"class": "columns large-4 medium-6 small-6 bloccoPlaylist containerOption"}):
        for div2 in div.find_all("div", attrs={"class": "programItemPlaylist"}):
            titolo = data = ""

            risorsaaudio = div2.get("data-mediapolis")
            risorsaaudiob64 = base64.b64encode(div2.get("data-mediapolis"))

            if risorsaaudiob64 not in risorseaudioarray:

                # Ottengo l'URL del MP3
                response = requests.post(risorsaaudio, headers=headerdesktop, timeout=timeoutconnection)

                linkmp3 = base64.b64encode(response.url)

                for title in div.find_all("h3"):
                    titolo = base64.b64encode(title.text.encode("ascii", "ignore"))

                for date in div.find_all("span", attrs={"class": "canale"}):
                    data = base64.b64encode(date.text.encode("ascii", "ignore"))

                nuovapuntata = True
                puntatearray.insert(0, titolo + "|" + data + "|" + linkmp3 + "|" + risorsaaudiob64)
                save_analyzed_case(titolo + "|" + data + "|" + linkmp3 + "|" + risorsaaudiob64)

    return nuovapuntata


def main():
    # URL riepilogativo delle puntate di pascal
    url = "http://www.raiplayradio.it/programmi/pascal/archivio/puntate/"

    # Carico le puntate gia analizzate
    load_analyzed_case()

    # Splitto l'array per creare l'array con i soli mp3
    for data in puntatearray:
        if data:
            risorseaudioarray.append(data.split("|")[3])

    # Verifico se vi sono nuove puntate
    nuovapuntata = load_puntate(url)

    # Se e stata rilevata una nuova puntata rigenero il feed
    if nuovapuntata:

        # Creo un nuovo podcast
        p = Podcast()

        p.name = "Pascal Rai Radio 2"
        p.description = "Pascal un programma di Matteo Caccia in onda su Radio2 che racconta storie di vita. Episodi grandi o piccoli, stravolgenti o minuti, momenti che hanno modificato per sempre la nostra vita o che, anche se di poco, l'hanno indirizzata. Storie che sono il termometro della temperatura di ognuno di noi e che in parte raccontano chi siamo. "
        p.website = "http://www.raiplayradio.it/programmi/pascal/"
        p.explicit = True
        p.image = "https://rss.draghetti.it/pascal_image.jpg"
        p.feed_url = "https://rss.draghetti.it/pascal.xml"
        p.copyright = "Rai Radio 2"
        p.language = "it-IT"

        for data in puntatearray:
            episode = Episode()

            episode.title = base64.b64decode(data.split("|")[0])

            # La dimensione del file e approssimativa
            episode.media = Media(base64.b64decode(data.split("|")[2]), 56722176)
            episode.publication_date = datetime.datetime(int(base64.b64decode(data.split("|")[1]).split("/")[2]),
                                                         int(base64.b64decode(data.split("|")[1]).split("/")[1]),
                                                         int(base64.b64decode(data.split("|")[1]).split("/")[0]), 02,
                                                         00, tzinfo=pytz.utc)
            p.episodes.append(episode)

        # Print to stdout, just as an example
        p.rss_file(rssfile, minimize=False)


if __name__ == "__main__":
    main()
