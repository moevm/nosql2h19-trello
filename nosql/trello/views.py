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
from .TrelloToMongoAdapter import TrelloToMongoAdapter, getDB
from .MongoDBUtility import getLists, getLabels, getMembers, saveDBToFile, loadDBFromFile

from .forms import SettingsForm, BoardForm, FileForm
from .models import Settings


board = None # название доски и ID в словаре
tokenKey = ""
date_error = False
from_file = False


class KeyGet(View):
	def get(self, request):
		global tokenKey
		tokenKey = ""
		global from_file
		from_file = False
		return render(request, 'trello/start_page.html', context={'file_form': FileForm()})

	def post(self, request):
		return redirect('https://trello.com/1/authorize?callback_method=fragment&return_url={return_url}&expiration=1day&name=TrelloStatistic&scope=read&response_type=token&key={YourAPIKey}'.format(
				return_url=request.build_absolute_uri()+'next', YourAPIKey=apiKey))


class Next(View):
	def get(self, request):
		return render(request, 'trello/next_page.html', context={})

	def post(self, request):
		if(request.POST['token'] != ''):
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
		if apiKey or from_file:
			if tokenKey:
				boardId =  board['boardID']
				collection = TrelloToMongoAdapter(boardId, apiKey, tokenKey)
				trello = TrelloUtility(apiKey, tokenKey)
				elems = trello.getBoardLists(boardId)
				# ---------------------
			db = getDB()
			lists = []
			labels = []
			members = []
			tmp = getLists(db)
			for d in tmp:
				lists.append((d['name'], d['name']))
			tmp = getLabels(db)
			for d in tmp:
				labels.append(("{color}${name}".format(color=d['color'], name=d['name']),
									"{color} ({name})".format(color=d['color'], name=d['name'])))
			tmp = getMembers(db)
			for d in tmp:
				members.append(("{fullName}".format(fullName=d['fullName']),
									 "{fullName} ({username})".format(fullName=d['fullName'], username=d['username'])))
			form = SettingsForm(lists=lists, labels=labels, members=members)
			return render(request, 'trello/settings_page.html', context={'form': form, 'date_error': date_error})

		else:
			return HttpResponseNotFound()

	def post(self, request):
		bound_form = SettingsForm(request.POST)
		due_date = datetime.strptime(request.POST['due_date'], "%Y-%m-%d")
		from_date = datetime.strptime(request.POST['from_date'], "%Y-%m-%d")
		to_date = datetime.strptime(request.POST['to_date'], "%Y-%m-%d")
		global date_error
		if(to_date<=from_date):
			date_error = True
			return render(request, 'trello/settings_page.html', context={'form': bound_form, 'date_error': date_error})
		date_error = False
		new_settings = Settings(start_list=request.POST.getlist('start_list'),
				                             key_words=request.POST['key_words'].split(),
				                             labels=request.POST.getlist('labels'),
				                             executors=request.POST.getlist('executors'),
				                             due_date=due_date,
				                             from_date=from_date,
				                             to_date=to_date,
				                             attachment=request.POST.get('attachment', False),
				                             comments=request.POST.get('comments', False))
		boardName = "";
		if tokenKey:
			new_settings.generate_statistic(board['boardName'])
		return redirect('download_page_url') # страница загрузки PDF


class Download(View):
	def get(self, request):
		if apiKey or from_file:
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


class Import(View):
	def get(self, request):
		return redirect('start_page_url')

	def post(self, request):
		print("FILE!")
		print(request.FILES)
		form = FileForm(request.POST, request.FILES)
		if form.is_valid():
			global from_file
			from_file = True
			print("FILE!")
			print(request.FILES)
			f = request.FILES['file']
			with open('./trello/JSON/import.txt', 'wb+') as destination:
				for chunk in f.chunks():
					destination.write(chunk)
			loadDBFromFile(getDB(), './trello/JSON/import.txt')
		# загрузка данных файла в БД
		return redirect('settings_page_url')


class Export(View):
	def get(self, request):
		return redirect('download_page_url')

	def post(self, request):
		# выгрузить статистику из БД
		excel_file_name = './trello/JSON/export.txt'
		saveDBToFile(getDB(), excel_file_name)
		fp = open(excel_file_name, "rb")
		response = HttpResponse(fp.read())
		fp.close()
		file_type = mimetypes.guess_type(excel_file_name)
		if file_type is None:
			file_type = 'application/octet-stream'
		response['Content-Type'] = file_type
		response['Content-Length'] = str(os.stat(excel_file_name).st_size)
		response['Content-Disposition'] = "attachment; filename=export.txt"
		return response
