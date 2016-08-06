import scrapy
import math
import json
import time
import re

from like123.db_manager import *

class Like123Spider(scrapy.Spider):
    # name of the spider
		name = "like123"		

		# list of allowed domains																										
		allowed_domains = ["www.like123.us"]

		# domain url
		domain = "http://www.like123.us"

		# list of search keys
		# key_words = ["pump", "gap", "steel", "carbon%20fiber", "autoclave"]
		key_words = ["autoclave"]

		def __init__(self):

				# get connection for database
				self.db = getConnection()
		
				# remove all data in database
				self.db.product.remove({})

		# make requests using items
		def start_requests(self):

				requests = []

				# iterate search keyword and make requests for getting list of products searched by keywords.
				for key in self.key_words:
						url = "http://www.like123.us/listings.php?browse=product&show_save=yes&cid=0&keyword=%s&pg=1" % key

						# make request for each search key.
						request = scrapy.Request(url, callback=self.parse_products)
						request.meta["page"] = 1
						request.meta["key"] = key
						request.meta["contacts"] = []
						requests.append(request)
		
				return requests

		# parse the list of products and make requests for scraping the detail data of a product 
		def parse_products(self, response):
				contacts = response.meta["contacts"]
				current_page = response.meta["page"]

				contacts = response.meta["contacts"]
				current_page = response.meta["page"]

				# if the current page is 1, crawl the total number of products and calculate the total number of pages.
				if current_page == 1:
						total_products = self.validate(response.xpath("//table[@class='maintablestyle']//td[@class='activetab']/text()"))
						total_products = total_products.split("(")
						
						# if there is no the total number of products in the page, exit scraping data from this page.
						if total_products == "" or len(total_products) < 2:
								return
						# otherwise, crawl the total number of products.
						else:
								total_product = int(total_products[1].strip()[:-1])

								# get the total number of pages
								total_pages = int(math.ceil(total_product / 100.0))

				# otherwise, get the total number of products from the request.
				else:
						total_pages = response.meta["total_page"]

				# if current page is greater than the total number of pages, make requests for contacts and exit to scrape data from this page.
				if current_page > total_pages:

						# make request for scraping data from the product detail pages.
						for contact in contacts:
								yield contact

						return;

				# otherwise, crawl information of all products and contacts from this page.
				else:
						# get all product nodes
						items = response.xpath("//td[@class='itemBox']")

						# iterate product nodes
						for item in items:
								product = dict()

								product["search_key"] = response.meta["key"]

								# get product name
								product["name"] = self.validate(item.xpath(".//a[@class='list_boom']/text()"))

								# make a request for product detail page and append it into contacts variable.
								url = self.validate(item.xpath(".//a[@class='list_boom']/@href"))

								request = scrapy.Request(url , callback=self.parse_product_detail, dont_filter=True)
								request.meta["product"] = product
								contacts.append(request)

						# generate url with a page number.
						url = response.url
						if "pg" in url:
								url = response.url.split("&pg")[0]
			
						url = "%s&pg=%d" % (url, current_page + 1) 

						# generate url with a page number.
						request = scrapy.Request(url, callback=self.parse_products, dont_filter=True)
						request.meta["page"] = current_page + 1
						request.meta["total_page"] = total_pages
						request.meta["key"] = response.meta["key"]
						request.meta["contacts"] = contacts
						yield request

		# crawl the detail data of a product from product detail page and make a request for scraping company contact info.
		def parse_product_detail(self, response):
				product = response.meta["product"]

				# get product attribute nodes
				attribute_nodes = response.xpath("//table[contains(@class, 'tables')]//th[@class='Formbx_head']")
				
				# crawl product info (description, price, posted_on)
				for attribute in attribute_nodes:
						
						attr_name = self.validate(attribute.xpath("./text()"))

						# get date that a product is posted	
						if attr_name == "Posted On:":
								attr_value = self.validate(attribute.xpath("./following-sibling::td[1]//div/text()"))
								product['posted_on'] = attr_value

						# get the price of a product
						if attr_name == "Price:":
								attr_value = self.validate(attribute.xpath("./following-sibling::td[1]//div/text()"))
								tp_price = attr_value.split(" ")
								if len(tp_price) > 1:
									product['price'] = tp_price[1].strip()
								else:
									product['price'] = attr_value[1:].strip()

						# get the description of a product
						if attr_name == "Description:":
								temp = attribute.xpath("./following-sibling::td[1]").extract()
								attr_value += ''.join(temp).strip()
								attr_value = self.cleanhtml(attr_value).strip()
								attr_value = attr_value.split("\t\t\t")

								if len(attr_value) > 1:
										attr_value = attr_value[1]
								else:
										attr_value = attr_value[0]

								product['description'] = attr_value.strip()

				# make a request for scraping data from company contact page
				url = self.validate(response.xpath("//a[contains(@href, 'company_contact.php')]/@href"))

				# check if url for company contact page.
				if url != "":
						url = "%s/%s" % (self.domain, url)

						# make a request for scraping data from company contact page.
						request = scrapy.Request(url, callback=self.parse_company_contact, dont_filter=True)
						request.meta["product"] = product
						yield request

		# crawl the company contact data from company contact page and save data into mongodb.
		def parse_company_contact(self, response):
				product = response.meta["product"]
				product['company'] = dict()

				# get company contact info nodes
				contact_nodes = response.xpath("//table[@width='102%']//tr")

				# crawl company contact info
				for node in contact_nodes:
						contact_type = self.validate(node.xpath(".//td[1]/text()"))
						contact_value = self.validate(node.xpath(".//td[2]/text()"))

						if contact_type != "":
								product['company'][self.get_contact_key(contact_type)] = contact_value

				# save all data of one product into database.
				self.db.product.insert(product)

		# validate the value of html node
		#		return string value, if data is validated
		#		return "", otherwise
		def validate(self, node):
				if len(node) > 0:
						temp = node[0].extract().strip()
						return temp
				else:	
						return ""

		# remove all html tags from content
		def cleanhtml(self, raw_html):

				cleanr =re.compile('<.*?>')
				cleantext = re.sub(cleanr, '', raw_html)

				return cleantext

		# filter a key for company contact
		def get_contact_key(self, contact_type):
				contact_type = contact_type.replace(":", "").strip()
				contact_type = contact_type.replace(" ", "_").strip()
				contact_type = contact_type.lower()

				return contact_type


