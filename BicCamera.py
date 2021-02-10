# -*- coding: utf-8 -*- 

import Shop

import requests
from lxml import html
import re

from joblib import Parallel, delayed

class BicCamera(Shop.Shop):
	def __init__(self):
		super(BicCamera, self).__init__()
		self.name = "BicCamera"
		self.url = "https://www.biccamera.com/"
		self.itemList = []
		self.maxItems = 500
		self.minPercentage = 15

	def ObtainItemListByCategory(self, category):
		itemList = []

		displayCount = 100

		headers = {
			'User-Agent': 'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; WOW64; Trident/6.0)',
			'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
			'Accept-Language': 'ja',
		}
		response = requests.get(self.url + category["url"], timeout = self.timeout, headers = headers)
		if requests.codes.ok != response.status_code:
			print("status code is " + str(response.status_code) + " from " + self.url + category["url"])
			return itemList
		try:
			items = html.fromstring(response.text).xpath("//input[@type='hidden'][@name='totalRecord']/@value")[0]
		except IndexError:
			print("Oops!")
			print(self.url + category["url"])
			return itemList
		# Get item table in each page.
		for loop in range((int(items) // displayCount) + 1):
			try:
				esponse = requests.get(self.url + category["url"] + "/?rowPerPage=" + str(displayCount) + "&p=" + str(loop + 1), timeout = self.timeout, headers = headers)
			except:
				continue
			if requests.codes.ok != response.status_code:
				continue
			doc = html.fromstring(response.text)
			# Path for getting model name.
			pathes = doc.xpath("//p[@class='bcs_point']/preceding-sibling::p[@class='bcs_title']/a/@href")
			# Price.
			prices = doc.xpath("//p[@class='bcs_point']/preceding-sibling::p[@class='bcs_price']/span[@class='val']")
			# Points.
			points = doc.xpath("//p[@class='bcs_point']/span")
			for i in range(len(pathes)):
				if re.search('[0-9]+(,[0-9]{1,3})*', prices[i].text) is not None:
					price = re.search('[0-9]+(,[0-9]{1,3})*', prices[i].text).group(0).replace(",", "")
					point = re.search('[0-9]+(,[0-9]{1,3})*', points[i].text).group(0).replace(",", "").replace("ポイント", "")
					try:
						# First, I check if this item is added over 10% points.
						if (self.minPercentage > (int(price) / int(point))):
							continue
					except:
						continue
					dict = {}
					dict["price"] = price
					# I check price is affordable.
					if self.minPrice > int(price) or self.maxPrice < int(price):
						continue
					try:
						detailDoc = requests.get(pathes[i], timeout = self.timeout, headers = headers)
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
					model = None
					try:
						model = html.fromstring(detailDoc.text).xpath("//div[@class='bcs_detail']/table[1]/tbody[1]/tr[2]/td[1]")[0]
					except:
						pass
					if model is None:
						try:
							model = html.fromstring(detailDoc.text).xpath("//div[@class='bcs_detail']/table[1]/tbody/tr[2]/td")[0]
						except:
							pass
					if model is None:
						continue
					dict["name"] = model.text
					# Product Name
					product = html.fromstring(detailDoc.text).xpath("//section/@data-item-name")[0]
					dict["product"] = product
					dict["point"] = point
					dict["url"] = pathes[i]
					itemList.append(dict)
		return itemList

	def UpdateItemList(self):
		categories = [
	#		{"url": "/bc/category/001/150/035/", "name": "空気清浄機・空間清浄器"},
	#		{"url": "/bc/category/001/150/110/", "name": "除湿機・乾燥機"},
	#		{"url": "/bc/category/001/150/041/", "name": "加湿器・関連品"},
	#		{"url": "/bc/category/001/150/100/", "name": "扇風機・サーキュレーター"},
	#		{"url": "/bc/category/001/153/005/", "name": "オーブンレンジ・電子レンジ"},
	#		{"url": "/bc/category/001/153/010/", "name": "炊飯器・精米機"},
	#		{"url": "/bc/category/001/153/020/", "name": "ケトル・ポット"},
			{"url": "/bc/category/001/100/009/", "name": "パソコン・タブレットPC"},
			{"url": "/bc/category/001/100/013/", "name": "ゲーミングパソコン・デバイス"},
			{"url": "/bc/category/001/100/012/", "name": "Mac・iPad・Apple関連"},
	#		{"url": "/bc/category/001/100/042/", "name": "パソコンアクセサリー"},
	#		{"url": "/bc/category/001/100/040/", "name": "タブレットPCアクセサリー"},
	#		{"url": "/bc/category/001/100/085/", "name": "モニター・ディスプレイ"},
			{"url": "/bc/category/001/100/150/", "name": "DOS/Vパーツ関連"},
	#		{"url": "/bc/category/001/130/005/", "name": "テレビ"},
	#		{"url": "/bc/category/001/130/015/", "name": "レコーダー"},
	#		{"url": "/bc/category/001/130/060/", "name": "プレーヤー"},
	#		{"url": "/bc/category/001/130/020/", "name": "プロジェクター"},
	#		{"url": "/bc/category/001/130/050/", "name": "ホームシアター"},
	#		{"url": "/bc/category/001/130/055/", "name": "VR・ヘッドマウントディスプレイ"},
	#		{"url": "/bc/category/001/140/003/", "name": "ハイレゾ対応オーディオ"}, # 実際は各種オーディオカテゴリでハイレゾ検索しているだけ
			{"url": "/bc/category/001/140/020/", "name": "イヤホン・ヘッドホン"},
			{"url": "/bc/category/001/140/030/", "name": "単品オーディオ・スピーカー・レコードプレーヤー"},
			{"url": "/bc/category/001/140/005/", "name": "デジタル・オーディオ"},
			{"url": "/bc/category/001/140/010/", "name": "iPod・iPod関連品"},
	#		{"url": "/bc/category/001/140/056/", "name": "ワイヤレススピーカー・アクティブスピーカー"},
	#		{"url": "/bc/category/001/140/045/", "name": "カーナビ・ドライブレコーダー・カー用品"},
	#		{"url": "/bc/category/001/160/040/005/010/", "name": "美顔器"},
	#		{"url": "/bc/category/001/160/040/", "name": "フェイスケア"},
	#		{"url": "/bc/category/001/160/050/005/015/", "name": "光美容器"},
	#		{"url": "/bc/category/001/160/050/", "name": "ボディケア用品"},
	#		{"url": "/bc/category/001/160/050/005/", "name": "脱毛器・除毛器(レディースシェーバー)"},
	#		{"url": "/bc/category/001/160/020/", "name": "ヘアケア"},
	#		{"url": "/bc/category/001/160/040/", "name": "フェイスケア"},
	#		{"url": "/bc/category/001/160/050/", "name": "ボディケア"},
	#		{"url": "/bc/category/001/160/085/", "name": "マッサージ"},
	#		{"url": "/bc/category/001/160/090/", "name": "デンタルケア"},
			{"url": "/bc/category/001/160/135/", "name": "ウェアラブル端末・歩数計"},
			{"url": "/bc/category/001/160/120/", "name": "電子タバコ"},
			{"url": "/bc/category/001/260/005/", "name": "メンズ腕時計"},
			{"url": "/bc/category/001/260/015/", "name": "レディース腕時計"},
			{"url": "/bc/category/001/260/175/", "name": "男女兼用腕時計"},
			{"url": "/bc/category/001/260/167/", "name": "Apple Watch"},
			{"url": "/bc/category/001/260/166/", "name": "ウェアラブル端末"},
	#		{"url": "/bc/category/001/260/035/", "name": "キッズ腕時計"},
	#		{"url": "/bc/category/001/260/125/", "name": "バッグ"},
	#		{"url": "/bc/category/001/260/145/", "name": "フレグランス"},
	#		{"url": "/bc/category/001/220/005/", "name": "男の子おもちゃ"},
	#		{"url": "/bc/category/001/220/010/", "name": "女の子おもちゃ"},
	#		{"url": "/bc/category/001/220/015/", "name": "知育・幼児玩具"},
	#		{"url": "/bc/category/001/220/200/", "name": "絵本・児童書・教育"},
	#		{"url": "/bc/category/001/220/017/", "name": "ランドセル・学習グッズ"},
	#		{"url": "/bc/category/001/220/210/", "name": "プログラム教育"},
	#		{"url": "/bc/category/001/220/008/", "name": "ヒーロー・キャラクターおもちゃ"},
	#		{"url": "/bc/category/001/220/025/", "name": "ブロック"},
	#		{"url": "/bc/category/001/220/006/", "name": "車・電車"},
	#		{"url": "/bc/category/001/220/070/", "name": "トレーディングカード・スリープ"},
	#		{"url": "/bc/category/001/220/021/", "name": "ラジコン"},
	#		{"url": "/bc/category/001/220/037/", "name": "ミニ四駆・ゲキドライブ"},
	#		{"url": "/bc/category/001/220/035/", "name": "プラモデル(模型)・工作シリーズ"},
	#		{"url": "/bc/category/001/220/040/", "name": "プラモデル制作用アイテム"},
			{"url": "/bc/category/001/220/020/", "name": "フィギュア・キャラクター"},
	#		{"url": "/bc/category/001/220/045/", "name": "鉄道模型(Nゲージ)・情景アイテム"},
	#		{"url": "/bc/category/001/220/055/", "name": "季節用品・おもちゃ"},
	#		{"url": "/bc/category/001/220/030/", "name": "ゲーム・バラエティ・パズル"},
	#		{"url": "/bc/category/001/220/060/", "name": "カードゲーム"},
	#		{"url": "/bc/category/001/220/065/", "name": "ボードゲーム"},
	#		{"url": "/bc/category/001/220/014/", "name": "ベビーカー"},
	#		{"url": "/bc/category/001/220/016/", "name": "チャイルドシート"},
	#		{"url": "/bc/category/001/220/050/", "name": "ベビー用品"},
			{"url": "/bc/category/001/240/020/", "name": "SIMフリースマートフォン"},
			{"url": "/bc/category/001/240/225/", "name": "SIMフリータブレット"},
	#		{"url": "/bc/category/001/240/028/", "name": "SIMフリールーター"},
	#		{"url": "/bc/category/001/240/015/", "name": "モバイルバッテリー"},
	#		{"url": "/bc/category/001/300/001/", "name": "エアコン(アウトレット)"},
	#		{"url": "/bc/category/001/300/002/", "name": "冷蔵庫・洗濯機(アウトレット)"},
	#		{"url": "/bc/category/001/300/003/", "name": "季節家電・空気清浄機(アウトレット)"},
	#		{"url": "/bc/category/001/300/004/", "name": "調理家電(アウトレット)"},
	#		{"url": "/bc/category/001/300/014/", "name": "キッチン用品・水筒・弁当箱(アウトレット)"},
	#		{"url": "/bc/category/001/300/016/", "name": "掃除機(アウトレット)"},
	#		{"url": "/bc/category/001/300/017/", "name": "家事家電(アウトレット)"},
	#		{"url": "/bc/category/001/300/018/", "name": "照明器具・電球(アウトレット)"},
	#		{"url": "/bc/category/001/300/006/", "name": "ビューティー家電・健康家電(アウトレット)"},
	#		{"url": "/bc/category/001/300/007/", "name": "TV・レコーダー(アウトレット)"},
			{"url": "/bc/category/001/300/008/", "name": "オーディオ・ドライブレコーダー(アウトレット)"},
	#		{"url": "/bc/category/001/300/009/", "name": "デジタルカメラ(アウトレット)"},
			{"url": "/bc/category/001/300/010/", "name": "パソコン・周辺機器・サプライ・OA(アウトレット)"},
	#		{"url": "/bc/category/001/300/011/", "name": "スーツケース、インテリア・バス用品(アウトレット)"},
	#		{"url": "/bc/category/001/300/012/", "name": "スポーツ・フィットネス(アウトレット)"},
		]
		# Parallel processing by count of CPU.
		itemListArray = Parallel(n_jobs = -1)([delayed(self.ObtainItemListByCategory)(category) for category in categories])
		self.itemList = [e for inner_list in itemListArray for e in inner_list]
