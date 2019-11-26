from django.shortcuts import render
from django.views import View
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseNotFound
from django.shortcuts import redirect

import pymongo
from datetime import datetime
import mimetypes
import os

from .APIKey import apiKey
from .tokenKey import tokenKey
from .TrelloUtility import TrelloUtility

from .forms import LinkForm, SettingsForm



from_start_page = False
board_link = None

class LinkGet(View):
	def get(self, request):
		global from_start_page
		from_start_page = False
		form = LinkForm()
		return render(request, 'trello/start_page.html', context={'form': form})

	def post(self, request):
		bound_form = LinkForm(request.POST)
		if bound_form.is_valid():
			global board_link
			board_link = bound_form.save()

			global from_start_page
			from_start_page = True
			return redirect('https://trello.com/1/authorize?callback_method=fragment&return_url={return_url}&expiration=1day&name=TrelloStatistic&scope=read&response_type=token&key={YourAPIKey}'.format(
				return_url=request.build_absolute_uri()+'settings', YourAPIKey=apiKey))
		return render(request, 'trello/start_page.html', context={'form': bound_form})


class SettingsGet(View):
	def get(self, request):
		print("get")
		if from_start_page:
			boardId = 'VoCJJodK' # board_link.boardID
			## Uncomment to load data from board
			## (Very slow process)
			## Making Mongo database on that board using Trello API requests to get data:
			# collection = TrelloToMongoAdapter(board_link.boardID, apiKey, tokenKey)
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
			new_settings.generate_statistic(board_link.boardName)
			return redirect('download_page_url') # страница загрузки PDF
		return render(request, 'trello/settings_page.html', context={'form': bound_form})


class Download(View):
	def get(self, request):
		if from_start_page:
			return render(request, 'trello/download_page.html', context={})
		else:
			return HttpResponseNotFound()

	def post(self, request):
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