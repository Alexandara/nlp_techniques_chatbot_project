"""
Code by Alexis Tudor
This code creates and runs the chatbot, who I have named Adamant.
"""
import os
import pickle
from random import seed
from random import randint
import enchant
import nltk
import utilities


class Chatbot():
	def __init__(self):
		nltk.download('punkt')
		self.us_dictionary = enchant.Dict("en_US")
		system = os.name
		if system == "posix":
			filename = "files/knowledge_base/kb.pickle"
			userloc = "files/user_base/ub.pickle"
		elif system == "nt":
			filename = "files\\knowledge_base\\kb.pickle"
			userloc = "files\\user_base\\ub.pickle"
		else:
			print("Operating system not recognized. Contact the developer for more information.")
			exit(1)
		try:
			with open(filename, 'rb') as handle:
				self.kb = pickle.load(handle)
		except:
			print("Knowledge base cannot be loaded. Is it located at files/knowledge_base/kb.pickle?")
			exit(1)
		try:
			with open(userloc, 'rb') as handle:
				self.user_base = pickle.load(handle)
		except:
			print("No user base found. Initializing without user base.")
		self.possible_introductions = [
			"Hello, my name is Adamant. Who are you?",
			"Salutations. I am Adamant. What is your designation?",
			"Hello. I am a rudimentary automaton designed for human companionship. My name is Adamant. What is yours?",
			"Greetings. What is your name? I am called Adamant.",
			"Greetings, human. I am called Adamant. What is your name?"
		]

	def chat(self):
		response = input(self.possible_introductions[randint(0, len(self.possible_introductions)-1)])
		name = self.get_name(response)
		if not name:
			response = input("I'm sorry, I didn't get your name. Could you repeat it?")
			name = self.get_name(response)
			if not name:
				name = utilities.generate_name()
				print("I'm sorry, I didn't get that. Your name is foreign to me. "
				      "Luckily for you, I can give you a name that I can understand. Your new name is " + name +".")
		print(name)

	# Retrieval using similarity measures from the corpus you created in part 1
	# Hard-coded responses with some randomization (perhaps for greetings, etc.)
	# Make sure your project includes NLP techniques learned in class. Examples: parse user
	# response, use term frequency measures, NER, or information retrieval techniques, or any
	# techniques we learned in class.

	def get_name(self, sentence):
		tokens = nltk.word_tokenize(sentence)
		for token in tokens:
			if token.isalpha() and not self.us_dictionary.check(token):
				return token
		return False
