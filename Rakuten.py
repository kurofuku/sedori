# -*- coding: utf-8 -*- 

import Shop

import requests
from lxml import html
import re
import math

from joblib import Parallel, delayed

class Rakuten(Shop.Shop):
	def __init__(self):
		super(Rakuten, self).__init__()
		self.name = "Rakuten"
		self.url = "https://search.rakuten.co.jp/search/mall/-/"
		self.itemList = []
		self.maxItems = 450
		self.minPercentage = 20

	def ObtainItemListByCategory(self, category):
		itemList = []

		displayCount = 45

		# First, I get total items in category.
		# ex. https://search.rakuten.co.jp/search/mall/-/212575/?max=60000&min=20000
		baseUrl = self.url + category["url"] + "/?min=" + str(self.minPrice) + "&max=" + str(self.maxPrice)
		print("url = " + baseUrl)
		response = requests.get(baseUrl, timeout = self.timeout)
		if requests.codes.ok != response.status_code:
			print("status code is " + str(response.status_code) + " from " + baseUrl)
			return itemList
		try:
			body = html.fromstring(response.text).xpath("//span[@class='count _medium']")[0].text
			items = re.search('（([1-9]+(,[0-9]{1,3})*)件）', body).group(1).replace(",", "")
		except:
			print("Oops!")
			print(baseUrl)
			return itemList
		print("items = " + items)
		if -1 != self.maxItems:
			if int(items) > self.maxItems:
				items = str(self.maxItems)
		# Get item table in each page.
		for loop in range(((int(items) - 1) // displayCount) + 1):
			thisPageUrl = baseUrl + "&p=" + str(loop + 1)
			print(thisPageUrl)
			try:
				response = requests.get(thisPageUrl, timeout = self.timeout)
			except:
				continue
			if requests.codes.ok != response.status_code:
				continue
			doc = html.fromstring(response.text)
			# Path for getting some information.
			pathes = doc.xpath("//div[@class='dui-card searchresultitem']/div[@class='image']/a/@href")
			# Product.
			products = doc.xpath("//div[@class='dui-card searchresultitem']/div[@class='content title']/h2/a/@title")
			# Price.
			prices = doc.xpath("//div[@class='dui-card searchresultitem']/div[@class='content description price']/span[@class='important']")
			# Points.
			points = doc.xpath("//div[@class='dui-card searchresultitem']/div[@class='content points']/span")
			for i in range(len(pathes)):
				price = prices[i].text.replace(",", "")
				try:
					point = re.search('([1-9][0-9]*(,[0-9]{1,3})*)ポイント', points[i].text).group(1).replace(",", "")
				except:
					print("Oops! cannot get points[i]")
					continue
				percentage = math.floor(int(point) / int(price) * 100)
				if percentage < 1:
					percentage = 1
				if (self.minPercentage > percentage):
					continue
				dict = {}
				# Shop
				dict["shop"] = self.name
				# Category
				dict["category"] = category["name"]
				# Product
				dict["product"] = products[i]
				# Name
				dict["name"] = "None"
				# Price
				dict["price"] = str(price)
				# Point
				dict["point"] = str(point)
				# URL
				dict["url"] = pathes[i]
				exists = False
				for item in itemList:
					if item["url"] == dict["url"]:
						exists = True
						break
					if item["product"] == dict["product"]:
						exists = True
						break
				if False == exists:
					itemList.append(dict)
		return itemList

	def UpdateItemList(self):

		categories = [
			{"url": "565211", "name": "財布・ケース"},
			{"url": "302050", "name": "レディース腕時計"},
			{"url": "301981", "name": "メンズ腕時計"},
			{"url": "564895", "name": "スマートウォッチ"},
			{"url": "100486", "name": "レディースジュエリー・アクセサリー"},
			{"url": "407326", "name": "メンズジュエリー・アクセサリー"},
			{"url": "502835", "name": "ヘッドホン・イヤホン"},
			{"url": "204245", "name": "美顔器・スチーマー"},
			{"url": "100940", "name": "ヘアケア・スタイリング"},
			{"url": "100960", "name": "ボディケア"},
			{"url": "212575", "name": "シェーバー・バリカン"},
			{"url": "566891", "name": "デンタルケア"},
			{"url": "212540", "name": "ドライヤー・ヘアアイロン"},
			{"url": "100083", "name": "デジタルカメラ"},
			{"url": "100087", "name": "PCパーツ"},
			{"url": "560202", "name": "スマートフォン本体"},
			{"url": "560029", "name": "タブレットPC本体"},
			{"url": "111120", "name": "香水・フレグランス"},
		]
		# Parallel processing by count of CPU.
		itemListArray = Parallel(n_jobs = -1)([delayed(self.ObtainItemListByCategory)(category) for category in categories])
		self.itemList = [e for inner_list in itemListArray for e in inner_list]
