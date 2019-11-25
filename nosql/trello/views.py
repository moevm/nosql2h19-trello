from django.shortcuts import render
from django.views import View
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseNotFound
from django.shortcuts import redirect
import pymongo

from .APIKey import apiKey
from .tokenKey import tokenKey
from .TrelloUtility import TrelloUtility

from .forms import LinkForm, SettingsForm





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
			boardId = 'VoCJJodK'
			## Uncomment to load data from board
			## (Very slow process)
			## Making Mongo database on that board using Trello API requests to get data:
			# collection = TrelloToMongoAdapter(boardId, apiKey, tokenKey)
			trello = TrelloUtility(apiKey, tokenKey)
			elems = trello.getBoardLists(boardId)

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
			print("Valid!")
			new_settings = bound_form.save()
			# Тут нужно передать полученные данные в функцию обработчик
			new_settings.generate_statistic()
			return redirect('settings_page_url') # страница загрузки PDF
		return render(request, 'trello/settings_page.html', context={'form': bound_form})