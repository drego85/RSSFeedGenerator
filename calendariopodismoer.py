#!/usr/bin/python3
# -*- coding: utf-8 -*-
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

import os
import sys
import json
import Config
import requests
import hashlib

from lxml import etree as ET
from bs4 import BeautifulSoup
from time import gmtime, strftime

# User Agent MSIE 11.0 (Win 10)
headerdesktop = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; MATBJS; rv:11.0) like Gecko",
                 "Accept-Language": "it"}

timeoutconnection = 120
rssfile = Config.outputpath + "calendariopodismoer.xml"
eventianalyzedarray = []


def load_analyzed_case():
    try:
        f = open("calendariopodismoer_analyzed.txt", "r", errors="ignore")

        for line in f:
            if line:
                line = line.rstrip()
                eventianalyzedarray.append(line)

        f.close()

    except IOError as e:
        print(e)
        sys.exit()
    except Exception as e:
        print(e)
        raise


def save_analyzed_case(casehash):
    try:
        f = open("calendariopodismoer_analyzed.txt", "a")
        f.write(str(casehash) + "\n")
        f.close()
    except IOError as e:
        print(e)
        sys.exit()
    except Exception as e:
        print(e)
        raise


def make_feed():
    root = ET.Element("rss")
    root.set("version", "2.0")

    channel = ET.SubElement(root, "channel")

    title = ET.SubElement(channel, "title")
    title.text = "Calendario Podismo Emilia Romagna"

    link = ET.SubElement(channel, "link")
    link.text = "http://rss.draghetti.it"

    description = ET.SubElement(channel, "description")
    description.text = "Feed RSS di tutte le manifestazioni podistiche in Emilia Romagna tratte da calendaripodismo.it"

    language = ET.SubElement(channel, "language")
    language.text = "it-IT"

    generator = ET.SubElement(channel, "generator")
    generator.text = "RSS Feed Generator by Andrea Draghetti"

    tree = ET.ElementTree(root)
    tree.write(rssfile, pretty_print=True, xml_declaration=True, encoding="UTF-8")


def add_feed(titlefeed, luogo, data, descrizione, immagini, linkfeed):
    parser = ET.XMLParser(remove_blank_text=True)
    tree = ET.parse(rssfile, parser)
    channel = tree.getroot()

    # Escludo eventuali duplicati in base al link
    for i in channel.findall(".//link"):
        if (i.text == linkfeed):
            return

    item = ET.SubElement(channel, "item")

    title = ET.SubElement(item, "title")
    title.text = titlefeed + " " + luogo + " " + data

    link = ET.SubElement(item, "link")
    link.text = linkfeed

    description = ET.SubElement(item, "description")

    descriptionfeed = "<html> <body>" + descrizione + "<br> <br>"
    if immagini:
        for immagine in immagini:
            descriptionfeed += "<img src='" + immagine + "'> <br>"
    descriptionfeed += "</body> </html>"

    description.text = descriptionfeed

    pubDate = ET.SubElement(item, "pubDate")
    pubDate.text = strftime("%a, %d %b %Y %H:%M:%S +0000", gmtime())

    channel.find(".//generator").addnext(item)

    tree = ET.ElementTree(channel)
    tree.write(rssfile, pretty_print=True, xml_declaration=True, encoding="UTF-8")


def main():
    url = "https://www.calendariopodismo.it/api/Api/app/gare"

    headerdesktop = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; MATBJS; rv:11.0) like Gecko",
                     "Accept-Language": "it",
                     "Content-Type": "application/json"}

    # Carico casi gia analizzati
    load_analyzed_case()

    # Se non esiste localmente un file XML procedo a crearlo.
    if os.path.exists(rssfile) is not True:
        make_feed()

    # Ottengo la lista degli eventi pubblicati
    payload = '{"Regione": "3", "Provincia": "0", "Categoria": "0", "GiornoDa": "", "GiornoA": "", "from": 0, "limit": 0}'
    page = requests.post(url, headers=headerdesktop, timeout=timeoutconnection, data=payload)

    data = json.loads(page.text)

    if data:
        for each in data["data"]["gare"]:
            linkevento = "https://www.calendariopodismo.it/" + each["Progressivo"]
            title = each["NomeCorsa"]
            luogo = each["Luogo"]
            data = each["Giorno"]

            # Genero HASH che identifica univocamente l'evento in base al link
            casehash = hashlib.sha256(linkevento.encode()).hexdigest()

            if casehash not in eventianalyzedarray:
                url = "https://www.calendariopodismo.it/api/Api/app/gara/" + each["Progressivo"]

                page2 = requests.get(url, headers=headerdesktop, timeout=timeoutconnection)

                data2 = json.loads(page2.text)

                if data2:
                    descrizione = data2["data"]["gara"]["Dettaglio"]
                    immagini = data2["data"]["gara"]["listIMG"]
                else:
                    descrizione = ""
                    immagini = ""

                # Aggiungo l'evento al FEED
                add_feed(title, luogo, data, descrizione, immagini, linkevento)

                # Salvo il caso
                eventianalyzedarray.append(casehash)
                save_analyzed_case(casehash)


if __name__ == "__main__":
    main()
