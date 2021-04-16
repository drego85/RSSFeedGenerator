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
rssfile = Config.outputpath + "autosprint.xml"
list_of_articles = []


def make_feed():
    root = ET.Element("rss")
    root.set("version", "2.0")

    channel = ET.SubElement(root, "channel")

    title = ET.SubElement(channel, "title")
    title.text = "Autosprint RSS Feed - Articoli Principali Formula 1"

    link = ET.SubElement(channel, "link")
    link.text = "http://rss.draghetti.it"

    description = ET.SubElement(channel, "description")
    description.text = "RSS feed degli articoli principali sulla Formula 1 pubblicati da Autosprint"

    language = ET.SubElement(channel, "language")
    language.text = "en-EN"

    generator = ET.SubElement(channel, "generator")
    generator.text = "Autosprint.it by Andrea Draghetti"

    tree = ET.ElementTree(root)
    tree.write(rssfile, pretty_print=True, xml_declaration=True, encoding="UTF-8")


def add_feed(titlefeed, descriptionfeed, linkfeed):
    parser = ET.XMLParser(remove_blank_text=True)
    tree = ET.parse(rssfile, parser)
    channel = tree.getroot()

    # Exclude duplicated articles
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


def scrap_autosprint(url):
    pagedesktop = requests.get(url, headers=header_desktop, timeout=timeoutconnection)
    soupdesktop = BeautifulSoup(pagedesktop.text, "html.parser")

    articolo = soupdesktop.find("div", attrs={"class": "main-article"}).find("h1", attrs={"class": "title"}).find("a", href=True)
    list_of_articles.append(articolo["href"])


def main():
    url = "https://autosprint.corrieredellosport.it/formula1/"

    # I get all the URLs of the articles written by the author
    scrap_autosprint(url)

    # If doesn't exist local XML file, I generate it
    if os.path.exists(rssfile) is not True:
        make_feed()

    # I analyze each articles found
    for urlarticolo in list_of_articles:
        response = requests.get(urlarticolo, headers=header_desktop, timeout=timeoutconnection)

        description = Document(response.text).summary()
        title = Document(response.text).short_title()

        add_feed(title, description, urlarticolo)


if __name__ == "__main__":
    main()
