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
from urllib.parse import parse_qs, urlencode, urljoin, urlparse, urlunparse

header_desktop = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:80.0) Gecko/20100101 Firefox/80.0",
                 "Accept-Language": "it,en-US;q=0.7,en;q=0.3"}

timeoutconnection = 120
rssfile = Config.outputpath + "ilpost.xml"


def normalize_article_url(url):
    parsed = urlparse(url)
    query_params = parse_qs(parsed.query, keep_blank_values=True)
    query_params.pop("homepagePosition", None)
    normalized_query = urlencode(query_params, doseq=True)

    return urlunparse(
        (
            parsed.scheme,
            parsed.netloc,
            parsed.path,
            parsed.params,
            normalized_query,
            "",
        )
    )

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
    linkfeed = normalize_article_url(linkfeed)

    parser = ET.XMLParser(remove_blank_text=True)
    tree = ET.parse(rssfile, parser)
    root = tree.getroot()
    channel = root.find("channel")

    # Escludo eventuali duplicati in base al link
    for i in channel.findall(".//link"):
        if (i.text == linkfeed):
            return

    # Mantieni al massimo 20 item: se già presenti, elimina il più vecchio
    items = channel.findall("item")
    if len(items) >= 20:
        channel.remove(items[-1])

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

    tree = ET.ElementTree(root)
    tree.write(rssfile, pretty_print=True, xml_declaration=True, encoding="UTF-8")


def scrap_ilpost(url):
    pagedesktop = requests.get(url, headers=header_desktop, timeout=timeoutconnection)
    soup = BeautifulSoup(pagedesktop.text, "html.parser")

    article_by_position = {}

    for anchor in soup.select('a[href*="homepagePosition="]'):
        href = anchor.get("href")
        if not href:
            continue

        absolute_url = urljoin(url, href)
        parsed_url = urlparse(absolute_url)
        homepage_position = parse_qs(parsed_url.query).get("homepagePosition", [None])[0]

        if homepage_position is None or not homepage_position.isdigit():
            continue

        if parsed_url.path.startswith("/episodes/"):
            continue

        if homepage_position not in article_by_position:
            article_by_position[homepage_position] = normalize_article_url(absolute_url)

    return [
        article_by_position[position]
        for position in sorted(article_by_position, key=int)[:4]
    ]

def main():
    url = "https://www.ilpost.it/"

    # Acquisisco l'articolo principale
    list_of_articles = scrap_ilpost(url)

    print(list_of_articles)

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
