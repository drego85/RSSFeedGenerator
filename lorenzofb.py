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

# User Agent MSIE 11.0 (Win 10)
headerdesktop = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; MATBJS; rv:11.0) like Gecko",
                 "Accept-Language": "it"}

timeoutconnection = 120
rssfile = Config.outputpath + "lorenzofb.xml"
articoliList = []


def make_feed():
    root = ET.Element("rss")
    root.set("version", "2.0")

    channel = ET.SubElement(root, "channel")

    title = ET.SubElement(channel, "title")
    title.text = "Lorenzo Franceschi-Bicchierai RSS Feed"

    link = ET.SubElement(channel, "link")
    link.text = "http://rss.draghetti.it"

    description = ET.SubElement(channel, "description")
    description.text = "RSS feed of all articles written by Lorenzo Franceschi-Bicchierai for Vice"

    language = ET.SubElement(channel, "language")
    language.text = "en-EN"

    generator = ET.SubElement(channel, "generator")
    generator.text = "Lorenzo Franceschi-Bicchierai by Andrea Draghetti"

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


def scrap_vice(url):
    pagedesktop = requests.get(url, headers=headerdesktop, timeout=timeoutconnection)
    soupdesktop = BeautifulSoup(pagedesktop.text, "html.parser")

    for div in soupdesktop.find_all("div", attrs={"class": "pager-wrapper"}):
        for link in div.find_all("a", href=True):
            articoliList.append("https://www.vice.com" + link["href"])


def main():
    url = "https://www.vice.com/it/contributor/lorenzo-franceschi-bicchierai"

    # I get all the URLs of the articles written by the author
    scrap_vice(url)

    url = "https://www.vice.com/en_us/contributor/lorenzo-franceschi-bicchierai"

    # I get all the URLs of the articles written by the author
    scrap_vice(url)

    # If doesn't exist local XML file, I generate it
    if os.path.exists(rssfile) is not True:
        make_feed()

    # I analyze each articles found
    for urlarticolo in articoliList:
        response = requests.get(urlarticolo, headers=headerdesktop, timeout=timeoutconnection)

        description = Document(response.text).summary()
        title = Document(response.text).short_title()

        add_feed(title, description, urlarticolo)


if __name__ == "__main__":
    main()
