from bs4 import BeautifulSoup
import requests
import re
import urllib.request
from urllib.parse import urljoin

class WebCrawler():
	def __init__(self, urls):
		print("Initializing Web Crawler...")
		self.starter_urls = urls
		self.urls = []

	# Start with 1-3 URLs that represent a topic (a sport, a celebrity, a place, etc.) and crawl to
	# find 15 – 25 relevant URLs. Make sure that some of the URLs are outside the original
	# starter URLs.
	def find_urls(self):
		print("Finding URLs from starter URLs...")
		first_level_urls = []
		excluded_urls = self.read_file_into_list("files/urls/bad_urls.txt")
		for url in self.starter_urls:
			r = requests.get(url)

			data = r.text
			soup = BeautifulSoup(data, 'html.parser')

			# Find first level URLs
			for link in soup.find_all('a'):
				path = link.get('href')
				if path and path.startswith('/'):
					path = urljoin(url, path)
				first_level_urls.append(path)

		# Remove some URLs that I have selected as not very productive
		# Mostly dice rollers and random generators
		for url in excluded_urls:
			if url in first_level_urls:
				first_level_urls.remove(url)

		# Find second level URLs
		# (note, this is not the correct way to do this. Far better would be
		# to use recursion with a set depth, but because I know the site has most things
		# on the second level I'm just doing this twice)
		for url in first_level_urls:
			try:
				r = requests.get(url)
			except:
				continue

			data = r.text
			soup = BeautifulSoup(data, 'html.parser')

			# Find second level URLs
			it = 0
			for link in soup.find_all('a'):
				path = link.get('href')
				if path and path.startswith('/'):
					path = urljoin(url, path)
				self.urls.append(path)
				it += 1
				if it > 25:
					break

		for url in excluded_urls:
			if url in self.urls:
				self.urls.remove(url)

		temp_set = set(self.urls)
		self.urls = list(temp_set)
		# Remove all invalid items
		for url in self.urls:
			try:
				_ = requests.get(url)
			except:
				self.urls.remove(url)
		self.write_list_to_file("files/urls/urls.txt", self.urls)

	# Code from Dr. Mazidi's GitHub below
	def visible(self, element):
		if element.parent.name in ['style', 'script', '[document]', 'head', 'title']:
			return False
		elif re.match('<!--.*-->', str(element.encode('utf-8'))):
			return False
		return True

	def read_file_into_list(self, file):
		f = open(file, "r")
		new_list = []
		for line in f:
			new_list.append(line)
		f.close()
		return new_list

	def write_list_to_file(self, file, l):
		f = open(file, "w")
		for item in l:
			f.write(str(item))
			f.write("\n")

	# • Write a function to loop through the URLs, scrape text off each page and write it to a
	# file. Write each URL’s text to a separate file.
	def scrape_all_urls(self):
		print("Scraping found URLs for data...")

	# • Write another function to clean up the text files. Read in each raw file and clean it up as
	# much as possible with NLP techniques. If you have x files in, you will have x files out.
	def clean_files(self):
		print("Cleaning scraped text...")

	# • Write a function to extract at least 25 important terms from the cleaned-up files using
	# an importance measure such as tf-idf. You might want to lower-case everything, remove
	# stopwords and punctuation first. Output the top 25-40 important terms.
	# • Manually determine the top 10-15 terms based on your domain knowledge.
	def extract_important_terms(self):
		print("Extracting important terms...")

	# • Build a searchable knowledge base of facts that a chatbot can share related to your
	# important terms. The “knowledge base” can be a simple as a Python dict which you
	# pickle or a simple sql database.
	def build_knowledge_base(self):
		print("Building knowledge base...")

