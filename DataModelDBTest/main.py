from pymongo import MongoClient;
from datetime import datetime, timezone;
from pprint import pprint # Pretty printing
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

	# testTFBoard();
	testTestBoard();

def testTestBoard():
	boardId = 'VoCJJodK';
	## Uncomment to load data from board
	## (Very slow process)
	## Making Mongo database on that board using Trello API requests to get data:
	collection = TrelloToMongoAdapter(boardId, apiKey, tokenKey);

	collection = getCollection();

	cards = collection.find({
		'moves.toList': 'Previously Released',
		'moves.date': {'$gte': datetime(2019,10,8), '$lte': datetime(2019,10,9) }
	});
	print("Cards that were moved in done list at 2019.10.8:")
	for it in cards:
		print(" ", it['name'], len(it['comments']));

	# Карточка на конец периода осталась в целевом списке:
	Date1 = datetime(2019,10,29);
	Date2 = datetime(2019,11,30);
	toList = 'DEF'
	cards = collection.aggregate([
		{ '$project': { # Добавляем поле lastList,
			'name': '$name',
			'lastList': {
				'$filter': { # Фильтруем массив, чтобы он содержал только нужные нам записи по дате
					'input': '$moves',
					'as': 'move',
					'cond': { '$and': [
						{ '$gte': [ '$$move.date', Date1] },
						{ '$lt': [ '$$move.date', Date2] }
					]}
				}
			},
		}},
		{ '$project': { # Добавляем поле max,
			'name': '$name',
			'lastList': '$lastList',
			'max': { '$max': '$lastList.date' } # Содержащее дату последнего действия в заданном интервалеы
		}},
		{ '$project': {
			'name': '$name',
			'lastList': {
				'$filter': { # Фильтруем массив, чтобы он содержал только последнюю запись в заданном интервале
					'input': '$lastList',
					'as': 'move',
					'cond': { '$and': [
						{'$eq': ['$$move.date', '$max']},
						#{ '$eq': ['$$move.toList', ]} # Works other way than next aggregation stage
					]}
				}
			},
			'max': '$max'
		}},
		{ '$match': { # Убираем документы, конечный список которых не соответствует нужному
			'lastList.toList': toList
		}},
		{ '$count': 'count'	} # Считаем количество документов и заносим в поле count
		# Возвращаем документ с единственным полем count
	])
	number = cards.next()['count']
	print(number);
	# for it in cards:
	# 	print(it);
	# for it in cards:
	# 	pprint([it['name'], it['lastList'], it['max']], indent=2);

	Date3 = datetime(2019,10,25);
	Date4 = datetime(2019,10,31);
	member = "Denmey"
	commentsNumber = collection.aggregate([
		{ '$project': {
			"count": { "$size": { # We put in field 'count' size of
				'$filter': { # Filtered 'comments' array
					'input': '$comments',
					# Elements of which matches this conditions:
					'cond': {'$and': [
						{'$eq': ['$$this.member.fullName', member]},
						{'$gte': ['$$this.date', Date3]},
						{'$lt': ['$$this.date', Date4]},
					]}
				}
			}}
		}},
		{ '$group': { # Then group all documents
			'_id': None, # In one
			'comments': {'$push': '$count'},
			'number': {'$sum': '$count'}, # And sum of counts in each document is a new field 'number'
		}},
	])
	commentsNumber = commentsNumber.next()['number'];
	print("Comments number between dates", Date3, Date4, "from user", member + ":");
	print(commentsNumber);
	# for it in commentsNumber:
	# 	pprint(it)

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

	# Карточки, помещенные в список List за период с Date1 по Date2
	# (не проверяется, что карточка потом не была перемещена):
	# https://docs.mongodb.com/manual/tutorial/query-array-of-documents/
	# https://docs.mongodb.com/manual/reference/operator/query/elemMatch/#op._S_elemMatch
	# https://pymongo.readthedocs.io/en/stable/tutorial.html
	# datetime signature: (year, month, day, hour=0, minute=0, second=0)
	# cards = collection.find({
	# 	'moves': { '$elemMatch': {
	# 		'toList': 'Previously Released',
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
		print(" ", it['name'], len(it['comments']));

	# Карточка на конец периода осталась в целевом списке:


	print("Number of comments that were published between date1 and date2:");
	cardsN = collection.aggregate([
	# { '$filter': {
	# 	'comments.date': {'$gte': datetime(2019,10,8)}
	# }},
	]);
	# for it in cardsN:
	# 	print(len(it['comments']));

if __name__ == '__main__':
	main()
