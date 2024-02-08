from bs4 import BeautifulSoup
import requests
import re
from urllib.parse import urljoin
import os
import nltk
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer
import pickle

class WebCrawler():
	def __init__(self, urls):
		print("Initializing Web Crawler...")
		nltk.download('punkt')
		nltk.download('stopwords')
		nltk.download('wordnet')
		nltk.download('averaged_perceptron_tagger')
		self.starter_urls = urls
		try:
			self.urls = self.read_file_into_list("files/urls/urls.txt")
		except:
			self.urls = []
		self.tokens = self.tokenize_clean_text()
		try:
			self.terms = self.read_file_into_list("files/important_terms/chosenterms.txt")
		except:
			self.terms = []

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
				new_info = new_info.replace("\t", "")
				new_info = new_info.replace("\xa0", "")
				if len(new_info) != 0:
					clean_text += new_info
					if new_info[-1] != " ":
						clean_text += " "
			f = open("files/clean_information/clean_" + file, "w")
			# Uncomment this line to include URLs in the clean files
			# (the URLs are included in the raw information and the file numbers match)
			# f.write(url + "\n")
			f.write(clean_text)
			f.close()

	# Instruction:
	# Write a function to extract at least 25 important terms from the cleaned-up files using
	# an importance measure such as tf-idf. You might want to lower-case everything, remove
	# stopwords and punctuation first. Output the top 25-40 important terms.
	# • Manually determine the top 10-15 terms based on your domain knowledge.
	def extract_important_terms(self):
		"""
		This method performs tf-idf on the clean texts and prints all the terms
		with a tf-idf score greater than 5 to a file.
		"""
		print("Extracting important terms...")
		# Get cleaned text if not gotten
		if not self.tokens:
			self.tokens = self.tokenize_clean_text()
		# Preprocess the documents to remove stop words and non-alphabetical tokens
		processed_tokens = []
		for document in self.tokens:
			processed_document = ""
			for token in document:
				if token.isalpha() and token not in stopwords.words('english'):
					processed_document += token
					processed_document += " "
			processed_tokens.append(processed_document)
		# Reference: https://www.geeksforgeeks.org/understanding-tf-idf-term-frequency-inverse-document-frequency/
		tfidf = TfidfVectorizer()
		# get tf-df values
		_ = tfidf.fit_transform(processed_tokens)
		relevant_terms = {}
		for word, relevance in zip(tfidf.get_feature_names_out(), tfidf.idf_):
			relevant_terms[word] = relevance
		# Sort the dictionary
		# This code snippet from the word guess game
		sorted_relevant_terms = dict(sorted(relevant_terms.items(), key=lambda item: item[1]))
		# Output all words in importance order
		f = open("files/important_terms/autogeneratedterms.txt", "w")
		for token, relevance in reversed(sorted_relevant_terms.items()):
			if relevance < 5:
				break
			f.write(token)
			f.write(" : ")
			f.write(str(relevance))
			f.write("\n")
		f.close()

	@staticmethod
	def tokenize_clean_text():
		"""
		This tokenizes the clean text into sentences.
		:return: tokenized clean text in the following format:
				[["Document one.", "Sentence two in document one."], [...] ... ]
		"""
		text = []
		files = os.listdir("files/clean_information/")
		if len(files) == 0:
			return []
		for file in files:
			f = open("files/clean_information/" + file, "r")
			toks = nltk.sent_tokenize(f.read().lower())
			f.close()
			text.append(toks)
		return text

	# Instruction:
	# Build a searchable knowledge base of facts that a chatbot can share related to your
	# important terms. The “knowledge base” can be a simple as a Python dict which you
	# pickle or a simple sql database.
	def build_knowledge_base(self):
		"""
		This creates and pickles a knowledge base from the cleaned up text and
		chosen important terms.
		"""
		print("Building knowledge base...")
		kb = {'ttrpg': ["Ttrpgs are fun games to play with your friends."]}
		documents = self.tokenize_clean_text()
		# Build a knowledge base for every term
		for term in self.terms:
			chosen_sentences = []
			for document in documents:
				for sentence in document:
					if term in sentence:
						chosen_sentences.append(sentence)
			kb[term] = chosen_sentences
		# Pickles the knowledge base dictionary
		with open("files/knowledge_base/kb.pickle", 'wb') as handle:
			pickle.dump(kb, handle, protocol=pickle.HIGHEST_PROTOCOL)