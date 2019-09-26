from django.shortcuts import render
from django.views import View
from django.http import HttpResponseRedirect, HttpResponse
import pymongo
from datetime import datetime

class TestView(View):

	def get(self, request):
		x = None
		myclient = pymongo.MongoClient("mongodb://localhost:27017/")
		mydb = myclient["mydatabase"]
		mycol = mydb["customers"]
		# mycol.delete_many({})
		mydict = { "name": "Test", "date": str(datetime.now()) }
		x = mycol.insert_one(mydict)
		x = mycol.find()
		return HttpResponse(x)
