# -*- coding: utf-8 -*-

import Shop

import requests
from lxml import html
import re

from joblib import Parallel, delayed

class YamadaWebCom(Shop.Shop):
	def __init__(self):
		super(YamadaWebCom, self).__init__()
		self.name = "YamadaWebCom"
		self.url = "https://www.yamada-denkiweb.com"
		self.itemList = []
		self.maxItems = 600
		self.minPercentage = 15

	def ObtainItemListByCategory(self, category):
		itemList = []

		displayCount = 60

		# First, I get total items in category.
		print("url = " + self.url + category["url"] + "/?pl=" + str(self.minPrice) + "&ph=" + str(self.maxPrice))
		response = requests.get(self.url + category["url"] + "/?pl=" + str(self.minPrice) + "&ph=" + str(self.maxPrice), timeout = self.timeout)
		if requests.codes.ok != response.status_code:
			print("status code is " + str(response.status_code) + " from " + self.url + category["url"])
			return itemList
		try:
			items = html.fromstring(response.text).xpath("//div[@class='round-box list-search-panel clearfix']/div[1]/p[1]/span[@class='highlight']")[0].text
		except IndexError:
			print("Oops!")
			print(self.url + category["url"])
			return itemList
		print("items = " + items)
		if -1 != self.maxItems:
			if int(items) > self.maxItems:
				items = str(self.maxItems)
		# Get item table in each page.
		for loop in range(((int(items) - 1) // displayCount) + 1):
			print(self.url + category["url"] + "/?o=" + str(loop * displayCount) + "&limit=60&pl=" + str(self.minPrice) + "&ph=" + str(self.maxPrice))
			try:
				response = requests.get(self.url + category["url"] + "/?o=" + str(loop * displayCount) + "&limit=60", timeout = self.timeout)
			except:
				continue
			if requests.codes.ok != response.status_code:
				continue
			doc = html.fromstring(response.text)
			# Path for getting model name.
			pathes = doc.xpath("//span[contains(./text(), '%')]/../../preceding-sibling::p[@class='item-name']/a/@href")
			# Price.
			prices = doc.xpath("//span[contains(./text(), '%')]/../preceding-sibling::p[@class='subject-text']/span[@class='highlight large']")
			# Points.
			points = doc.xpath("//span[contains(./text(), '%')]")
			percentages = doc.xpath("//span[contains(./text(), '%')]")
			for i in range(len(pathes)):
				try:
					# First, I check if this item is added over 10% points.
					percentage = re.search('([0-9]*)%', percentages[i].text).group(1)
					if (self.minPercentage > int(percentage)):
						continue
				except:
					print("Oopsss!")
					continue
				if re.search('[1-9]+(,[0-9]{1,3})*', prices[i].text) is not None:
					dict = {}
					price = re.search('[1-9]+(,[0-9]{1,3})*', prices[i].text).group(0)
					dict["price"] = price.replace(",", "")
					try:
						detailDoc = requests.get(self.url + pathes[i], timeout = self.timeout)
					except requests.exceptions.ConnectionError:
						print("Connection Error")
						print(self.url + pathes[i])
					except requests.exceptions.ReadTimeout:
						print("Oops!")
						print(self.url + pathes[i])
						continue
					if requests.codes.ok != detailDoc.status_code:
						continue
					detailDoc.encoding = detailDoc.apparent_encoding
					# Shop
					dict["shop"] = self.name
					# Category
					dict["category"] = category["name"]
					# Model Name
					try:
						model = html.fromstring(detailDoc.text).xpath("//div[@class='parts-block spec-table']/table[1]/tr[1]/td[1]")[0]
						dict["name"] = model.text
					except:
						print("Oops!")
						print("ModelName, url = " + self.url + pathes[i])
						dict["name"] = ""
					# Product Name
					try:
						product = html.fromstring(detailDoc.text).xpath("//div[@class='item_description default-price-block']/p[@class='item_name']")[0]
						dict["product"] = product.text
					except:
						print("Oops!")
						print("Product, url = " + self.url + pathes[i])
						dict["product"] = ""
					# Point
					try:
						point = re.search('(.*)P', points[i].text).group(1)
						dict["point"] = point.replace(",", "")
					except:
						print("Oops!")
						print("Point, url = " + self.url + pathes[i])
						dict["point"] = "0"
					dict["url"] = self.url + pathes[i]
					if self.minPrice < int(dict["price"]) and int(dict["price"]) < self.maxPrice:
						found = False
						for item in itemList:
							if dict["name"] == item["name"]:
								found = True
								break
						if False == found:
							itemList.append(dict)
							print(dict)
		return itemList

	def UpdateItemList(self):

		categories = [
	#		{"url": "/category/201", "name": "冷蔵庫・洗濯機・掃除機・生活家電"},
	#		{"url": "/category/202", "name": "電子レンジ・炊飯器・キッチン家電"},
	#		{"url": "/category/203", "name": "エアコン・空調・季節家電"},
	#		{"url": "/category/204", "name": "テレビ・レコーダー"},
			{"url": "/category/205", "name": "美容家電・健康家電"},
			{"url": "/category/206", "name": "カメラ・ビデオカメラ"},
			{"url": "/category/207", "name": "パソコン・周辺機器・PCソフト"},
			{"url": "/category/208", "name": "オーディオ・電子楽器"},
			{"url": "/category/209", "name": "携帯電話・スマートフォン"},
			{"url": "/category/210", "name": "電子辞書・電話・FAX・オフィス用品"},
			{"url": "/category/211", "name": "インク・記録メディア・電池・電球"},
	#		{"url": "/category/212", "name": "家具・インテリア雑貨"},
			{"url": "/category/213", "name": "ゲーム機・ゲームソフト"},
	#		{"url": "/category/214", "name": "映画・音楽ソフト"},
			{"url": "/category/215", "name": "おもちゃ・ホビー"},
	#		{"url": "/category/216", "name": "フィットネス・トレーニング機器"},
			{"url": "/category/217", "name": "食料品・ドリンク・日用品・雑貨品"},
			{"url": "/category/218", "name": "美容・コスメ・健康"},
			{"url": "/category/219", "name": "医薬品・衛生用品・ベビー・介護"},
			{"url": "/category/220", "name": "時計"},
	#		{"url": "/category/221", "name": "工具・DIY"},
	#		{"url": "/category/222", "name": "スポーツ・アウトドア・カー用品"},
	#		{"url": "/category/223", "name": "文房具"},
	#		{"url": "/category/224", "name": "リユース"},
		]
		# Parallel processing by count of CPU.
		itemListArray = Parallel(n_jobs = -1)([delayed(self.ObtainItemListByCategory)(category) for category in categories])
		self.itemList = [e for inner_list in itemListArray for e in inner_list]
