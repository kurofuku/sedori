# -*- coding: utf-8 -*-

import os
import syslog
import requests
from lxml import html
import re
import time
import pandas as pd

timeout = 120
diff = 0.1

csvFileName = "/tmp/result.csv"
xlsxFileName = "/tmp/result.xlsx"

def GetKakakuComInfo(ModelName):
	if 0 == len(ModelName):
		return None, None
	if "None" == ModelName:
		return None, None
	ret = 99999999
	url = ""
	print("To get the kakaku.com price of " + ModelName)
	response = requests.get("http://kakaku.com/search_results/" + ModelName + "/", timeout = timeout)
	if requests.codes.ok != response.status_code:
		return None, None
	doc = html.fromstring(response.text)
	for priceTag in doc.xpath("//span[contains(@class, 'c-num p-item_price_num')]"):
		price = priceTag.text
		print("price = " + price)
		if re.search("¥([1-9]?[0-9]*)?(,[0-9]{1,3})*", price) is not None and "" != price:
			print("case 1")
			p = int(re.search("¥([1-9]?[0-9]*)?(,[0-9]{1,3})*", price).group(0).replace(",", "").replace("¥¥", "").replace("¥", ""))
			if ret > p:
				linkAttr = priceTag.xpath("../../../preceding-sibling::div[@class='c-positioning_cell p-result_item_cell-1']/div/p/a/@href")
				if 0 < len(linkAttr) and (not "redirect" in linkAttr[0]):
					ret = p
					url = linkAttr[0]
		else:
			print("case 2")
	if 99999999 != ret:
		return ret, url
	else:
		return None, None

def GetAucFanPrice(ModelName):
	if 0 == len(ModelName):
		return None
	if "None" == ModelName:
		return None
	ret = {"min": 99999999, "max": 0}
	response = requests.get("https://aucfan.com/search1/q-" + ModelName + "/s-mix/?shipping=all&o=p1&location=0", timeout = timeout)
	if requests.codes.ok != response.status_code:
		return None
	doc = html.fromstring(response.text)
	for priceTag in doc.xpath("//span[@class='amount']"):
		price = priceTag.text
		if re.search("[1-9]+(,[0-9]{1,3})*", price) is not None:
			p = int(re.search("[1-9]+(,[0-9]{1,3})*", price).group(0).replace(",", ""))
			ret["min"] = ret["min"] if ret["min"] < p else p
			ret["max"] = ret["max"] if ret["max"] > p else p
	if 99999999 != ret["min"] and 0 != ret["max"]:
		return ret
	else:
		return None

def OutputAsCsv(filename, itemList):
	with open(filename, mode = 'w', encoding = 'utf-8') as f:
		line = '"Shop","Category","Product","Name","Price","Point","Percentage","URL","kakaku.com price","kakaku.com URL","aucfan.com"\n'
		f.write(line)
		for item in itemList:
			price = int(item["price"])
			if "kakakucom" in item.keys():
				kakakucom = int(item["kakakucom"])
				if diff < (price - kakakucom) / price:
					continue
			line = '"%s","%s","%s","%s","%s","%s","%s","%s"' % (item["shop"], item["category"], item["product"].replace(",", ""), item["name"], item["price"], item["point"], str((int(item["point"]) * 100)//int(item["price"])), item["url"])
			if "kakakucomPrice" in item.keys():
				line += ",\"" + item["kakakucomPrice"] + "\""
				line += ",\"" + item["kakakucomUrl"] + "\""
			else:
				line += ",\"None\""
				line += ",\"None\""
			line += ",\"" + item["aucfan"] + "\"" if "aucfan" in item.keys() else ",\"None\""
			line += "\n"
			f.write(line)

def main():

	import YamadaWebCom
	import BicCamera
	import Rakuten
	import YodobashiCamera

	syslog.openlog(logoption = syslog.LOG_PID)
	syslog.syslog("Process start.")

	start = time.time()

	os.chdir(os.path.dirname(os.path.abspath(__file__)))

	itemList = []
	shopList = []
	shopList.append(YamadaWebCom.YamadaWebCom())
	shopList.append(BicCamera.BicCamera())
	shopList.append(Rakuten.Rakuten())
	shopList.append(YodobashiCamera.YodobashiCamera())

	for shop in shopList:
		shop.UpdateItemList()
		itemList.extend(shop.GetItemList())

	for item in itemList:
		kakakuComPrice, kakakuComUrl = GetKakakuComInfo(item["name"])
		if None is not kakakuComPrice:
			item["kakakucomPrice"] = str(kakakuComPrice)
			item["kakakucomUrl"] = kakakuComUrl
		aucFanPrice = GetAucFanPrice(item["name"])
		if None is not aucFanPrice:
			item["aucfan"] = "%d-%d" % (aucFanPrice["min"], aucFanPrice["max"])

	OutputAsCsv(csvFileName, itemList)

	data = pd.read_csv(csvFileName)
	data.to_excel(xlsxFileName, encoding = 'utf-8')
	os.remove(csvFileName)

	from pydrive.auth import GoogleAuth
	from pydrive.drive import GoogleDrive

	gauth = GoogleAuth()
	gauth.CommandLineAuth()
	drive = GoogleDrive(gauth)

	f = drive.CreateFile(
		{
			'id': '1M5g1VlCBWdawEsImHEieIyLk_fiv2b3Y',
			'title': os.path.basename(xlsxFileName),
			'mimeType': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
		}
	)
	f.SetContentFile(xlsxFileName)
	f.Upload()
	os.remove(xlsxFileName)

	end = time.time()
	elapsed_time = end - start
	print(f"elapsed time = {elapsed_time}(s)")
	syslog.syslog("elapsed time = {}".format(elapsed_time))

main()
