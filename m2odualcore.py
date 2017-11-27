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
import Config
import requests
from lxml import etree as ET
from time import gmtime, strftime

# User Agent MSIE 11.0 (Win 10)
headerdesktop = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; MATBJS; rv:11.0) like Gecko",
                 "Accept-Language": "it"}

timeoutconnection = 120
rssfile = Config.outputpath + "m2odualcore.xml"
urlarticoliarray = []


def make_feed():
    root = ET.Element("rss")
    root.set("version", "2.0")

    channel = ET.SubElement(root, "channel")

    title = ET.SubElement(channel, "title")
    title.text = "M2O Dual Core RSS Feed"

    link = ET.SubElement(channel, "link")
    link.text = "https://rss.draghetti.it"

    description = ET.SubElement(channel, "description")
    description.text = "Feed RSS delle puntante di M2O Dual Core"

    language = ET.SubElement(channel, "language")
    language.text = "it-IT"

    generator = ET.SubElement(channel, "generator")
    generator.text = "M2O Dual Core Podcast by Andrea Draghetti"

    enclosure = ET.SubElement(channel, "itunes:image")
    enclosure.set("href", "https://upload.wikimedia.org/wikipedia/commons/a/ae/Logo-m2o-plain-nero.jpg")

    tree = ET.ElementTree(root)
    tree.write(rssfile, pretty_print=True, xml_declaration=True, encoding="UTF-8")


def add_feed(titlefeed, linkmp3):
    parser = ET.XMLParser(remove_blank_text=True)
    tree = ET.parse(rssfile, parser)
    channel = tree.getroot()

    # Escludo eventuali duplicati in base al link del mp3
    for i in channel.findall(".//link"):
        if (i.text == linkfeed):
            return

    item = ET.SubElement(channel, "item")

    title = ET.SubElement(item, "title")
    title.text = titlefeed

    link = ET.SubElement(item, "link")
    link.text = "https://www.m2o.it/programmi/dual-core/puntate/"

    description = ET.SubElement(item, "description")
    description.text = titlefeed

    enclosure = ET.SubElement(item, "enclosure")
    enclosure.set("url", linkmp3)
    enclosure.set("type", "audio/mpeg")

    pubDate = ET.SubElement(item, "pubDate")
    pubDate.text = strftime("%a, %d %b %Y %H:%M:%S +0000", gmtime())

    channel.find(".//generator").addnext(item)

    tree = ET.ElementTree(channel)
    tree.write(rssfile, pretty_print=True, xml_declaration=True, encoding="UTF-8")


def scrap_reloaded():
    try:

        url = "https://media.m2o.it/" + strftime("/%Y/%m/%d") + "/episodes/dualcore/dc_" + strftime(
            "%d") + "_novembre_ok.mp3"

        pagedesktop = requests.get(url, headers=headerdesktop, timeout=timeoutconnection)

        if pagedesktop.status_code == 200:
            return url
        else:

            url = "https://media.m2o.it/" + strftime("/%Y/%m/%d") + "/episodes/dualcore/dc_" + strftime(
                "%d") + "_novembre.mp3"

            pagedesktop = requests.get(url, headers=headerdesktop, timeout=timeoutconnection)

            if pagedesktop.status_code == 200:
                return url
            else:
                return ""

    except:
        pass


def main():
    # Controllo se la puntata odierna e stata pubblicata
    mp3url = scrap_reloaded()

    # Se non esiste localmente un file XML procedo a crearlo.
    if os.path.exists(rssfile) is not True:
        make_feed()

    if mp3url:
        add_feed("Dual Core del " + strftime("%d-%m-%Y"), mp3url)


if __name__ == "__main__":
    main()
