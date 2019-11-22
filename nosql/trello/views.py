from django.shortcuts import render
from django.views import View
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseNotFound
from django.shortcuts import redirect
import pymongo
from .forms import LinkForm, SettingsForm
# from datetime import datetime

from_start_page = False

class LinkGet(View):
	def get(self, request):
		global from_start_page
		from_start_page = False
		print("GET!")
		form = LinkForm()
		return render(request, 'trello/start_page.html', context={'form': form})

	def post(self, request):
		print("POST!")
		bound_form = LinkForm(request.POST)
		if bound_form.is_valid():
			new_link = bound_form.save()
			# Тут нужно выжать из этой ссылки на доску все данные и сохранить их в БД
			global from_start_page
			from_start_page = True
			return redirect('settings_page_url')
		return render(request, 'trello/start_page.html', context={'form': bound_form})

class SettingsGet(View):
	def get(self, request):
		print("GET!")
		if from_start_page:
			form = SettingsForm()
			return render(request, 'trello/settings_page.html', context={'form': form})
		else:
			return HttpResponseNotFound()


	def post(self, request):
		print("POST!")
		bound_form = SettingsForm(request.POST)
		if bound_form.is_valid():
			new_settings = bound_form.save()
			# Тут нужно передать полученные данные в функцию обработчик
			return redirect('settings_page_url') # страница загрузки PDF
		return render(request, 'trello/settings_page.html', context={'form': bound_form})

# class TestView(View):
#
# 	def get(self, request):
# 		# x = None
# 		# myclient = pymongo.MongoClient("mongodb://localhost:27017/")
# 		# mydb = myclient["mydatabase"]
# 		# mycol = mydb["customers"]
# 		# # mycol.delete_many({})
# 		# mydict = { "name": "Test", "date": str(datetime.now()) }
# 		# x = mycol.insert_one(mydict)
# 		# x = mycol.find()
# 		x = 0
# 		return HttpResponse(x)
