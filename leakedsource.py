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
rssfile = "./public_html/leakedsource.xml"
urlarticlesarray = []


def check_article(url):
    try:
        pagedesktop = requests.get(url, headers=headerdesktop, timeout=timeoutconnection)
        soupdesktop = BeautifulSoup(pagedesktop.text, "html.parser")
        return str(soupdesktop)
    except:
        pass


def make_feed():
    root = ET.Element("rss")
    root.set("version", "2.0")

    channel = ET.SubElement(root, "channel")

    title = ET.SubElement(channel, "title")
    title.text = "Leakedsource RSS Feed"

    link = ET.SubElement(channel, "link")
    link.text = "https://rss.draghetti.it"

    description = ET.SubElement(channel, "description")
    description.text = "Feed RSS for LeakedSource Blog"

    language = ET.SubElement(channel, "language")
    language.text = "it-IT"

    generator = ET.SubElement(channel, "generator")
    generator.text = "LeakedsourceFeed by Andrea Draghetti - https://github.com/drego85/LeakedSourceFeed"

    tree = ET.ElementTree(root)
    tree.write(rssfile, pretty_print=True, xml_declaration=True)


def add_feed(titlefeed, descriptionfeed, linkfeed):
    parser = ET.XMLParser(remove_blank_text=True)
    tree = ET.parse(rssfile, parser)
    channel = tree.getroot()

    # Ruled out any duplicates based on links
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

    for li in soupdesktop.find_all("li", attrs={"style": "margin-top: 5px;"}):
        for link in li.find_all("a", href=True):
            if link["href"].startswith(strftime("https://www.leakedsource.com/blog/")):
                urlarticlesarray.append(link["href"])

def scrap_rss(url):
    feed = feedparser.parse(url)
    for post in feed.entries:
        urlarticoliarray.append(post.link)


def main(argv):
    blog_url = "https://www.leakedsource.com/blog/"

    # Acquire all articles published in the blog
    scrap_home(blog_url)

    # If an XML file does not exist locally proceed to create it.
    if os.path.exists(rssfile) is not True:
        make_feed()

    # Analyze every single article
    for urlarticle in urlarticlesarray:

        htmlscrap = check_article(urlarticle)

        if htmlscrap:
            print "New article: " + urlarticle

            title = Document(htmlscrap).short_title()
            description = Document(htmlscrap).summary()
            add_feed(title, description, urlarticle)


if __name__ == "__main__":
    main(sys.argv[1:])
