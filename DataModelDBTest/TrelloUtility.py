import json; # For json parsing and pretty json printing
from urllib import request, parse, error; # For REST-requests
# import urllib;

# Implements various functions that help getting data from trello boards.
class TrelloUtility:

	def __init__(self, api, token):
		self.api = api;
		self.token = token;

	def checkBoard(self, boardId):
		try:
			data = self.sendRequest("boards/{}".format(boardId), "id");
			return True;
		except error.HTTPError:
			return False;
		print(data);

	# Auxiliary function for sending requests to Trello.
	# Returns received data
	# Add wrong ids/keys exceptions?
	def sendRequest(self, params, fields="", filter="", batch=""):
		keyTokenStr = "key={}&token={}" \
			.format(self.api, self.token)

		fieldsStr = ""
		if (fields != ""):
			fieldsStr = "&fields=" + fields
		filterStr = "";
		if (filter != ""):
			filterStr = "&filter=" + filter;

		url = "https://api.trello.com/1/" + params + "?" + batch + "&" + keyTokenStr + fieldsStr + filterStr;
		# url = urllib.quote(url);
		# print(url);
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

	def getBoardLabels(self, boardId, fields="name,color"):
		params = "boards/{}/labels".format(boardId);
		data   = self.sendRequest(params, fields);

		return data;

	## Getters for lists ##
	def getListInfo(self, listId, fields=""):
		params = "lists/{}".format(listId);
		data = self.sendRequest(params, fields);

		return data;

	def getListCards(self, listId, fields=""):
		params = "lists/{}/cards".format(listId);
		data = self.sendRequest(params, fields);

		return data;

	## Getters for cards ##

	def getCardInfo(self, cardId, fields=""):
		params = "cards/{}".format(cardId);
		data = self.sendRequest(params, fields);

		return data;

	def getCardSubInfo(self, cardId):
		# trello.getCardMembers(cardId);
		# trello.getCardMoves(cardId);
		# trello.getCardLabels(cardId);
		# trello.getCardComments(cardId, "type,memberCreator,date");
		# trello.getCardAttachments(cardId);
		# 	trello.getMember(attachment['idMember'], "fullName,username");
		batch = "urls=\
/cards/{cardId}/members/,\
/cards/{cardId}/actions/,\
/cards/{cardId}/labels/,\
/cards/{cardId}/attachments/"\
		.format(cardId=cardId);
		data = self.sendRequest("batch", batch=batch);
		# for i in data:
		# 	print(i);
		if ('200' in data[0]):
			members = data[0]['200'];
		# print("Members:", members);
		if ('200' in data[1]):
			actions = data[1]['200'];
		# print("Actions:", actions);
		if ('200' in data[2]):
			labels = data[2]['200'];
		# print("Labels:", labels);
		if ('200' in data[3]):
			attachments = data[3]['200'];
		# print("Attachments:", attachments);
		# filter moves
		filterFunction = lambda x : ((x['type'] == 'updateCard') and ('listAfter' in x['data']));
		moves = list(filter(filterFunction, actions));

		# filter comments
		filterFunction = lambda x : ((x['type'] == 'commentCard'));
		comments = list(filter(filterFunction, actions));

		return [members, moves, labels, comments, attachments];


	def getCardLabels(self, cardId, fields=""):
		params = "cards/{}/labels".format(cardId);
		data = self.sendRequest(params, fields);

		return data;

	def getCardMembers(self, cardId, fields=""):
		params = "cards/{}/members".format(cardId);
		data = self.sendRequest(params, fields);

		return data;

	def getCardAttachments(self, cardId, fields=""):
		params = "cards/{}/attachments".format(cardId);
		data = self.sendRequest(params, fields);

		return data;

	def getCardMoves(self, cardId, fields="data,type,date"):
		params = "cards/{}/actions".format(cardId);
		if (fields != "" and 'type' not in fields):
			fields += ",type";
		data = self.sendRequest(params, fields);
		# print(data);
		filterFunction = lambda x : ((x['type'] == 'updateCard') and ('listAfter' in x['data']));
		filteredList = list(filter(filterFunction, data));

		return filteredList;

	def getCardComments(self, cardId, fields=""):
		params = "cards/{}/actions".format(cardId);
		if (fields != "" and 'type' not in fields):
			fields += ",type";
		data = self.sendRequest(params, fields);

		filterFunction = lambda x : ((x['type'] == 'commentCard'));
		filteredList = list(filter(filterFunction, data));

		return filteredList;

	# Doesn't work.
	def getCardCreationDate(self, cardId, fields=""):
		params = "cards/{}/actions".format(cardId);
		# if (fields != "" and 'type' not in fields):
		# 	fields += ",type";
		# data = self.sendRequest(params, fields, "type eq \"createCard\"");

		# filterFunction = lambda x : ((x['type'] == 'commentCard'));
		# filteredList = list(filter(filterFunction, data));

		return data;

	## Getters for members ##
	def getMember(self, memberId, fields=""):
		params = "members/{}".format(memberId);
		# If there's no such member anymore(deleted account?), 404 exception.
		try:
			data = self.sendRequest(params, fields);
		except error.HTTPError as e:
			if (e.code == 404):
				data = None;
			else:
				raise;
		return data;
