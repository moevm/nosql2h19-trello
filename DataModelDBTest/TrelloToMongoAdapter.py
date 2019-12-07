from pymongo import MongoClient
from TrelloUtility import TrelloUtility
from bson.objectid import ObjectId;
from json import dumps;
from datetime import datetime;
from pprint import pprint;

def strToDatetime(str):
	return datetime.strptime(str, "%Y-%m-%dT%H:%M:%S.%fZ");
# Gets board id and returns mongoDB with data
def TrelloToMongoAdapter(boardId, apiKey, tokenKey):
	trello = TrelloUtility(apiKey, tokenKey);
	client = MongoClient();

	db = client.db;


	collection = db.TrelloStats_cards;
	collection.remove();

	# Adding collections for members, lists and ?labels?
	membersCollection = db.TrelloStats_members;
	membersCollection.remove();
	boardMembers = trello.getBoardMembers(boardId, fields="");
	for i in boardMembers:
		i['_id'] = i.pop('id');
	membersCollection.insert_many(boardMembers);
	listsCollection = db.TrelloStats_lists;
	listsCollection.remove();
	lists = trello.getBoardLists(boardId, fields="name");
	for i in lists:
		i['_id'] = i.pop('id');
	listsCollection.insert_many(lists);
	labelsCollection = db.TrelloStats_labels;
	labelsCollection.remove();
	labels = trello.getBoardLabels(boardId, fields="name,color");
	for i in labels:
		i['_id'] = i.pop('id');
	# pprint(labels);
	labelsCollection.insert_many(labels);

	# For each list
	for list in trello.getBoardLists(boardId):
		# print(list['name']);
		# For each card
		for card in trello.getListCards(list['id'], "name,desc,due,badges"):
			cardId = card['id']
			print(" ", list['name'], "|", card['name']);
			# Get creation date:
			# creationDate = trello.getCardCreationDate(cardId);
			# print(creationDate);
			# break;
			# print("   Get card info:");
			[cardMembers, cardMoves, cardLabels, cardComments, cardAttachments] = trello.getCardSubInfo(cardId);
			# For each member
			# print("   Members:");
			members = [];
			for member in cardMembers:
				members.append({
					'_id': ObjectId(member['id']),
					'fullName': member['fullName'],
					'username': member['username']
				})
			# For each move
			moves = [];
			# print("   Moves:");
			for move in cardMoves:
				memberDoc = None; # Some comments don't have authors? Deleted accounts?
				if ('memberCreator' in move):
					memberDoc = {
						'_id': ObjectId(move['memberCreator']['id']),
						'fullName': move['memberCreator']['fullName'],
						'username': move['memberCreator']['username']
					};
				moves.append({
					'_id': ObjectId(move['id']),
					'date': strToDatetime(move['date']),
					'member': memberDoc,
					'fromList': move['data']['listBefore']['name'],
					'toList': move['data']['listAfter']['name'],
				});

			# For each label
			# print("   Labels:");
			labels = [];
			for label in cardLabels:
				labels.append({
					'_id': ObjectId(label['id']),
					'name': label['name'],
					'color': label['color']
				});

			# For each comment
			# print("   Comments:");
			comments = [];
			for comment in cardComments:
				memberDoc = None; # Some comments don't have authors? Deleted accounts?
				if ('memberCreator' in comment):
					memberDoc = {
						'_id': ObjectId(comment['memberCreator']['id']),
						'fullName': comment['memberCreator']['fullName'],
						'username': comment['memberCreator']['username']
					};
				comments.append({
					'_id': ObjectId(comment['id']),
					'member': memberDoc,
					'date': strToDatetime(comment['date'])
				});
			# print(comments);
			# For each attachment
			# print("   Attachments:");
			attachments = [];
			for attachment in cardAttachments:
				# member = trello.getMember(attachment['idMember'], "fullName,username");
				memberDoc = None;
				for i in boardMembers:
					if i['_id'] == attachment['idMember']:
						memberDoc = i;
						break;
				attachments.append({
					'_id': ObjectId(attachment['id']),
					'date': strToDatetime(attachment['date']),
					'member': memberDoc
				});
			# print(attachments);

			if (card['badges']['due'] == None or card['badges']['dueComplete'] == True):
				due = None;
			else:
				due = strToDatetime(card['badges']['due']);

			collection.insert_one({
				'_id': ObjectId(card['id']),
				'name': card['name'],
				'description': card['desc'],
				'created': ObjectId(card['id']).generation_time,
				'dueTo': due,
				'currentList': list['name'],
				'members': members,
				'moves': moves,
				'labels': labels,
				'comments': comments,
				'attachments': attachments
			})

def getDB():
	client = MongoClient();
	return client.db;

def getCollection():
	client = MongoClient();
	db = client.db;
	collection = db.TrelloStats_cardsCollection;
	return collection;
