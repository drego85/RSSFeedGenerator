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
urlarticoliarray = []


def check_carola(url):
    try:
        pagedesktop = requests.get(url, headers=headerdesktop, timeout=timeoutconnection)
        soupdesktop = BeautifulSoup(pagedesktop.text, "html.parser")
        autore = soupdesktop.find("div", attrs={"style": "float:left"})
        if ("carola frediani" in str(autore.contents)) or ("frediani carola" in str(autore.contents)):
            return str(soupdesktop)
    except:
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


def scrap_home(url):
    pagedesktop = requests.get(url, headers=headerdesktop, timeout=timeoutconnection)
    soupdesktop = BeautifulSoup(pagedesktop.text, "html.parser")

    for div in soupdesktop.find_all("div", attrs={"class": "ls-box-titolo"}):
        for link in div.find_all("a", href=True):
            if link["href"].startswith(strftime("/%Y/%m")):
                urlarticoliarray.append("http://www.lastampa.it%s" % link["href"])


def scrap_rss(url):
    feed = feedparser.parse(url)
    for post in feed.entries:
        urlarticoliarray.append(post.link)


def main(argv):
    home_url = "http://www.lastampa.it"
    rss_url = "http://www.lastampa.it/rss.xml"

    # Acquisisco tutti gli URL degli articoli attraverso il Feed RSS del quotidiano
    scrap_rss(rss_url)

    # Acquisisco tutti gli URL degli articoli pubblicati in home, poiche il Feed RSS non contiene tutti gli articoli
    # pubblicati online ma solo i piu rilevanti
    scrap_home(home_url)

    # Se non esiste localmente un file XML procedo a crearlo.
    if os.path.exists(rssfile) is not True:
        make_feed()

    # Analizzo ogni singolo articolo rilevato
    for urlarticolo in urlarticoliarray:
        
        # Se l articolo appariene a carola la funzione check_carola mi restituisce il codice HTML della pagina che
        # sara utile per estrarre il titolo dell articolo e il relativo contenuto
        htmlscrap = check_carola(urlarticolo)

        if htmlscrap:
            print "Trovato articolo: " + urlarticolo
            title = Document(htmlscrap).short_title()
            description = Document(htmlscrap).summary()
            add_feed(title, description, urlarticolo)


if __name__ == "__main__":
    main(sys.argv[1:])
