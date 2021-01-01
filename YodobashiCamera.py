# -*- coding: utf-8 -*- 

import Shop

import requests
from lxml import html
import re

from joblib import Parallel, delayed

class YodobashiCamera(Shop.Shop):
	def __init__(self):
		super(YodobashiCamera, self).__init__()
		self.name = "YodobashiCamera"
		self.url = "https://www.yodobashi.com/"
		self.itemList = []

	def ObtainItemListByCategory(self, category):
		itemList = []

		displayCount = 48
		headers = {
			'User-Agent': 'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; WOW64; Trident/6.0)',
			'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
			'Accept-Language': 'ja',
		}
		response = requests.get(self.url + category["url"] + "?word=", timeout = self.timeout, headers = headers)
		if requests.codes.ok != response.status_code:
			print("status code is " + str(response.status_code) + " from " + self.url + category["url"])
			return itemList
		try:
			items = re.search('NumHit: \'(\d+)\'', response.text).group(1)
		except IndexError:
			print("Oops!")
			print(self.url + category["url"])
			return itemList
		# Get item table in each page.
		for loop in range((int(items) // displayCount) + 1):
			try:
				response = requests.get(self.url + category["url"] + "p" + str(loop + 1) + "/?word=", timeout = self.timeout, headers = headers)
			except:
				continue
			if requests.codes.ok != response.status_code:
				continue
			doc = html.fromstring(response.text)
			# Path for getting model name.
			pathes = doc.xpath("//div[@id='listContents']/div[3]/div/a/@href")
			# Price.
			prices = doc.xpath("//div[@id='listContents']/div[3]/div/div[@class='pInfo']/ul/li[2]/span")
			# Points.
			points = doc.xpath("//div[@id='listContents']/div[3]/div/div[@class='pInfo']/ul/li[3]/span")
			percentages = doc.xpath("//div[@id='listContents']/div[3]/div/div[@class='pInfo']/ul/li[3]/span/span")
			for i in range(len(pathes)):
				try:
					# First, I check if this item is added over 10% points.
					percentage = re.search('（([0-9]*)％還元）', percentages[i].text).group(1)
					if (10 > int(percentage)):
						continue
				except:
					continue
				if re.search('￥[0-9]*(,[0-9]{1,3})*', prices[i].text) is not None:
					dict = {}
					price = re.search('￥([0-9]*(,[0-9]{1,3})*)', prices[i].text).group(1)
					dict["price"] = price.replace(",", "")
					# I check price is affordable.
					# if self.minPrice > int(dict["price"]) or self.maxPrice < int(dict["price"]):
					# 	continue
					try:
						detailDoc = requests.get(self.url + pathes[i], timeout = self.timeout, headers = headers)
					except:
						print("Oops!")
						print(pathes[i])
						continue
					if requests.codes.ok != detailDoc.status_code:
						continue
					detailDoc.encoding = detailDoc.apparent_encoding
					# Shop
					dict["shop"] = self.name
					# Category
					dict["category"] = category["name"]
					# Model Name
					modelList = html.fromstring(detailDoc.text).xpath("//div[@id='productTab_spec01']/ul/li[2]/a/span")
					if(0 != len(modelList)):
						model = modelList[0]
						dict["name"] = re.search('(.*)のもっと詳しい情報について', model.text).group(1)
					else:
    						dict["name"] = html.fromstring(detailDoc.text).xpath("//h1[@id='products_maintitle']/span")[0].text
					# Product Name
					product = html.fromstring(detailDoc.text).xpath("//h1[@id='products_maintitle']/span")[0]
					dict["product"] = product.text
					point = re.search('([0-9]{1,3}(,[0-9]{1,3})?)ポイント', points[i].text).group(1)
					dict["point"] = point.replace(",", "")
					dict["url"] = self.url + pathes[i]
					itemList.append(dict)
		return itemList

	def UpdateItemList(self):
		categories = [
			{"url": "category/22052/500000073035/500000073036/", "name": "ヘッドホン・イヤホン"},
		]
		# Parallel processing by count of CPU.
		itemListArray = Parallel(n_jobs = -1)([delayed(self.ObtainItemListByCategory)(category) for category in categories])
		self.itemList = [e for inner_list in itemListArray for e in inner_list]
