#!/usr/bin/python2
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
        with open("calendariopodismoer_analyzed.txt", "r") as f:
            for line in f:
                if line[-1] == "\n":
                    if line != "\n":
                        eventianalyzedarray.append(line[:-1])
                else:
                    if line != "":
                        eventianalyzedarray.append(line)
    except IOError as e:
        print "I/O error on read Keywords File({0}): {1}".format(e.errno, e.strerror)
        sys.exit()
    except Exception as e:
        print str(e)
        print "Unexpected error on read Keywords File:", sys.exc_info()[0]
        raise


def save_analyzed_case(casehash):
    try:
        f = open("calendariopodismoer_analyzed.txt", "a")
        f.write(casehash + "\n")
        f.close()
    except IOError as e:
        print "I/O error on write Last Analyzed File({0}): {1}".format(e.errno, e.strerror)
    except:
        print "Unexpected error on write Last Analyzed File:", sys.exc_info()[0]
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
    description.text = descriptionfeed

    pubDate = ET.SubElement(item, "pubDate")
    pubDate.text = strftime("%a, %d %b %Y %H:%M:%S +0000", gmtime())

    channel.find(".//generator").addnext(item)

    tree = ET.ElementTree(channel)
    tree.write(rssfile, pretty_print=True, xml_declaration=True, encoding="UTF-8")


def main():
    url = "http://www.calendariopodismo.it/index.php?dove=3&regoprov=regione&tipogara=0"

    # Carico casi gia analizzati
    load_analyzed_case()

    # Se non esiste localmente un file XML procedo a crearlo.
    if os.path.exists(rssfile) is not True:
        make_feed()

    # Ottengo la lista degli eventi pubblicati

    pagedesktop = requests.get(url, headers=headerdesktop, timeout=timeoutconnection)
    soup = BeautifulSoup(pagedesktop.text, "html.parser")

    for table in soup.find_all("table", attrs={"class": "tab"}):

        for idx, row in enumerate(table.findAll("tr", onclick=True)):

            cells = row.findAll("td")
            title = cells[2].find(text=True).encode("ascii", "ignore") + " - " + cells[1].find(text=True).encode(
                "ascii", "ignore")

            linkevento = row["onclick"]
            linkevento = linkevento.replace("javascript:document.location='", "")
            linkevento = linkevento.replace("';", "")
            linkevento = "https://www.calendariopodismo.it/" + linkevento

            # Genero HASH che identifica univocamente l'evento in base al link
            casehash = hashlib.sha256(linkevento).hexdigest()

            if casehash not in eventianalyzedarray:

                # Ottengo la descrizione dell'evento
                pagedesktop = requests.get(linkevento, headers=headerdesktop, timeout=timeoutconnection)
                soup = BeautifulSoup(pagedesktop.text, "html.parser")

                description = ""

                for idx, table2 in enumerate(soup.find_all("table", attrs={"align": "center"})):

                    # La prima e la seconda tabella non ci interessano le salto e proseguo
                    if idx == 0 or idx == 1:
                        continue

                    for idx, row in enumerate(table2.findAll("tr")):

                        # Le celle che non ci interessano le salto e proseguo
                        if idx == 2 or idx == 3 or idx == 4 or idx == 6 or idx == 7:
                            continue

                        description = description + str(row)

                    try:
                        description = description.replace("src=\"", "align=\"center\" src=\"https://www.calendariopodismo.it/")
                    except:
                        pass

                description = "<table align=\"center\">" + description + "</table>"

                description = description.decode("ascii", "ignore")

                # Aggiungo l'evento al FEED
                add_feed(title, description, linkevento)

                # Salvo il caso
                eventianalyzedarray.append(casehash)
                save_analyzed_case(casehash)


if __name__ == "__main__":
    main()
