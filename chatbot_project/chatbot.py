"""
Code by Alexis Tudor
This code creates and runs the chatbot, who I have named Adamant.
"""
import os
import pickle
from random import seed
from random import randint
import nltk
import utilities
from spellchecker import SpellChecker
import time
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

class Chatbot():
	def __init__(self):
		nltk.download('punkt')
		self.spellchecker = SpellChecker()
		self.sentiment = SentimentIntensityAnalyzer()
		system = os.name
		if system == "posix":
			filename = "files/knowledge_base/kb.pickle"
			self.userloc = "files/user_base/ub.pickle"
		elif system == "nt":
			filename = "files\\knowledge_base\\kb.pickle"
			self.userloc = "files\\user_base\\ub.pickle"
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
			with open(self.userloc, 'rb') as handle:
				self.user_base = pickle.load(handle)
		except:
			print("No user base found. Initializing without user base.")
		self.rule = "[Type \"EXIT\" to finish chatting and save your user model]"
		self.possible_introductions = [
			"Hello, my name is Adamant. Who are you?",
			"Salutations. I am Adamant. What is your designation?",
			"Hello. I am a rudimentary automaton designed for human companionship. My name is Adamant. What is yours?",
			"Greetings. What is your name? I am called Adamant.",
			"Greetings, human. I am called Adamant. What is your name?"
		]
		self.curr_user = None

	def chat(self):
		# Make some space for the user to see the chatbot is starting
		print("Chatbot initializing...")
		time.sleep(1)
		print(".")
		time.sleep(1)
		print(".")
		time.sleep(1)
		print(".")
		time.sleep(1)
		# Introduce the robot
		response = self.ex(input(self.possible_introductions[randint(0, len(self.possible_introductions)-1)]))
		name = self.get_name(response)
		# Find a valid name logic, if the name is not found, create one!
		if len(nltk.word_tokenize(response)) == 1:
			name = response
		if not name:
			response = self.ex(input("I'm sorry, I didn't get your name. Could you repeat it?\n"))
			name = self.get_name(response)
			if len(nltk.word_tokenize(response)) == 1:
				name = response
			if not name:
					name = utilities.generate_name()
					print("I'm sorry, I didn't get that. Your name is foreign to me. " +
					      "Luckily for you, I can give you a name that I can understand. Your new name is " + name + ".\n")
		# Check if found name matches a user in the user base
		self.curr_user = utilities.user(name)
		new_user = False
		try:
			self.curr_user = self.user_base[self.curr_user.name]
		except:
			new_user = True
		# If the user is new, say hi. If they are old, ask if they'd like to discuss a random like.
		if new_user:
			response = self.ex(input("It's nice to meet you, " + self.curr_user.name + ". What would you like to talk about?\n"))
			topic = self.get_topic(response)
		else:
			suggestion = self.curr_user.likes[randint(0, len(self.curr_user.likes)-1)]
			response = self.ex(input("Welcome back, " + self.curr_user.name + ". Would you like to talk about " +
			                         suggestion + " again?\n"))
			if "yes" in response.lower():
				topic = suggestion
			else:
				topic = self.get_topic(response)
			if not topic:
				response = self.ex(input("What would you like to discuss, then?\n"))
				topic = self.get_topic(response)
		# At this point, the main conversation loop can begin
		while True:
			# If we've found a topic, great! Talk about it.
			if topic:
				random_facts = self.kb[topic]
				random_fact = random_facts[randint(0,len(random_facts)-1)]
				if random_fact[-1] != "." and random_fact[-1] != "!" and random_fact[-1] != "?":
					random_fact = random_fact + "."
				if topic in self.curr_user.likes:
					speaking_options = [
						topic.title() + " is also one of my favorite topics to discuss. Here's something I know " +
						                "about it: " + random_fact,
						"I recall that you like " + topic + ". Did you know this? " + random_fact,
						"Humans do enjoy discussing the topics they like. Here's what I have in my database: " random_fact
					]
				elif topic in self.curr_user.dislikes:
					speaking_options = [
						"Know thy enemy. Is that why you want to discuss " + topic + " even though you dislike that topic? " +
						            "I can respect that. Here's something I know: " + random_fact,
						"I believe " + random_fact + " What a horrible fact.",
						"I believe you spoke negatively about " + topic + " in the past. In any event, " + random_fact
					]
				else:
					speaking_options = [
						"I see, you'd like to talk about " + topic + ". Here's what I think: " + random_fact,
						"I think " + random_fact + " Does that make sense?",
						"This feels like a topic you're fairly neutral about. About " + topic + " I know " + random_fact
					]
				response = self.ex(input(speaking_options[randint(0,len(speaking_options)-1)]))
				topic = self.get_topic(response)
			else:
				# No topic found
				# CHANGEX

	# Retrieval using similarity measures from the corpus you created in part 1
	# Hard-coded responses with some randomization (perhaps for greetings, etc.)
	# Make sure your project includes NLP techniques learned in class. Examples: parse user
	# response, use term frequency measures, NER, or information retrieval techniques, or any
	# techniques we learned in class.

	def get_name(self, sentence):
		tokens = nltk.word_tokenize(sentence)
		for token in tokens:
			if token != self.spellchecker.correction(token):
				return token
		return False

	def ex(self, response):
		if response.lower() == "exit":
			if self.curr_user:
				print("Thank you for chatting with me. I will remember you, " + self.curr_user.name + ".\n")
				self.save_user()
			else:
				print("Thank you for chatting with me, nameless stranger.\n")
			exit(0)
		return response

	def save_user(self):
		self.user_base[self.curr_user.name] = self.curr_user
		with open(self.userloc, 'wb') as handle:
			pickle.dump(self.user_base, handle, protocol=pickle.HIGHEST_PROTOCOL)

	def get_topic(self, response):
		keys = list(self.kb.keys())
		for key in keys:
			if key in response:
				# If we've found a key, we want to update the user model with it whether it is positive or negative
				score = self.sentiment.polarity_scores(response)["compound"]
				if score > .3:
					self.curr_user.likes.append(key)
				elif score < -.3:
					self.curr_user.dislikes.append(key)
				return key
		return None