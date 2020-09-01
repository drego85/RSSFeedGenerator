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

headerdesktop = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:80.0) Gecko/20100101 Firefox/80.0",
                 "Accept-Language": "it,en-US;q=0.7,en;q=0.3"}

timeoutconnection = 120
rssfile = Config.outputpath + "carolafeed.xml"
articoliList = []


def make_feed():
    root = ET.Element("rss")
    root.set("version", "2.0")

    channel = ET.SubElement(root, "channel")

    title = ET.SubElement(channel, "title")
    title.text = "Carola Frediani RSS Feed"

    link = ET.SubElement(channel, "link")
    link.text = "https://rss.draghetti.it"

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
    description.text = descriptionfeed

    pubDate = ET.SubElement(item, "pubDate")
    pubDate.text = strftime("%a, %d %b %Y %H:%M:%S +0000", gmtime())

    channel.find(".//generator").addnext(item)

    tree = ET.ElementTree(channel)
    tree.write(rssfile, pretty_print=True, xml_declaration=True, encoding="UTF-8")


def scrap_tinyletter(url):
    pagedesktop = requests.get(url, headers=headerdesktop, timeout=timeoutconnection)
    soupdesktop = BeautifulSoup(pagedesktop.text, "html.parser")

    for div in soupdesktop.find_all("div", attrs={"class": "message-body"}):
        for link in div.find_all("a", attrs={"class": "message-link"}, href=True):
            articoliList.append(link["href"])


def scrap_substack(url):
    pagedesktop = requests.get(url, headers=headerdesktop, timeout=timeoutconnection)
    soupdesktop = BeautifulSoup(pagedesktop.text, "html.parser")

    for h1 in soupdesktop.find_all("h1", attrs={"class": "post-title"}):
        for link in h1.find_all("a", href=True):
            if link["href"].startswith("https://guerredirete.substack.com"):
                articoliList.append(link["href"])
            else:
                articoliList.append("https://guerredirete.substack.com" + link["href"])


def main():
    substack_url = "https://guerredirete.substack.com/?no_cover=true"

    # Acquisisco gli URL degli articolo su Substack
    scrap_substack(substack_url)

    # Se non esiste localmente un file XML procedo a crearlo.
    if os.path.exists(rssfile) is not True:
        make_feed()

    # Analizzo ogni singolo articolo rilevato
    for urlarticolo in articoliList:
        response = requests.get(urlarticolo, headers=headerdesktop, timeout=timeoutconnection)

        description = Document(response.text).summary()
        title = Document(response.text).short_title()

        add_feed(title, description, urlarticolo)


if __name__ == "__main__":
    main()
