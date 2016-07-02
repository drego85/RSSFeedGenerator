#!/usr/bin/python
import sys, os
import requests
import re
# pip install bs4
from bs4 import BeautifulSoup
# pip install feedparser
import feedparser
# pip install readability-lxml
from readability.readability import Document

from lxml import etree as ET
from time import gmtime, strftime

# User Agent MSIE 11.0 (Win 10)
headerdesktop = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; MATBJS; rv:11.0) like Gecko",
                 "Accept-Language": "it"}
timeoutconnection = 10
rssfile = "carolafeed.xml"


def get_html(url):
    try:
        pagedesktop = requests.get(url, headers=headerdesktop, timeout=timeoutconnection)
        soupdesktop = BeautifulSoup(pagedesktop.text, "html.parser")
        return str(soupdesktop)
    except:
        return ""
        pass


def check_carola(url):
    try:
        pagedesktop = requests.get(url, headers=headerdesktop, timeout=timeoutconnection)
        soupdesktop = BeautifulSoup(pagedesktop.text, "html.parser")
        test = soupdesktop.find("div", attrs={"style": "float:left"})
        if ("carola frediani" in str(test.contents)) or ("frediani carola" in str(test.contents)):
            return True
    except:
        return ""
        pass


def make_feed():
    root = ET.Element("rss")
    root.set("version", "2.0")

    channel = ET.SubElement(root, "channel")

    title = ET.SubElement(channel, "title")
    title.text = "Carola Frediani RSS Feed"

    link = ET.SubElement(channel, "link")
    link.text = "http://carola.draghetti.it"

    description = ET.SubElement(channel, "description")
    description.text = "Feed RSS di tutti gli articoli scritti da Carola Frediani per La Stampa"

    language = ET.SubElement(channel, "language")
    language.text = "it-IT"

    generator = ET.SubElement(channel, "generator")
    generator.text = "CarolaFeed by Andrea Draghetti - https://github.com/drego85/CarolaFeed"

    tree = ET.ElementTree(root)
    tree.write(rssfile, pretty_print=True, xml_declaration=True)


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
    description.text = descriptionfeed[0:400]

    pubDate = ET.SubElement(item, "pubDate")
    pubDate.text = strftime("%a, %d %b %Y %H:%M:%S +0000", gmtime())

    channel.find(".//generator").addnext(item)
    # print ET.tostring(channel, pretty_print=True, xml_declaration=True)
    tree = ET.ElementTree(channel)
    tree.write(rssfile, pretty_print=True, xml_declaration=True)


def main(argv):
    rss_url = "http://www.lastampa.it/rss.xml"
    feed = feedparser.parse(rss_url)

    # Se non esiste un file XML procedo a crearlo.
    if os.path.exists(rssfile) is not True:
        make_feed()

    for post in feed.entries:

        url = post.link

        if check_carola(url):
            print "Trovato articolo: " + url
            htmlscrap = get_html(url)
            description = Document(htmlscrap).summary()
            title = Document(htmlscrap).short_title()
            add_feed(title, description, post.link)


if __name__ == "__main__":
    main(sys.argv[1:])
