from bs4 import BeautifulSoup
import requests
import re
import urllib.request
from urllib.parse import urljoin, urlparse
import os

class WebCrawler():
	def __init__(self, urls):
		print("Initializing Web Crawler...")
		self.starter_urls = urls
		try:
			self.urls = self.read_file_into_list("files/urls/urls.txt")
		except:
			self.urls = []

	# Instructions:
	# Start with 1-3 URLs that represent a topic (a sport, a celebrity, a place, etc.) and crawl to
	# find 15 – 25 relevant URLs. Make sure that some of the URLs are outside the original
	# starter URLs.
	def find_urls(self):
		"""
		Given a starter URL, this finds all URLs from the starter URL and also
		25 URLs from each of those URLs.
		"""
		print("Finding URLs from starter URLs...")
		# These excluded URLs are mostly randomized generators
		excluded_urls = self.read_file_into_list("files/urls/bad_urls.txt")
		# Get every URL from the starter URL pages
		for url in self.starter_urls:
			r = requests.get(url)

			data = r.text
			soup = BeautifulSoup(data, 'html.parser')

			# Find first level URLs
			for link in soup.find_all('a'):
				path = link.get('href')
				if path and path.startswith('/'):
					path = urljoin(url, path)
				self.urls.append(self.remove_after_hash(path))

		# Remove excluded URLs from the final list
		new_urls = []
		for url in self.urls:
			if not (url.replace("\n","") in excluded_urls):
				new_urls.append(url)
		self.urls = new_urls

		# Turn the URL list to a set and back again to remove duplicates
		temp_set = set(self.urls)
		self.urls = list(temp_set)

		# Remove all invalid items
		for url in self.urls:
			try:
				_ = requests.get(url)
			except:
				self.urls.remove(url)
		# Write final URL list to file
		self.write_list_to_file("files/urls/urls.txt", self.urls)

	# Code inspired by code from Dr. Mazidi's GitHub below
	def is_valuable(self, element):
		"""
		Determines whether an element in an html file is part of useful information or not
		:param element: element to check
		:return: True if element is not blacklisted, False if not
		"""
		not_wanted = ['style', 'script', '[document]', 'head', 'title',
		              'noscript', 'header', 'html', 'meta', 'input',
		              '\n', 'Advertisement']
		if element.parent.name in not_wanted:
			return False
		elif re.match('<!--.*-->', str(element.encode('utf-8'))):
			return False
		return True

	def read_file_into_list(self, file):
		"""
		Code to read the contents of a file into a list
		:param file: filename to read in
		:return: a list containing the contents of each line of the
					file as an element
		"""
		f = open(file, "r")
		new_list = []
		for line in f:
			newline = line.replace("\n", "")
			new_list.append(newline)
		f.close()
		return new_list

	def write_list_to_file(self, file, l):
		"""
		Helper function that writes a list into a file, each element of
		the list separated by a newline
		:param file: filename to write to
		:param l: list to write
		"""
		f = open(file, "w")
		for item in l:
			f.write(str(item.replace("\n", "")))
			f.write("\n")

	def remove_after_hash(self, element):
		"""
		This method just removes all text after a #
		This is primarily for URLs that are duplicates but have a #section
		indicating what part of the page to start with (useful for humans,
		useless for a web scraper and results in duplication)
		:param element: text to remove end of
		:return: returns string without anything after the # (including the #)
		"""
		new_string = ""
		for char in element:
			if char != "#":
				new_string += char
			else:
				break
		return new_string

	# Instruction:
	# Write a function to loop through the URLs, scrape text off each page and write it to a
	# file. Write each URL’s text to a separate file.
	def scrape_all_urls(self):
		"""
		This method scrapes the urls in self.urls (which contains
		URLs from files/urls/urls.txt) and puts each URL's data into
		a separate file. This does rudimentary text cleaning primarily
		to get only visible text information from the website.
		"""
		print("Scraping found URLs for data...")
		i = 1
		for url in self.urls:
			# Get the information from the URL as raw HTML
			try:
				raw_site = requests.get(url)
			except:
				continue
			html_site = raw_site.content
			# Get a soup object to parse the html
			soup = BeautifulSoup(html_site, 'html.parser')
			raw_text = soup.find_all(text=True)
			# Remove valueless items
			final_text = []
			for text in raw_text:
				if self.is_valuable(text):
					final_text.append(text)
			# Write to file with the URL as the first  line
			if "d20srd" in url:
				for _ in range(111):
					try:
						final_text.pop(0)
					except:
						break
			final_text.insert(0, url)
			self.write_list_to_file("files/raw_information/file" + str(i) + ".txt", final_text)
			i += 1

	# Instruction:
	# Write another function to clean up the text files. Read in each raw file and clean it up as
	# much as possible with NLP techniques. If you have x files in, you will have x files out.
	def clean_files(self):
		print("Cleaning scraped text...")
		files = os.listdir("files/raw_information/")
		for file in files:
			information = self.read_file_into_list("files/raw_information/" + file)
			url = information.pop(0)
			clean_text = ""
			for info in information:
				new_info = info.replace("\n", "")
				if len(new_info) != 0:
					clean_text += new_info
					if new_info[-1] != " ":
						clean_text += " "
			f = open("files/clean_information/clean_" + file, "w")
			f.write(url)
			f.write("\n")
			f.write(clean_text)
			f.close()

	# Instruction:
	# Write a function to extract at least 25 important terms from the cleaned-up files using
	# an importance measure such as tf-idf. You might want to lower-case everything, remove
	# stopwords and punctuation first. Output the top 25-40 important terms.
	# • Manually determine the top 10-15 terms based on your domain knowledge.
	def extract_important_terms(self):
		print("Extracting important terms...")

	# Instruction:
	# Build a searchable knowledge base of facts that a chatbot can share related to your
	# important terms. The “knowledge base” can be a simple as a Python dict which you
	# pickle or a simple sql database.
	def build_knowledge_base(self):
		print("Building knowledge base...")

