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
import urllib
import Config
import pickle
import base64
import hashlib
import datetime
import requests
from bs4 import BeautifulSoup
from podgen import Podcast, Episode, Media

# User Agent MSIE 11.0 (Win 10)
headerdesktop = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; MATBJS; rv:11.0) like Gecko",
                 "Accept-Language": "it"}
timeoutconnection = 120
risorseaudioarray = []

rssfile = Config.outputpath + "necstpodcast.xml"


def load_analyzed_case():
    try:
        with open("necstpodcast_analyzed.txt", "rb") as fp:
            if fp:
                episodesList = pickle.load(fp)

        return episodesList

    except IOError as e:
        print(e)
        sys.exit()
    except Exception:
        return []


def save_analyzed_case(episodesList):
    try:
        with open("necstpodcast_analyzed.txt", "wb") as fp:
            pickle.dump(episodesList, fp)
    except IOError as e:
        print(e)
        sys.exit()
    except Exception as e:
        print(e)
        raise


def genero_feed(episodesList):
    if episodesList:
        # Creo un nuovo podcast
        p = Podcast()

        p.name = "NECST Tech Time"
        p.description = "Feed Podcast non ufficiale di NECST Tech Time - Powered By Andrea Draghetti"
        p.website = "http://www.poliradio.it/podcast/programmi/34/necst-tech-time"
        p.explicit = True
        p.image = "https://rss.draghetti.it/necst_image.jpg"
        p.feed_url = "https://rss.draghetti.it/necstpodcast.xml"
        p.copyright = "Poli Radio"
        p.language = "it-IT"

        for episodedetails in episodesList:
            episode = Episode()

            episode.title = episodedetails[1].encode("ascii", "ignore")
            episode.link = episodedetails[2].encode("ascii", "ignore")

            # La dimensione e statistica in base alle puntante analizzate
            episode.media = Media(episodedetails[3], 30000000, type="audio/x-m4a", duration=None)
            episode.publication_date = episodedetails[4]

            p.episodes.append(episode)

        # Print to stdout, just as an example
        p.rss_file(rssfile, minimize=False)


def main():
    # Ottengo la lista delle puntante gia analizzate
    episodesList = load_analyzed_case()

    # Estrapolo dalla lista appena ottenuta i soli Hash delle puntate precedenti
    episodesHash = []
    for episodes in episodesList:
        episodesHash.append(episodes[0])

    # Analizzo tutte le puntante pubblicate sul sito per individuarne di nuove
    urlmixcloud = "https://www.mixcloud.com/NECST_Tech_Time/"

    response = requests.get(urlmixcloud, headers=headerdesktop, timeout=timeoutconnection)
    soup = BeautifulSoup(response.text, "html.parser")

    for hgroup in soup.find_all("hgroup", attrs={"class": "card-title"}):

        episodeAudio = ""

        for h1 in hgroup.find_all("h1"):
            for link in h1.find_all("a", href=True):

                episodeLink = "https://www.mixcloud.com%s" % link["href"]
                episodeLinkHash = hashlib.sha1(episodeLink.encode("ascii", "ignore")).hexdigest()
                episodeTitle = link.find("span").get("title")

                if episodeLinkHash not in episodesHash:

                    # Ottengo l'URL della nuova risorsa audio
                    mixclouddownloader = "http://www.mixcloud-downloader.com/download/"
                    data = {"url": episodeLink}
                    response = requests.post(mixclouddownloader, data=data, headers=headerdesktop, timeout=timeoutconnection)
                    soup = BeautifulSoup(response.text, "html.parser")

                    for link in soup.find_all("a", href=True):
                        if "mixcloud.com" in link["href"]:
                            episodeAudio = link["href"]

                    # Aggiungo alla lista la nuova puntanta
                    if episodeAudio:
                        episodeDate = pytz.utc.localize(datetime.datetime.utcnow())
                        episodesList.insert(0, [episodeLinkHash, episodeTitle, episodeLink, episodeAudio, episodeDate])

    # Salvo la lista delle puntante
    save_analyzed_case(episodesList)

    # Genero il Feed XML
    genero_feed(episodesList)


if __name__ == "__main__":
    main()
