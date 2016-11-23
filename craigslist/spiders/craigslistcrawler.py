# -*- coding: utf-8 -*-
import scrapy
from urlparse import urlparse
from pymongo import MongoClient
from scrapy import Selector
from postmarker.core import PostmarkClient
import time

class CraigslistcrawlerSpider(scrapy.Spider):
    name = "craigslistcrawler"
    start_urls = ['https://sandiego.craigslist.org/search/sss?query=macbook+pro+15%22+16gb+2015&sort=rel']

    def parse(self, response):
    	o = urlparse(response.url)
    	rootUrl = o.scheme + "://" + o.netloc

        client = MongoClient(host="mongodb://usrcraigslist:8wqiqAVeaOmW@ds035750.mlab.com:35750/craigslist")
    	db = client.craigslist

    	email_content = ""
    	item_price = ""
    	item_url = ""
    	item_title = ""
    	aryLI = response.xpath('/html/body/section/form/div[4]/ul/li').extract()
    	for li in aryLI:
    		selLi = Selector(text=li, type="html")

    		#PRICE
    		aryPrice = selLi.css('.result-price::text').extract()
    		if len(aryPrice)>0:
    			item_price = str(aryPrice[0])

    		#URL
    		aryUrl = selLi.xpath('//a/@href').extract()
    		if len(aryUrl)>0:
    			item_url = str(aryUrl[0]).strip()
    			if len(item_url)>5:
    				if item_url[0:2] == "//":
    					item_url = "https:" + item_url
    				else:
    					item_url = rootUrl + item_url

    		#TITLE
    		aryTitle = selLi.xpath('//a/text()').extract()
    		if len(aryTitle)>0:
    			for title in aryTitle:
    				title = str(title).strip()
    				if title != "":
    					item_title = title
    					break

    		item_price = item_price.strip()
    		item_url = item_url.strip()
    		item_title = item_title.strip()

    		rec_count = db.macbookpro.find({"url":item_url}).count()
    		if rec_count==0:
    			#if there is no record, save it!
    			db.macbookpro.insert_one({"url":item_url,"title":item_title,"price":item_price})
    			email_content += "\n<br>url:" + item_url + "\n<br>title:" + item_title + "\n<br>price:" + item_price+"\n<hr>"


    	client.close()

    	#EMAIL
    	if email_content !="":
			email_content = "<b>URL:</b>" + str(o.geturl()) + "<br><br>" + email_content
			now = str(time.strftime("%d/%m/%Y %H:%M"))

			html_body = '<html><body><strong>' + now + ' result</strong><p>' + email_content + '</body></html>'
			email_title = "craigslist new post " + now

			postmarkapp = PostmarkClient(token="339a68d4-2d68-42ba-9a73-ea849fd60ecd")
			result = postmarkapp.emails.send(From="osman@geonni.com",To="osman@geonni.com",Subject=email_title,HtmlBody=html_body)
			print result