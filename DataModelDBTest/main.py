from pymongo import MongoClient;
from datetime import datetime, timezone;
import json;
# Keys from trello, should be kept in private:
from APIKey import apiKey;
from tokenKey import tokenKey;

from TrelloUtility import TrelloUtility
from TrelloToMongoAdapter import TrelloToMongoAdapter, getCollection

def main():
	# LOTR board from MMZ's example. Not really an id, but a short-link.
	# boardId = 'tLvDmGT5'; # Board is copied from another one, so there's no 'create card' actions and adapter can't fill in creation date
	# My test board:
	# boardId = 'VoCJJodK';

	# https://trello.com/b/qhgryS9a/
	# Id of the board:
	# boardId = 'qhgryS9a'

	testTFBoard();

def testTFBoard():
	boardId = 'AddXFWee';
	## Uncomment to load data from board
	## (Very slow process)
	## Making Mongo database on that board using Trello API requests to get data:
	# collection = TrelloToMongoAdapter(boardId, apiKey, tokenKey);

	# Working with MongoDB collection here:
	collection = getCollection();
	print("Documents in collection:", collection.count_documents({}));
	db = collection.database;
	stats = db.command("collstats", collection.name);
	print("Collection size:", stats['size']);
	print("Collection document avg size:", stats['avgObjSize']);

	# Trying to find something:
	WIPListCards = collection.find({
		'currentList': 'Work In Progress'
	});

	print("Cards in work in progress list:");
	for it in WIPListCards:
		print("  " + it['name']);

	# Карточки, помещенные в список List за период с Date1 по Date2:
	# https://docs.mongodb.com/manual/tutorial/query-array-of-documents/
	# https://docs.mongodb.com/manual/reference/operator/query/elemMatch/#op._S_elemMatch
	# https://pymongo.readthedocs.io/en/stable/tutorial.html
	# datetime signature: (year, month, day, hour=0, minute=0, second=0)
	# cards = collection.find({
	# 	'moves': { '$elemMatch': {
	# 		'toList': 'Previously Released',
	# 		# 'date': datetime(2019,10,8)
	# 		'date': {'$lte': datetime(2029,10,9), '$gte': datetime(2019,10,8)}
	# 	}}
	# });
	# Same thing:
	cards = collection.find({
		'moves.toList': 'Previously Released',
		'moves.date': {'$gte': datetime(2019,10,8), '$lte': datetime(2019,10,9) }
	});
	print("Cards that were moved in done list at 2019.10.8:")
	for it in cards:
		print("  " + it['name']);

if __name__ == '__main__':
	main()
