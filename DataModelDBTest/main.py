# from pymongo import MongoClient;
from datetime import datetime, timezone, timedelta;
from pprint import pprint # Pretty printing
import json;

# from bson.json_util import dumps

# Keys from trello, should be kept in private:
from APIKey import apiKey;
from tokenKey import tokenKey;
from TrelloUtility import TrelloUtility

from TrelloToMongoAdapter import TrelloToMongoAdapter, getCollection, getDB;
from MongoDBUtility import *;

def main():
	testTestBoard();

def testTestBoard():
	boardId = 'VoCJJodK';
	## Uncomment to load data from board
	## (Very slow process)
	## Making Mongo database on that board using Trello API requests to get data:
	# collection = TrelloToMongoAdapter(boardId, apiKey, tokenKey);
	trello = TrelloUtility(apiKey, tokenKey);
	elems = trello.getBoardLists(boardId);

	# print("Check correct board:");
	# print(trello.checkBoard(boardId));
	# print("Check incorrect board:");
	# print(trello.checkBoard("VoCJJod"));

	db = getDB();
	collection = getCollection();
	# pprint(getLabels(db));
	pprint(getLabelNInList(collection, "test", "sky", "BCD"));
	pprint(getLabelN(collection, "test", "sky"));

	Date3 = datetime(2019,11,19);
	Date4 = datetime(2019,11,21);
	listName = "Work In Progress"
	member = "Jordan Womack"

	# print("Lists:");
	# pprint(getLists(db));
	# print("Labels:");
	labels = getLabels(db);
	pprint(getLabels(db));
	# print("Members:");
	# pprint(getMembers(db));
	members = db.members.find();
	pprint(list(db.members.find()));
	pprint(members);
	# pprint(dumps(members))

	print("Serialization test:");
	with open('out.json', 'w') as f:
		json.dump(labels, f);

	with open('out.json', 'r') as f:
		print("Read input:");
		pprint(json.load(f));

	# print("#### Paper1 stats ####");
	# print("List name is known from input");
	# print("Board name - too");
	# print("Cards N in list:")
	# pprint(getCardsNInListName(collection, listName));
	# print("Labels N of each type used:")
	# pprint(getLabelsN(collection));


	# print("#### Paper2 stats ####");
	# print("Created cards N:");
	# pprint(getCardsNCreatedInList(collection, listName, Date3, Date4));
	# print("Moved cards N:");
	# pprint(getCardsNMovedToList(collection, listName, Date3, Date4));
	# print("Moved or created cards N:");
	# pprint(getCardsNMovedOrCreatedInList(collection, listName, Date3, Date4));
	# print("AVG moved or created cards at last week:");
	# currday = datetime(2019, 11, 23)#datetime.utcnow()
	# lastweek = currday - timedelta(weeks=1)
	# lastmonth = currday - timedelta(days=31)
	# print(Date3 < Date4)
	# test = collection.aggregate([
	# 	{ '$project': { # Добавляем поле lastList,
	# 		'name': '$name',
	# 		'lastList': {
	# 			'$filter': { # Фильтруем массив, чтобы он содержал только нужные нам записи по дате
	# 				'input': '$moves',
	# 				'as': 'move',
	# 				'cond': { '$and': [
	# 					{ '$gte': [ '$$move.date', Date3] },
	# 					{ '$lt': [ '$$move.date', Date4] }
	# 					# { '$gte': ['$size': '$$']}
	# 				]}
	# 			}
	# 		},
	# 	}},
	# ])
	# pprint(list(test));
	# print(currday)
	# print(lastweek)
	# print(lastmonth)
	# pprint(getCardsNMovedOrCreatedInList(collection, listName, Date3, Date4)/7)
	# print("Max moved cards in all days")
	# pprint(getMaxCardsNMovedToList(collection, listName, Date3, Date4));
	# print("Cards added to list N, grouped by days");
	# pprint(getCardsNMovedOrCreatedInListGroupedByDay(collection, listName, Date3, Date4));
	# print("Cards added to list Number, grouped by day of week");
	# print("1 - Sunday, 7 - Saturday");
	# pprint(getCardsNMovedOrCreatedInListGroupedByDayOfWeek(collection, listName, Date3, Date4));
	#
	#
	# print("#### Paper3 stats ####");
	# print("-");
	#
	#
	# print("#### Paper4 stats ####");
	# print("Keywords stats:");
	# keyword = "test";
	# keyword = "Test";
	# keyword = "a";
	# pprint(getCardsNContainingKeyWord(collection, keyword))
	# print("Overdued cards number:")
	# print("?");
	# print("Number of days overdued:")
	# pprint(getOverduedDaysNInList(collection, listName));
	# print("Avg number of days overdued for each card:");
	# pprint(getOverduedDaysAvgNInList(collection, listName));
	# print("#### Paper5 stats ####");
	# print("Tasks that were done by user in period:")
	# pprint(getTasksFinishedByUserN(collection, member, listName, Date3, Date4))
	# print("Tasks that were done by user in period grouped by days:")
	# pprint(getTasksFinishedByUserNGroupedByDay(collection, member, listName, Date3, Date4))
	#
	#
	# print("#### Paper6 stats ####");
	# print("Attachments number made in period in particular list:");
	# pprint(getAttachmentsNInList(collection, listName, Date3, Date4))
	# print("Attachments avg number made in period in particular list:");
	# pprint(getAttachmentsAvgNInList(collection, listName, Date3, Date4))
	# print("Attachments made by user in particular list (not used)");
	# pprint(getAttachmentsNDoneInListByUser(collection, listName, member));
	#
	# print("#### Paper7 stats ####");
	# print("Number of comments in list");
	# # pprint(getCommentsNInList(collection, "DEF", Date1, Date2));
	# pprint(getCommentsNInList(collection, listName, Date3, Date4));
	# print("Average number of comments in list")
	# pprint(getCommentsAvgNInList(collection, listName, Date3, Date4));
	# print("Max number of comments in list");
	# pprint(getCommentsMaxNInList(collection, listName, Date3, Date4));
	# print("Get comments N in list by particular user:");
	# pprint(getCommentsNumberFromUserInList(collection, member, listName, Date3, Date4));


	# print("#### Paper8 stats ####");

if __name__ == '__main__':
	main()
