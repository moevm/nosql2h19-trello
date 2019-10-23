import json; # For json parsing and pretty json printing
from urllib import request, parse; # For REST-requests

# Implements various functions that help getting data from trello boards.
class TrelloUtility:
	# Add wrong ids/keys exceptions?

	def __init__(self, api, token):
		self.api = api;
		self.token = token;

	def getBoards(self):
		url = "https://api.trello.com/1/members/me/boards?fields=name,url&key={}&token={}" \
			.format(self.api, self.token);
		reqAnswer = request.urlopen(url).read().decode('utf-8');
		data = json.loads(reqAnswer);

		return data;

		# Print received data in readable format:
		prettyData = json.dumps(data, indent=3);
		print("Received boards:");
		print(prettyData);

	def getBoardActions(self, boardId):
		url = "https://api.trello.com/1/boards/{}/actions?key={}&token={}" \
			.format(boardId, self.api, self.token);
		data = json.loads(request.urlopen(url).read().decode('utf-8'));

		return data;

	def getBoardInfo(self, boardId):
		url = "https://api.trello.com/1/boards/{}?key={}&token={}" \
			.format(boardId, self.api, self.token);
		data = json.loads(request.urlopen(url).read().decode('utf-8'));

		return data;

		prettyData = json.dumps(data, indent=3);
		print("Info on board", data['name'], ":");
		print("", prettyData);

	def getListsOnBoard(self, boardId):
		# Full info on each list
		# url = "https://api.trello.com/1/boards/{}/lists?key={}&token={}" \
		# Only id, name and board id
		url = "https://api.trello.com/1/boards/{}/lists?fields=name,idBoard&key={}&token={}" \
			.format(boardId, self.api, self.token);
		data = json.loads(request.urlopen(url).read().decode('utf-8'));

		return data;

		print(json.dumps(data, indent=3)); # Cyrrilic printing is weird because of encoding, but data is okay.

	def getCardsOnList(self, listId):
		url = "https://api.trello.com/1/lists/{}/cards?key={}&token={}" \
			.format(listId, self.api, self.token);
		data = json.loads(request.urlopen(url).read().decode('utf-8'));

		return data;

		print(json.dumps(data, indent=3));

	def getCardInfo(self, cardId):
		url = "https://api.trello.com/1/cards/{}?key={}&token={}" \
			.format(cardId, self.api, self.token);
		data = json.loads(request.urlopen(url).read().decode('utf-8'));

		return data;

		print(json.dumps(data, indent=3));
