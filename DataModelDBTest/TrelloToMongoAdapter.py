from pymongo import MongoClient
from TrelloUtility import TrelloUtility
from bson.objectid import ObjectId;
from json import dumps;
# Gets board id and returns mongoDB with data
def TrelloToMongoAdapter(boardId, apiKey, tokenKey):
	trello = TrelloUtility(apiKey, tokenKey);
	client = MongoClient();

	db = client.db;

	collection = db.cardsCollection;

	# print("Removing collection:");
	# for t in collection.find():
	# 	print(t);

	collection.remove();

	# For each list
	for list in trello.getBoardLists(boardId):
		# print(list['name']);
		# For each card
		for card in trello.getListCards(list['id'], "name,desc,due"):
			cardId = card['id']
			print(" ", list['name'], card['name']);
			# Get creation date:
			# creationDate = trello.getCardCreationDate(cardId);
			# print(creationDate);
			# break;

			# For each member
			print("   Members:");
			members = [];
			for member in trello.getCardMembers(cardId): # √
				# print("    ", member);
				memberDoc = {
					'_id': ObjectId(member['id']),
					'fullName': member['fullName'],
					'username': member['username']
				}
				members.append(memberDoc)

			# For each move
			moves = [];
			print("   Moves:");
			for move in trello.getCardMoves(cardId): # √
				memberDoc = None; # Some comments don't have authors? Deleted accounts?
				if ('memberCreator' in move):
					memberDoc = {
						'_id': ObjectId(move['memberCreator']['id']),
						'fullName': move['memberCreator']['fullName'],
						'username': move['memberCreator']['username']
					};
				moveDoc = {
					'_id': ObjectId(move['id']),
					'date': move['date'],
					'member': memberDoc,
					'fromList': move['data']['listBefore']['name'],
					'toList': move['data']['listAfter']['name'],
				};
				# print("    ", move);
				moves.append(moveDoc);

			# For each label
			print("   Labels:");
			labels = [];
			for label in trello.getCardLabels(cardId): # √
				# print("    ", label);
				labelDoc = {
					'_id': ObjectId(label['id']),
					'name': label['name'],
					'color': label['color']
				};
				labels.append(labelDoc);

			# For each comment
			print("   Comments:");
			comments = [];
			for comment in trello.getCardComments(cardId, "type,memberCreator,date"): # √
				# print("    ", comment);
				memberDoc = None; # Some comments don't have authors? Deleted accounts?
				if ('memberCreator' in comment):
					memberDoc = {
						'_id': ObjectId(comment['memberCreator']['id']),
						'fullName': comment['memberCreator']['fullName'],
						'username': comment['memberCreator']['username']
					};
				commentDoc = {
					'_id': ObjectId(comment['id']),
					'member': memberDoc,
					'date': comment['date']
				};
				comments.append(commentDoc);

			# For each attachment
			print("   Attachments:");
			attachments = [];
			for attachment in trello.getCardAttachments(cardId):
				# print("    ", attachment);
				member = trello.getMember(attachment['idMember'], "fullName,username");
				# print("    attMember:", member)
				memberDoc = None;
				if (member != None):
					memberDoc = {
						'_id': ObjectId(member['id']),
						'fullName': member['fullName'],
						'username': member['username']
					};
				attachmentDoc = {
					'_id': ObjectId(attachment['id']),
					'date': attachment['date'],
					'member': memberDoc
				};

				attachments.append(attachmentDoc);

			collection.insert_one({
				'_id': ObjectId(card['id']),
				'name': card['name'],
				'description': card['desc'],
				'created': None,
				'dueTo': card['due'],
				'currentList': list['name'],
				'members': members,
				'moves': moves,
				'labels': labels,
				'comments': comments,
				'attachments': attachments
			})
