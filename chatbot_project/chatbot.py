"""
Code by Alexis Tudor
This code creates and runs the chatbot, who I have named Adamant.
"""
import difflib
import os
import pickle
import random
from random import randint
import nltk
import utilities
from spellchecker import SpellChecker
import time
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import torch
from deep_learning_chatbot_project.chatbot.model_training import RNN

class Chatbot():
	def __init__(self, machine_learning_enabled=False):
		"""
		Initializes the chatbot.
		"""
		nltk.download('punkt')
		# Check which OS is being used and set up the filenames appropriately
		self.system = os.name
		if self.system == "posix":
			filename = "files/knowledge_base/kb.pickle"
			self.userloc = "files/user_base/ub.pickle"
			model_file = "files/chosen_model/final_model_chat_generator_model.pt"
			word_ix = "files/chosen_model/2_model_word_to_ix.pickle"
			lengths = "files/chosen_model/2_model_lengths.pickle"
		elif self.system == "nt":
			filename = "files\\knowledge_base\\kb.pickle"
			self.userloc = "files\\user_base\\ub.pickle"
			model_file = "files\\chosen_model\\final_model_chat_generator_model.pt"
			word_ix = "files\\chosen_model\\2_model_word_to_ix.pickle"
			lengths = "files\\chosen_model\\2_model_lengths.pickle"
		else:
			print("Operating system not recognized. Contact the developer for more information.")
			exit(1)
		self.ml = machine_learning_enabled
		self.ml_topics = ["actors", "dungeon", "turn", "roll", "kraghammer", "advantage", "initiative",
			        "dragon", "dm", "strength", "dexterity", "constitution", "wisdom", "intelligence",
			        "charisma", "modifier", "damage"]
		if self.ml:
			print("Machine learning text generation enabled...")
			print("Loading vocabulary...")
			with open(word_ix, 'rb') as handle:
				self.word_to_ix = pickle.load(handle)
			with open(lengths, 'rb') as handle:
				lengths = pickle.load(handle)
				self.chunk_length = lengths[0]
				self.voc_len = lengths[1]
			print("Loading model...")
			self.decoder = RNN(self.voc_len, 500, self.voc_len, 4)
			self.decoder.load_state_dict(torch.load(model_file))
			self.decoder.eval()
		self.spellchecker = SpellChecker()
		self.sentiment = SentimentIntensityAnalyzer()
		# Load Knowledge Base
		try:
			with open(filename, 'rb') as handle:
				self.kb = pickle.load(handle)
		except:
			print("Knowledge base cannot be loaded. Is it located at files/knowledge_base/kb.pickle?")
			exit(1)
		# Load User Base
		try:
			with open(self.userloc, 'rb') as handle:
				self.user_base = pickle.load(handle)
		except:
			print("No user base found. Initializing without user base.")
			self.user_base = {}
		# Definitions for some greetings
		self.rule = "[Type \"EXIT\" to finish chatting and save your user model]\n"
		self.possible_introductions = [
			self.rule + "Hello, my name is Adamant. Who are you?" + "\n",
			self.rule + "Salutations. I am Adamant. What is your designation?" + "\n",
			self.rule + "Hello. I am a rudimentary automaton designed for human companionship. My name is Adamant. What is yours?" + "\n",
			self.rule + "Greetings. What is your name? I am called Adamant." + "\n",
			self.rule + "Greetings, human. I am called Adamant. What is your name?" + "\n"
		]
		self.curr_user = None

	def chat(self):
		"""
		The main conversation loop of the chatbot.
		"""
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
			try:
				suggestion = self.curr_user.likes[randint(0, len(self.curr_user.likes)-1)]
			except:
				try:
					suggestion = self.curr_user.dislikes[randint(0, len(self.curr_user.dislikes) - 1)]
				except:
					suggestion = None
			if suggestion:
				response = self.ex(input("Welcome back, " + self.curr_user.name + ". Would you like to talk about " +
			                         suggestion + " again?\n"))
				if "yes" in response.lower() or "sure" in response.lower() or "yeah" in response.lower() \
						or "yep" in response.lower() or "okay" in response.lower():
					topic = suggestion
				else:
					topic = self.get_topic(response)
				if not topic:
					response = self.ex(input("What would you like to discuss, then?\n"))
					topic = self.get_topic(response)
			else:
				response = self.ex(input("Welcome back, " + self.curr_user.name + ". " +
				                         "What would you like to discuss this time?\n"))
				topic = self.get_topic(response)
		# At this point, the main conversation loop can begin
		while True:
			# If we've found a topic, great! Talk about it.
			if topic:
				if self.ml:
					random_fact = self.generate_response(topic + " is", predict_len=5, temperature=10)
				else:
					random_fact = utilities.get_similar(response, self.kb[topic])
				if random_fact[-1] != "." and random_fact[-1] != "!" and random_fact[-1] != "?":
					random_fact = random_fact + "."
				if topic in self.curr_user.likes:
					speaking_options = [
						topic.title() + " is also one of my favorite topics to discuss. Here's something I know " +
						                "about it: " + random_fact + "\n",
						"I recall that you like " + topic + ". Did you know this? " + random_fact + "\n",
						"Humans do enjoy discussing the topics they like. Here's what I have in my database: " + random_fact + "\n"
					]
				elif topic in self.curr_user.dislikes:
					speaking_options = [
						"Know thy enemy. Is that why you want to discuss " + topic + " even though you dislike that topic? " +
						            "I can respect that. Here's something I know: " + random_fact + "\n",
						"I believe " + random_fact + " What a horrible fact." + "\n",
						"I believe you spoke negatively about " + topic + " in the past. In any event, " + random_fact + "\n"
					]
				else:
					speaking_options = [
						"I see, you'd like to talk about " + topic + ". Here's what I think: " + random_fact + "\n",
						"I think " + random_fact + " Does that make sense?" + "\n",
						"About " + topic + " I know " + random_fact + "\n"
					]
				response = self.ex(input(speaking_options[randint(0,len(speaking_options)-1)]))
				topic = self.get_topic(response)
			else:
				# No topic found
				random_topic = list(self.kb.keys())
				if self.ml:
					random_topic = self.ml_topics
				suggested_topic = random_topic[randint(0,len(random_topic)-1)]
				response = self.ex(input("I don't know about that. Do you want to talk about " + suggested_topic + "?\n"))
				if "yes" in response.lower() or "sure" in response.lower() or "yeah" in response.lower() \
						or "yep" in response.lower() or "okay" in response.lower():
					topic = suggested_topic
				else:
					topic = self.get_topic(response)

	def get_name(self, sentence):
		"""
		This method parses a sentence for a name and returns it.
		:param sentence: user sentence containing a name
		:return: the first word in the sentence not in the English dictionary, or False if all words are English words
		"""
		tokens = nltk.word_tokenize(sentence)
		if len(tokens) == 1:
			word = tokens[0].replace(" ", "")
			return word
		for token in tokens:
			if token != self.spellchecker.correction(token):
				word = token.replace(" ", "")
				return word
		return False

	def ex(self, response):
		"""
		This function serves as a passthrough that scans user input for the word "exit". If the user inputs "exit"
		the program ends, otherwise the response is returned unchanged.
		Best use of this function: user_response = self.ex(input("Chatbot words"))
		:param response: the sentence to parse
		:return: the response, unless an exit is found
		"""
		if response.lower() == "exit":
			if self.curr_user:
				print("Thank you for chatting with me. I will remember you, " + self.curr_user.name + ".\n")
				self.save_user()
			else:
				print("Thank you for chatting with me, nameless stranger.\n")
			exit(0)
		return response

	def save_user(self):
		"""
		This adds the current user to the user base and then saves the new user base.
		"""
		self.user_base[self.curr_user.name] = self.curr_user
		with open(self.userloc, 'wb') as handle:
			pickle.dump(self.user_base, handle, protocol=pickle.HIGHEST_PROTOCOL)

	def get_topic(self, response):
		"""
		This function finds a topic in the knowledge base in the sentence.
		:param response: sentence to check for a topic
		:return: topic if found, otherwise None.
		"""
		keys = list(self.kb.keys())
		if self.ml:
			keys = self.ml_topics
		new_response = response.lower()
		new_response = new_response.replace(".", "").replace(",", "").replace("!", "").replace("?", "")
		for key in keys:
			if key in new_response:
				# If we've found a key, we want to update the user model with it whether it is positive or negative
				score = self.sentiment.polarity_scores(response)["compound"]
				if score > .5:
					self.curr_user.likes.append(key)
				elif score < -.5:
					self.curr_user.dislikes.append(key)
				return key
		return None

	def generate_response(self, prime_str, predict_len=100, temperature=0.8):
		"""
		This function generates a sentence based on the first two words
		of it using the machine learning model
		NOTE: This code is modified based on the evaluation function
		in the deep_learning_chatbot_project/model_training.py
		:param prime_str: The first two words in the sentence
		:param predict_len: How many words to generate
		:param temperature: How much variation should be in the response
		(Lower temperatures result in more repeated words)
		:return: the completed string
		"""
		hidden = self.decoder.init_hidden()
		words_in_dict = self.word_to_ix.keys()
		starter_words = prime_str.split()
		# If we're using new words, we need to check if they're in our dictionary
		# or else this will crash. We select the closest word possible if that's the
		# case. This is a bad solution, but hey, it's been a long semester and
		# we're all only human, right?
		for index, word in enumerate(starter_words):
			if not word in words_in_dict:
				new_word = difflib.get_close_matches(word, words_in_dict)
				if len(new_word) == 0:
					starter_words[index] = random.choice(list(words_in_dict))
				else:
					starter_words[index] = new_word[0]
		for p in range(predict_len):
			prime_input = torch.tensor([self.word_to_ix[w] for w in starter_words], dtype=torch.long)
			input = prime_input[-2:]
			output, hidden = self.decoder(input, hidden)

			# Generate words from sampling the model
			output_dist = output.data.view(-1).div(temperature).exp()
			top_i = torch.multinomial(output_dist, 1)[0]

			# Make a new string with the predicted word and repeat
			predicted_word = list(self.word_to_ix.keys())[list(self.word_to_ix.values()).index(top_i)]
			prime_str += " " + predicted_word

		return prime_str