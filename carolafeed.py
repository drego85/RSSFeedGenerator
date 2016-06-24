#!/usr/bin/python
import sys, os
import requests
import re
#pin install bs4
from bs4 import BeautifulSoup
#pin install feedparser
import feedparser
#pin install readability-lxml
from readability.readability import Document

from lxml import etree as ET
from time import gmtime, strftime

#User Agent MSIE 11.0 (Win 10)
headerdesktop = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; MATBJS; rv:11.0) like Gecko", "Accept-Language": "it"}
timeoutconnection = 10
keywordsarray = ["<p class=\"article-author\">carola frediani</p>", "<p class=\"article-author\">frediani carola</p>"]
rssfile = "carolafeed.xml"

def get_phishedhtml(url):
	try:
		pagedesktop = requests.get(url, headers=headerdesktop, timeout=timeoutconnection)
		soupdesktop = BeautifulSoup(pagedesktop.text, "html.parser")
		return str(soupdesktop)
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
	
	#Escludo eventuali duplicati in base al link
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
	pubDate.text = strftime("%a, %d %b %Y +0000", gmtime())
	
	channel.find(".//generator").addnext(item)
	#print ET.tostring(channel, pretty_print=True, xml_declaration=True)
	tree = ET.ElementTree(channel)
	tree.write(rssfile, pretty_print=True, xml_declaration=True)
	
def main(argv):
	rss_url = "http://www.lastampa.it/rss.xml"
	feed = feedparser.parse(rss_url)
	
	#Se non esiste un file XML procedo a crearlo.
	if os.path.exists(rssfile) is not True:
		make_feed()

	for post in feed.entries:
    
    	#La funzione HTMLScrap mi restistuisce la versione in stringa dell'output di BeautifulSoup cosi che posso eseguire una ricerca senza problemi all'interno di tutto il codice, compresi i tag.
		htmlscrap = get_phishedhtml(post.link)
    
		for i in range(len(keywordsarray)):
		
			keyword = keywordsarray[i]
			try:
				if re.search(re.escape(keyword), htmlscrap, re.IGNORECASE):
					print "Trovato articolo: " + post.link 
					description = Document(htmlscrap).summary()
					title = Document(htmlscrap).short_title()
					add_feed(title, description, post.link)
			except:
				pass
			
if __name__ == "__main__":
	main(sys.argv[1:])


