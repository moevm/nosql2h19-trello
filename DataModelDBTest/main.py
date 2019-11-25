# from pymongo import MongoClient;
from datetime import datetime, timezone, timedelta;
from pprint import pprint # Pretty printing
import json;

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

	db = getDB();
	collection = getCollection();

	Date3 = datetime(2019,10,25);
	Date4 = datetime(2019,10,31);
	member = "Denmey"

	print("Lists:");
	pprint(getLists(db));
	print("Labels:");
	pprint(getLabels(db));
	print("Members:");
	pprint(getMembers(db));

	print("#### Paper1 stats ####");
	print("List name is known from input");
	print("Board name - too");
	print("Cards N in list:")
	pprint(getCardsNInListName(collection, "DEF"));
	print("Labels N of each type used:")
	pprint(getLabelsN(collection));


	print("#### Paper2 stats ####");
	print("Created cards N:");
	pprint(getCardsNCreatedInList(collection, "DEF"));
	print("Moved cards N:");
	pprint(getCardsNMovedToList(collection, "DEF"));
	print("Moved or created cards N:");
	pprint(getCardsNMovedOrCreatedInList(collection, "DEF"));
	print("AVG moved or created cards at last week:");
	currday = datetime(2019, 11, 23)#datetime.utcnow()
	lastweek = currday - timedelta(weeks=1)
	lastmonth = currday - timedelta(days=31)
	# print(currday)
	# print(lastweek)
	# print(lastmonth)
	pprint(getCardsNMovedOrCreatedInList(collection, "DEF", lastweek, currday)/7)
	print("Max moved cards in all days")
	pprint(getMaxCardsNMovedToList(collection, "DEF"));
	print("Cards added to list N, grouped by days");
	pprint(getCardsNMovedOrCreatedInListGroupedByDay(collection, "DEF"));
	print("Cards added to list Number, grouped by day of week");
	print("1 - Sunday, 7 - Saturday");
	pprint(getCardsNMovedOrCreatedInListGroupedByDayOfWeek(collection, "DEF"));


	print("#### Paper3 stats ####");
	print("-");


	print("#### Paper4 stats ####");
	print("Keywords stats:");
	keyword = "test";
	# keyword = "Test";
	# keyword = "a";
	pprint(getCardsNContainingKeyWord(collection, keyword))
	print("Overdued cards number:")
	print("?");
	print("Number of days overdued:")
	pprint(getOverduedDaysNInList(collection, "DEF"));
	print("Avg number of days overdued for each card:");
	pprint(getOverduedDaysAvgNInList(collection, "DEF"));
	print("#### Paper5 stats ####");
	print("Tasks that were done by user in period:")
	pprint(getTasksFinishedByUserN(collection, member, "DEF"))
	print("Tasks that were done by user in period grouped by days:")
	pprint(getTasksFinishedByUserNGroupedByDay(collection, member, "DEF"))


	print("#### Paper6 stats ####");
	print("Attachments number made in period in particular list:");
	pprint(getAttachmentsNInList(collection, "DEF"))
	print("Attachments avg number made in period in particular list:");
	pprint(getAttachmentsAvgNInList(collection, "DEF"))
	print("Attachments made by user in particular list (not used)");
	pprint(getAttachmentsNDoneInListByUser(collection, "DEF", member));

	print("#### Paper7 stats ####");
	print("Number of comments in list");
	# pprint(getCommentsNInList(collection, "DEF", Date1, Date2));
	pprint(getCommentsNInList(collection, "DEF"));
	print("Average number of comments in list");
	pprint(getCommentsAvgNInList(collection, "DEF"));
	print("Max number of comments in list");
	pprint(getCommentsMaxNInList(collection, "DEF"));
	print("Get comments N in list by particular user:");
	pprint(getCommentsNumberFromUserInList(collection, member, "DEF"));


	# print("#### Paper8 stats ####");

if __name__ == '__main__':
	main()
