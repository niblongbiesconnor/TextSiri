# -*- coding: utf-8 -*-

import json

class ParseJSON(object):
	def __init__(self, filename):
		super(ParseJSON, self).__init__()
		try:
			self.file = open(filename, "a+")
		except IOError:
			self.file = open(filename, "w+")
		self.file.seek(0)
		try:
			self.dict = json.load(self.file)
		except ValueError:
			self.dict = {"config": {}}

	def __getitem__(self, key):
		return self.dict[key]

	def __setitem__(self, key, value):
		self.dict[key] = value

	def write(self):
		self.file.seek(0)
		self.file.truncate()
		json.dump(self.dict, self.file, indent=4)
		self.file.seek(0)

	def close(self):
		self.file.close()

def decode(text):
    if type(text) == str:
        return text
    for codec in ('utf-8', 'iso-8859-1', 'shift_jis', 'cp1252'):
        try:
            return text.encode(codec)
        except UnicodeEncodeError:
            continue
    return text.encode('utf-8', 'ignore')
