"""
Code by Alexis Tudor
This code consists of utility functions for the web crawler and chatbot
"""
import os
import nltk
import re
from random import randint

consonants = [
	"b", "c", "d", "f", "g", "h", "j", "k", "l", "m", "n", "p", "q", "r", "s", "t", "v", "w", "x", "y", "z"
]
vowels = [
	"a", "e", "i", "o", "u", "y"
]

def generate_name():
	name = ""
	name += consonants[randint(0, len(consonants)-1)].upper()
	name += vowels[randint(0, len(vowels)-1)]
	name += consonants[randint(0, len(consonants)-1)]
	name += vowels[randint(0, len(vowels)-1)]
	name += consonants[randint(0, len(consonants) - 1)]
	return name

# Code inspired by code from Dr. Mazidi's GitHub below
def is_valuable(element):
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

def read_file_into_list(file):
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

def write_list_to_file(file, l):
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

def remove_after_hash(element):
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

# The user model should store the user’s name, personal information it gathers from the dialog,
# and the user’s likes and dislikes. Add personalized remarks from the user model to the dialog engine.
# The user model can be a simple text or xml file.
class user():
	def __init__(self, name):
		self.name = name
		self.likes = []
		self.dislikes = []

