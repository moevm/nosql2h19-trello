import json; # For json parsing and pretty json printing
from urllib import request, parse; # For REST-requests

# Implements various functions that help getting data from trello boards.
class TrelloUtility:

	def __init__(self, api, token):
		self.api = api;
		self.token = token;

	# Auxiliary function for sending requests to Trello.
	# Returns received data
	# Add wrong ids/keys exceptions?
	def sendRequest(self, params, fields=""):
		keyTokenStr = "key={}&token={}" \
			.format(self.api, self.token)

		fieldsStr = ""
		if (fields != ""):
			fieldsStr = "&fields=" + fields

		url = "https://api.trello.com/1/" + params + "?" + keyTokenStr + fieldsStr
		data = json.loads(request.urlopen(url).read().decode('utf-8'));

		return data;

	## Getters for boards ##

	def getBoards(self, fields="name,url"):
		params = "members/me/boards";
		data = self.sendRequest(params, fields);

		return data;

		# Print received data in readable format:
		prettyData = json.dumps(data, indent=3);
		print("Received boards:");
		print(prettyData);

	def getBoardInfo(self, boardId, fields=""):
		params = "boards/{}".format(boardId);
		data = self.sendRequest(params, fields);

		return data;

	def getBoardMembers(self, boardId, fields=""):
		params = "boards/{}/members".format(boardId);
		data = self.sendRequest(params, fields);

		return data;

	def getBoardActions(self, boardId, fields=""):
		params = "boards/{}/actions".format(boardId);
		data = self.sendRequest(params, fields);

		return data;

	def getBoardLists(self, boardId, fields="name"):
		params = "boards/{}/lists".format(boardId);
		data = self.sendRequest(params, fields);

		return data;

	## Getters for lists ##

	def getListCards(self, listId, fields=""):
		params = "lists/{}/cards".format(listId);
		data = self.sendRequest(params, fields);

		return data;

	## Getters for cards ##

	def getCardInfo(self, cardId, fields=""):
		params = "cards/{}".format(cardId);
		data = self.sendRequest(params, fields);

		return data;

	def getCardLabels(self, cardId, fields=""):
		params = "cards/{}/labels".format(cardId);
		data = self.sendRequest(params, fields);

		return data;
