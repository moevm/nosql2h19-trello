from django.shortcuts import render
from django.views import View
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseNotFound
from django.shortcuts import redirect

import pymongo
from datetime import datetime
import mimetypes
import os

from .APIKey import apiKey
from .TrelloUtility import TrelloUtility
from .TrelloToMongoAdapter import TrelloToMongoAdapter

from .forms import SettingsForm, BoardForm


board = None # название доски и ID в словаре
tokenKey = ""

class KeyGet(View):
	def get(self, request):
		global tokenKey
		tokenKey = ""
		return render(request, 'trello/start_page.html', context={})

	def post(self, request):
		return redirect('https://trello.com/1/authorize?callback_method=fragment&return_url={return_url}&expiration=1day&name=TrelloStatistic&scope=read&response_type=token&key={YourAPIKey}'.format(
				return_url=request.build_absolute_uri()+'next', YourAPIKey=apiKey))


class Next(View):
	def get(self, request):
		return render(request, 'trello/next_page.html', context={})

	def post(self, request):
		if(request.POST['token'] != ''):
			print(request.POST['token'])
			global tokenKey
			tokenKey = request.POST['token']
			return redirect('boards_page_url')
		else:
			return redirect('start_page_url')


class BoardGet(View):
	def get(self, request):
		if tokenKey:
			form = BoardForm()
			form.tokenKey = tokenKey
			return render(request, 'trello/boards_page.html', context={'form': form})
		else:
			return HttpResponseNotFound()

	def post(self, request):
		bound_form = BoardForm(request.POST)
		if bound_form.is_valid():
			global board
			board = bound_form.save()
			return redirect('settings_page_url')
		return render(request, 'trello/boards_page.html', context={'form': bound_form})


class SettingsGet(View):
	def get(self, request):
		if apiKey:
			# boardId = 'VoCJJodK'
			boardId =  board['boardID']
			collection = TrelloToMongoAdapter(boardId, apiKey, tokenKey)
			trello = TrelloUtility(apiKey, tokenKey)
			elems = trello.getBoardLists(boardId)
			form = SettingsForm()
			return render(request, 'trello/settings_page.html', context={'form': form})
		else:
			return HttpResponseNotFound()


	def post(self, request):
		bound_form = SettingsForm(request.POST)
		if bound_form.is_valid():
			# проверить что даты нормальные
			due_date = datetime.strptime(request.POST['due_date'], "%Y-%m-%d")
			from_date = datetime.strptime(request.POST['from_date'], "%Y-%m-%d")
			to_date = datetime.strptime(request.POST['to_date'], "%Y-%m-%d")
			new_settings = bound_form.save(due_date=due_date, from_date=from_date, to_date=to_date)
			new_settings.generate_statistic(board['boardName'])
			return redirect('download_page_url') # страница загрузки PDF
		return render(request, 'trello/settings_page.html', context={'form': bound_form})


class Download(View):
	def get(self, request):
		if apiKey:
			return render(request, 'trello/download_page.html', context={})
		else:
			return HttpResponseNotFound()

	def post(self, request):
		global tokenKey
		tokenKey = ""
		excel_file_name = './trello/statistic/Statistic.pdf'
		fp = open(excel_file_name, "rb")
		response = HttpResponse(fp.read())
		fp.close()
		file_type = mimetypes.guess_type(excel_file_name)
		if file_type is None:
			file_type = 'application/octet-stream'
		response['Content-Type'] = file_type
		response['Content-Length'] = str(os.stat(excel_file_name).st_size)
		response['Content-Disposition'] = "attachment; filename=Statistic.pdf"

		return response