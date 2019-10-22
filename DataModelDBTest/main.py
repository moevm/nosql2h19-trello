import pymongo;
import json; # For json parsing and pretty json printing
from urllib import request, parse; # For REST-requests

# Keys from trello:
from APIKey import apiKey;
from tokenKey import tokenKey;

def getBoards(apiKey, tokenKey):
	url = "https://api.trello.com/1/members/me/boards?fields=name,url&key={}&token={}" \
		.format(apiKey, tokenKey);
	print(url);
	reqAnswer = request.urlopen(url).read().decode('utf-8');
	data = json.loads(reqAnswer);

	return data;

	# Print received data in readable format:
	prettyData = json.dumps(data, indent=3);
	print("Received boards:");
	print(prettyData);

def getBoardInfo(id, apiKey, tokenKey):
	url = "https://api.trello.com/1/boards/{}?key={}&token={}" \
		.format(id, apiKey, tokenKey);
	data = json.loads(request.urlopen(url).read().decode('utf-8'));

	return data;

	prettyData = json.dumps(data, indent=3);
	print("Info on board", data['name'], ":");
	print("", prettyData);

def main():
	# TODO: make class with those functions that keeps api and token keys
	#       and remove them from the function args?
	boards = getBoards(apiKey, tokenKey);
	boardId = boards[0]['id'];
	getBoardInfo(boardId, apiKey, tokenKey);


if __name__ == '__main__':
	main()
