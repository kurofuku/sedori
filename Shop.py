# -*- coding: utf-8 -*- 

import multiprocessing

class Shop(object):
	def __init__(self):
		self.name = ""
		self.url = ""
		self.itemList = []
		self.minPercentage = 10
		self.minPrice = 20000
		self.maxPrice = 200000
		self.maxItems = -1
		self.timeout = 120

	def UpdateItemList(self):
		pass

	def GetItemList(self):
		return self.itemList
