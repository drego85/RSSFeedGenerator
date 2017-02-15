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
import os
import json
import Config
import requests
from lxml import etree as ET
from time import gmtime, strftime

# User Agent MSIE 11.0 (Win 10)
headerdesktop = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; MATBJS; rv:11.0) like Gecko",
                 "Accept-Language": "it"}

timeoutconnection = 120

rssfile = outputpath + "carolafeed.xml"


def make_feed():
    root = ET.Element("rss")
    root.set("version", "2.0")

    channel = ET.SubElement(root, "channel")

    title = ET.SubElement(channel, "title")
    title.text = "Carola Frediani RSS Feed"

    link = ET.SubElement(channel, "link")
    link.text = "http://rss.draghetti.it"

    description = ET.SubElement(channel, "description")
    description.text = "Feed RSS di tutti gli articoli scritti da Carola Frediani per La Stampa"

    language = ET.SubElement(channel, "language")
    language.text = "it-IT"

    generator = ET.SubElement(channel, "generator")
    generator.text = "CarolaFeed by Andrea Draghetti"

    tree = ET.ElementTree(root)
    tree.write(rssfile, pretty_print=True, xml_declaration=True, encoding="UTF-8")


def add_feed(titlefeed, descriptionfeed, linkfeed):
    parser = ET.XMLParser(remove_blank_text=True)
    tree = ET.parse(rssfile, parser)
    channel = tree.getroot()

    # Escludo eventuali duplicati in base al link
    for i in channel.findall(".//link"):
        if (i.text == linkfeed):
            return

    item = ET.SubElement(channel, "item")

    title = ET.SubElement(item, "title")
    title.text = titlefeed

    link = ET.SubElement(item, "link")
    link.text = linkfeed

    description = ET.SubElement(item, "description")
    description.text = descriptionfeed[0:500]

    pubDate = ET.SubElement(item, "pubDate")
    pubDate.text = strftime("%a, %d %b %Y %H:%M:%S +0000", gmtime())

    channel.find(".//generator").addnext(item)
    tree = ET.ElementTree(channel)

    tree.write(rssfile, pretty_print=True, xml_declaration=True, encoding="UTF-8")


def mercuryparser(url):
    mercury = "https://mercury.postlight.com/parser?url="

    page = requests.get(mercury + url, headers=Config.headermercury, timeout=timeoutconnection)
    page.encoding = "UTF-8"
    data = json.loads(page.text)

    return data["title"], data["content"]


def main():
    urlarticolo = "http://www.lastampa.it/2017/02/10/tecnologia/news/ecco-la-app-per-scoprire-se-la-tua-connessione-censurata-o-rallentata-p66YhNjnq1mdDZQum7lfgM/pagina.html"

    # Se non esiste il feed XML lo creo
    if os.path.exists(rssfile) is not True:
        make_feed()

    title, description = mercuryparser(urlarticolo)
    add_feed(title, description, urlarticolo)


if __name__ == "__main__":
    main()
