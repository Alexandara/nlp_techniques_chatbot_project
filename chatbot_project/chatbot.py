import os
import pickle

class Chatbot():
	def __init__(self):
		system = os.name
		if system == "posix":
			filename = "files/knowledge_base/kb.pickle"
		elif system == "nt":
			filename = "files\\knowledge_base\\kb.pickle"
		else:
			print("Operating system not recognized. Contact the developer for more information.")
			exit(1)
		try:
			with open(filename, 'rb') as handle:
				self.kb = pickle.load(handle)
		except:
			print("Knowledge base cannot be loaded. Is it located at files/knowledge_base/kb.pickle?")
			exit(1)