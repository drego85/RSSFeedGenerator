#!/usr/bin/env python3
# This file is part of RSS Generator Feed.
#
# RSS Feed Generator was made with ♥ by Andrea Draghetti
#
# This file may be licensed under the terms of of the
# GNU General Public License Version 3 (the ``GPL'').
#
import os
import Config
import requests
from lxml import etree as ET
from bs4 import BeautifulSoup
from readability import Document
from time import gmtime, strftime

header_desktop = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:80.0) Gecko/20100101 Firefox/80.0",
                 "Accept-Language": "it,en-US;q=0.7,en;q=0.3"}

timeoutconnection = 120
rssfile = Config.outputpath + "ilpost.xml"
list_of_articles = []


def make_feed():
    root = ET.Element("rss")
    root.set("version", "2.0")

    

    channel = ET.SubElement(root, "channel")

    title = ET.SubElement(channel, "title")
    title.text = "Il Post RSS Feed - Articoli Principali"

    link = ET.SubElement(channel, "link")
    link.text = "http://rss.draghetti.it"

    description = ET.SubElement(channel, "description")
    description.text = "RSS feed degli articoli principali pubblicati Il Post"

    language = ET.SubElement(channel, "language")
    language.text = "it-IT"

    generator = ET.SubElement(channel, "generator")
    generator.text = "Il Post by Andrea Draghetti"

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


def scrap_ilpost(url):
    pagedesktop = requests.get(url, headers=header_desktop, timeout=timeoutconnection)
    soupdesktop = BeautifulSoup(pagedesktop.text, "html.parser")

    # Ottengo i primi due articoli di rielivo
    article = 2

    for div in soupdesktop.find_all("div", attrs={"class": ["index_col-apertura__IK1DC", "_article-content_1jdu8_20", "_article-content_1n08y_20"]}):
        if article > 0:
            article_url = div.find("a")["href"]
            # remove any GET parameters
            article_url = article_url.split("?")[0]
            list_of_articles.append(article_url)
            article -= 1

def main():
    url = "https://www.ilpost.it/"

    # Acquisisco l'articolo principale
    scrap_ilpost(url)

    # Se non esiste localmente un file XML procedo a crearlo.
    if os.path.exists(rssfile) is not True:
        make_feed()

    # Analizzo ogni singolo articolo rilevato
    for urlarticolo in list_of_articles:
        response = requests.get(urlarticolo, headers=header_desktop, timeout=timeoutconnection)

        description = Document(response.text).summary()
        title = Document(response.text).short_title()

        add_feed(title, description, urlarticolo)


if __name__ == "__main__":
    main()
