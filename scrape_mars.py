from bs4 import BeautifulSoup
from splinter import Browser
from selenium import webdriver
import requests
import shutil
from IPython.display import Image
import pandas as pd
import time
import pymongo
import json

# Initialize PyMongo to work with MongoDBs
conn = 'mongodb://localhost:27017'
client = pymongo.MongoClient(conn)

# Define database and collection
db = client.Mars
collection = db.Mars


def init_browser():    
		executable_path = {'executable_path': 'chromedriver.exe'}
		return Browser('chrome', **executable_path, headless=False)

def scrape():
		mars_data = {}
		url = 'https://mars.nasa.gov/news/'
		url2 = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'
		url3 = 'https://twitter.com/marswxreport?lang=en'
		url4 = 'http://space-facts.com/mars/'
		url5 = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
		##nasa
		browser = init_browser()
		browser.visit(url)

		html = browser.html
		soup = BeautifulSoup(html, 'html.parser')

		article = soup.find("div", class_="list_text")
		news_p = article.find("div", class_="article_teaser_body").text
		news_title = article.find("div", class_="content_title").text
		news_date = article.find("div", class_="list_date").text
		# Add the news date, title and summary to the dictionary
		mars_data["news_date"] = news_date
		mars_data["news_title"] = news_title
		mars_data["summary"] = news_p
	
		#JPL
		browser = init_browser()
		browser.visit(url)

		html = browser.html
		soup = BeautifulSoup(html, 'html.parser')

		browser = init_browser()
		browser.visit(url2)
		browser.find_by_id('full_image').click()
		featured_image_url = browser.find_by_css('.fancybox-image').first['src']

		response = requests.get(featured_image_url, stream=True)
		with open('img.jpg', 'wb') as out_file:
			shutil.copyfileobj(response.raw, out_file)
		from IPython.display import Image
		Image(url='img.jpg')
		
		# Add the featured image url to the dictionary
		mars_data["featured_image_url"] = featured_image_url
		
		#twitter
		browser = init_browser()
		browser.visit(url3)
		for text in browser.find_by_css('.tweet-text'):
			if text.text.partition(' ')[0] == 'Sol':
				mars_weather = text.text
				break
		# Add the weather to the dictionary
		mars_data["mars_weather"] = mars_weather
		
		#facts		
		df = pd.read_html(url4, attrs = {'id': 'tablepress-mars'})[0]
		df = df.set_index(0).rename(columns={1:"value"})
		del df.index.name
		mars_facts = df.to_html()
		mars_data["mars_table"] = mars_facts

		#hemispheres
		browser = init_browser()
		browser.visit(url5)

		first = browser.find_by_tag('h3')[0].text
		second = browser.find_by_tag('h3')[1].text
		third = browser.find_by_tag('h3')[2].text
		fourth = browser.find_by_tag('h3')[3].text

		browser.find_by_css('.thumb')[0].click()
		first_img = browser.find_by_text('Sample')['href']
		browser.back()

		browser.find_by_css('.thumb')[1].click()
		second_img = browser.find_by_text('Sample')['href']
		browser.back()

		browser.find_by_css('.thumb')[2].click()
		third_img = browser.find_by_text('Sample')['href']
		browser.back()

		browser.find_by_css('.thumb')[3].click()
		fourth_img = browser.find_by_text('Sample')['href']

		hemisphere_image_urls = [
			{'title': first, 'img_url': first_img},
			{'title': second, 'img_url': second_img},
			{'title': third, 'img_url': third_img},
			{'title': fourth, 'img_url': fourth_img}
		]
		
		mars_data['mars_hemis'] = hemisphere_image_urls
		# Return the dictionary
		return mars_data

# Dictionary to be inserted as a MongoDB document
post = {scrape}

collection.insert_one(post)

