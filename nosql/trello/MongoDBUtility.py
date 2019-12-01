from datetime import datetime, MINYEAR, MAXYEAR
from pprint import pprint
minDate = datetime(MINYEAR, 1, 1);
maxDate = datetime(MAXYEAR, 12, 31);

def getCardsCreatedInListStage(list_, Date1 = minDate, Date2 = maxDate):
	return [
	{ "$match": {
		"moves": { "$size": 0 },
		"currentList": list_,
		"created": {'$gte': Date1, '$lt': Date2}
	}},
	]

def getCardsMovedToListStage(toList, Date1 = minDate, Date2 = maxDate):
	return [
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
					#{ '$eq': ['$$move.toList', toList]} # Works other way than next aggregation stage
				]}
			}
		},
		'max': '$max'
	}},
	{ '$match': { # Убираем документы, конечный список которых не соответствует нужному
		'lastList.toList': toList,
	}},
]


def getMembers(db):
	coll = db.members;
	return list(coll.find());

def getLabels(db):
	coll = db.labels;
	return list(coll.find());

def getLists(db):
	coll = db.lists;
	return list(coll.find());

### Paper1
def getCardsNInListName(collection, list):
	cardsN = collection.aggregate([
		{ '$match': {
			'currentList': list
		}},
		{ "$count": "count" }
	])
	if (cardsN.alive == False):
		number = 0;
	else:
		number = cardsN.next()['count'];
	return number;

def getLabelsN(collection):
	labelsN = collection.aggregate([
		{ "$project": {
			"labels": "$labels"
		}},
		{ '$unwind': "$labels" },
		{ "$project": {
			"labelType": { "$concat":
				["$labels.color", ",", "$labels.name"]
			},
		} },
		{ '$group': {
			'_id': '$labelType',
			'count': {'$sum': 1}
		}}
	])
	return list(labelsN);

# Get number of labels with exact name and color in particular list
def getLabelNInList(collection, name, color, listName):
	labelN = collection.aggregate([
		{ "$match": {
			"currentList": listName,
		}},
		{ "$project": {
			'labels': {
				'$filter': {
					'input': '$labels',
					'cond': { '$and': [
						{ '$eq': [ '$$this.name', name] },
						{ '$eq': [ '$$this.color', color] }
					]}
				}
			},
		}},
		{ '$unwind': "$labels" },
		{
			'$count': 'count'
		},
	])

	if (labelN.alive == False):
		result = 0;
	else:
		result = labelN.next()['count'];
	return result;

def getLabelN(collection, name, color):
	labelN = collection.aggregate([
		{ "$project": {
			'labels': {
				'$filter': {
					'input': '$labels',
					'cond': { '$and': [
						{ '$eq': [ '$$this.name', name] },
						{ '$eq': [ '$$this.color', color] }
					]}
				}
			},
		}},
		{ '$unwind': "$labels" },
		{
			'$count': 'count'
		},
	])

	if (labelN.alive == False):
		result = 0;
	else:
		result = labelN.next()['count'];
	return result;

### Paper2
def getCardsNCreatedInList(collection, list_,
		Date1 = minDate, Date2 = maxDate):
	stages = [];
	stages.extend(getCardsCreatedInListStage(list_, Date1, Date2));
	# stages.append({"$count": "count"});

	cards = collection.aggregate(stages);
	pprint(list(cards));
	if (cards.alive == False):
		number = 0;
	else:
		number = cards.next()['count'];

	return number;

# Returns cards that were put in list "toList" between "Date1" and "Date2" and were left in that list until Date2
def getCardsNMovedToList(collection, toList,
		Date1 = minDate, Date2 = maxDate):
	stages = [];
	stages.extend(getCardsMovedToListStage(toList, Date1, Date2));
	stages.append({"$count": "count"})

	cards = collection.aggregate(stages)

	# print(list(cards))
	# number;
	if (cards.alive == False):
		number = 0;
	else:
		number = cards.next()['count'];

	return number;

def getCardsNMovedOrCreatedInList(collection, toList,
		Date1 = minDate, Date2 = maxDate):
	cards = collection.aggregate([
		{ '$project': { # Добавляем поле lastList,
			'name': '$name',
			'created': '$created',
			'currentList': '$currentList',
			'moves': '$moves',
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
			'created': '$created',
			'currentList': '$currentList',
			'moves': '$moves',
			'lastList': '$lastList',
			'max': { '$max': '$lastList.date' } # Содержащее дату последнего действия в заданном интервалеы
		}},
		{ '$project': {
			'name': '$name',
			'created': '$created',
			'currentList': '$currentList',
			'moves': '$moves',
			'lastList': {
				'$filter': { # Фильтруем массив, чтобы он содержал только последнюю запись в заданном интервале
					'input': '$lastList',
					'as': 'move',
					'cond': {
						'$eq': ['$$move.date', '$max']
					},
				}
			},
			'max': '$max'
		}},
		{ '$match': { # Убираем документы, конечный список которых не соответствует нужному
			"$or": [
				{'lastList.toList': toList}, # Карточка перемещалась
				{ "$and": [ # Была создана в целевом списке и не перемещалась
					{'currentList': toList },
					{'moves': {"$size": 0}},
					{ "created": {'$gte': Date1, '$lt': Date2}}
				]}
			]
		}},
		{ '$count': 'count'	} # Считаем количество документов и заносим в поле count
		# Возвращаем документ с единственным полем count
	])
	# print(list(cards))
	# number;
	if (cards.alive == False):
		number = 0;
	else:
		number = cards.next()['count'];
	return number;

# Returns max number of cards that were created/moved in list by day
def getMaxCardsNMovedToList(collection, toList,
		Date1 = minDate, Date2 = maxDate):

	result = getCardsNMovedOrCreatedInListGroupedByDay(collection, toList, Date1, Date2);

	max = 0;
	for i in result:
		if (result[i] > max):
			max = result[i];

	return max;

def getCardsNCreatedInListGroupedByDay(collection, list_,
		Date1 = minDate, Date2 = maxDate):
	createdStages = [];
	createdStages.extend(getCardsCreatedInListStage(list_, Date1, Date2))
	createdStages.extend([
		{ "$project": {
			"created": {"$concat" : [
				{"$substr" : [{"$dayOfMonth" : "$created"}, 0, 2]}, "-",
				{"$substr" : [{"$month" : "$created"}, 0, 2]}, "-",
				{"$substr" : [{"$year" : "$created"}, 0, 4]}
			] }
		}},
		{ "$group": {
			"_id": "$created",
			"count": { "$sum": 1 }
		}}
	])
	created = collection.aggregate(createdStages);
	return list(created);

def getCardsNMovedToListGroupedByDay(collection, toList,
		Date1 = minDate, Date2 = maxDate):
	movedStages = [];
	movedStages.extend(getCardsMovedToListStage(toList, Date1, Date2))
	movedStages.extend([
		{ "$project": {
			"max": {"$concat" : [
				{"$substr" : [{"$dayOfMonth" : "$max"}, 0, 2]}, "-",
				{"$substr" : [{"$month" : "$max"}, 0, 2]}, "-",
				{"$substr" : [{"$year" : "$max"}, 0, 4]}
			] }
		}},
		{ "$group": {
			"_id": "$max",
			"count": { "$sum": 1 }
		}}
	])
	moved = collection.aggregate(movedStages);

	return list(moved);

def getCardsNMovedOrCreatedInListGroupedByDay(collection, toList,
		Date1 = minDate, Date2 = maxDate):
	# Get cards N moved to list grouped by date
	moved = getCardsNMovedToListGroupedByDay(collection, toList, Date1, Date2);
	# Get cards N created in list grouped by date
	created = getCardsNCreatedInListGroupedByDay(collection, toList, Date1, Date2);

	# Merge two lists in one and find max
	result = {};
	for i in range(len(moved)):
		result[moved[i]['_id']] = moved[i]['count'];
	for i in range(len(created)):
		if (created[i]['_id'] in result):
			result[created[i]['_id']] +=  created[i]['count'];
		else:
			result[created[i]['_id']] =  created[i]['count'];

	# pprint(moved);
	# pprint(created);
	# pprint(result);

	return result;

def getCardsNCreatedInListGroupedByDayOfWeek(collection, list_,
		Date1 = minDate, Date2 = maxDate):
	createdStages = [];
	createdStages.extend(getCardsCreatedInListStage(list_, Date1, Date2))
	createdStages.extend([
		{ "$project": {
			"created": {"$dayOfWeek" : "$created" }
		}},
		{ "$group": {
			"_id": "$created",
			"count": { "$sum": 1 }
		}}
	])
	created = collection.aggregate(createdStages);
	return list(created);

def getCardsNMovedToListGroupedByDayOfWeek(collection, toList,
		Date1 = minDate, Date2 = maxDate):
	movedStages = [];
	movedStages.extend(getCardsMovedToListStage(toList, Date1, Date2))
	movedStages.extend([
		{ "$project": {
			"max": {"$dayOfWeek" : "$max" }
		}},
		{ "$group": {
			"_id": "$max",
			"count": { "$sum": 1 }
		}}
	])
	moved = collection.aggregate(movedStages);

	return list(moved);

def getCardsNMovedOrCreatedInListGroupedByDayOfWeek(collection, toList,
		Date1 = minDate, Date2 = maxDate):
	# Get cards N moved to list grouped by date
	moved = getCardsNMovedToListGroupedByDayOfWeek(collection, toList, Date1, Date2);
	# Get cards N created in list grouped by date
	created = getCardsNCreatedInListGroupedByDayOfWeek(collection, toList, Date1, Date2);

	# Merge two lists in one and find max
	result = {};
	for i in range(len(moved)):
		result[moved[i]['_id']] = moved[i]['count'];
	for i in range(len(created)):
		if (created[i]['_id'] in result):
			result[created[i]['_id']] +=  created[i]['count'];
		else:
			result[created[i]['_id']] =  created[i]['count'];

	# pprint(moved);
	# pprint(created);
	# pprint(result);

	return result;


### Paper4
# Searches in description and title of all cards, comments aren't kept in DB
# Case insensitive
def getCardsNContainingKeyWord(collection, keyword):
	result = collection.aggregate([
		{"$match": { "$or": [
			{"description": {"$regex": keyword, "$options": "i"}},
			{"name": {"$regex": keyword, "$options": "i"}}
		]}},
		{ "$count": "count"}
	])
	if (result.alive == False):
		ret = 0;
	else:
		ret = result.next()['count']
	return ret;

# def getOverDueCards

def getOverduedDaysNInList(collection, list_):
	currtime = datetime.utcnow();
	result = collection.aggregate([
		{"$match": { "$and": [
			{ "dueTo": {"$ne": None} },
			{ "dueTo": {"$lte": currtime}},
			{ "currentList": list_ },
		]}},
		{ "$project": {
			"overdued": { "$floor": {"$divide": [{"$subtract": [currtime, "$dueTo"]}, 1000*60*60*24] } }
		}},
		{ "$group": {
			"_id": None,
			"result": {"$sum": "$overdued"}
		}}
	])
	if (result.alive == False):
		result = 0;
	else:
		result = result.next()['result']
	return result;

def getOverduedDaysAvgNInList(collection, list_):
	days = getOverduedDaysNInList(collection, list_);
	cards = getCardsNInListName(collection, list_);
	if (cards == 0):
		return 0;
	else:
		return days/cards;


### Paper5
def getTasksFinishedByUserN(collection, fullName, finishList, Date1 = minDate, Date2 = maxDate):
	result = collection.aggregate([
		{ '$project': { # Добавляем поле lastList,
			'name': '$name',
			'currentList': '$currentList',
			'moves': '$moves',
			'lastList': {
				'$filter': { # Фильтруем массив, чтобы он содержал только нужные нам записи по дате
					'input': '$moves',
					'as': 'move',
					'cond': { '$and': [
						{ '$gte': [ '$$move.date', Date1] },
						{ '$lt': [ '$$move.date', Date2] },
						{ '$eq': [ '$$move.member.fullName', fullName]}
					]}
				}
			},
		}},
		{ '$project': { # Добавляем поле max,
			'name': '$name',
			'currentList': '$currentList',
			'moves': '$moves',
			'lastList': '$lastList',
			'max': { '$max': '$lastList.date' } # Содержащее дату последнего действия в заданном интервалеы
		}},
		{ '$project': {
			'name': '$name',
			'currentList': '$currentList',
			'moves': '$moves',
			'lastList': {
				'$filter': { # Фильтруем массив, чтобы он содержал только последнюю запись в заданном интервале
					'input': '$lastList',
					'as': 'move',
					'cond': {
						'$eq': ['$$move.date', '$max']
					},
				}
			},
			"max": {"$concat" : [
				{"$substr" : [{"$dayOfMonth" : "$max"}, 0, 2]}, "-",
				{"$substr" : [{"$month" : "$max"}, 0, 2]}, "-",
				{"$substr" : [{"$year" : "$max"}, 0, 4]}
			] }
		}},
		{ '$match': { # Убираем документы, конечный список которых не соответствует нужному
			'lastList.toList': finishList
		}},
		# { '$group': {
		# 	'_id': '$max',
		# 	'count': {'$sum': 1}
		# }}
		{ '$count': 'count'	} # Считаем количество документов и заносим в поле count
		# # Возвращаем документ с единственным полем count
	]);
	if (result.alive == False):
		result = 0;
	else:
		result = result.next()['count'];
	return result;

def getTasksFinishedByUserNGroupedByDay(collection, fullName, finishList, Date1 = minDate, Date2 = maxDate):
	result = collection.aggregate([
		{ '$project': { # Добавляем поле lastList,
			'name': '$name',
			'currentList': '$currentList',
			'moves': '$moves',
			'lastList': {
				'$filter': { # Фильтруем массив, чтобы он содержал только нужные нам записи по дате
					'input': '$moves',
					'as': 'move',
					'cond': { '$and': [
						{ '$gte': [ '$$move.date', Date1] },
						{ '$lt': [ '$$move.date', Date2] },
						{ '$eq': [ '$$move.member.fullName', fullName]}
					]}
				}
			},
		}},
		{ '$project': { # Добавляем поле max,
			'name': '$name',
			'currentList': '$currentList',
			'moves': '$moves',
			'lastList': '$lastList',
			'max': { '$max': '$lastList.date' } # Содержащее дату последнего действия в заданном интервалеы
		}},
		{ '$project': {
			'name': '$name',
			'currentList': '$currentList',
			'moves': '$moves',
			'lastList': {
				'$filter': { # Фильтруем массив, чтобы он содержал только последнюю запись в заданном интервале
					'input': '$lastList',
					'as': 'move',
					'cond': {
						'$eq': ['$$move.date', '$max']
					},
				}
			},
			"max": {"$concat" : [
				{"$substr" : [{"$dayOfMonth" : "$max"}, 0, 2]}, "-",
				{"$substr" : [{"$month" : "$max"}, 0, 2]}, "-",
				{"$substr" : [{"$year" : "$max"}, 0, 4]}
			] }
		}},
		{ '$match': { # Убираем документы, конечный список которых не соответствует нужному
			'lastList.toList': finishList
		}},
		{ '$group': {
			'_id': '$max',
			'count': {'$sum': 1}
		}}
		# { '$count': 'count'	} # Считаем количество документов и заносим в поле count
		# # Возвращаем документ с единственным полем count
	]);

	return list(result);


### Paper6
def getAttachmentsNInList(collection, listName, Date1 = minDate, Date2 = maxDate):
	result = collection.aggregate([
		{ "$match": {
			"currentList": listName,
		}},
		{ "$project": {
			"attachments": { '$filter': { # Фильтруем массив, чтобы он содержал только нужные нам записи по дате
				'input': '$attachments',
				'cond': { '$and': [
					{ '$gte': [ '$$this.date', Date1] },
					{ '$lt': [ '$$this.date', Date2] },
				]}
			}}
		}},
		{ "$unwind": "$attachments"},
		{ "$count": "count"}
	]);

	if (result.alive == False):
		result = 0;
	else:
		result = result.next()['count'];
	return result;

def getAttachmentsAvgNInList(collection, listName, Date1 = minDate, Date2 = maxDate):
	attN = getAttachmentsNInList(collection, listName);
	cardsN = getCardsNInListName(collection, listName);
	if (cardsN == 0):
		return 0;
	else:
		return attN/cardsN;


### Paper7

def getAttachmentsNDoneInListByUser(collection, listName, fullName, Date1 = minDate, Date2 = maxDate):
	result = collection.aggregate([
		{ "$match": {
			"currentList": listName,
		}},
		{ "$project": {
			"attachments": { '$filter': { # Фильтруем массив, чтобы он содержал только нужные нам записи по дате
				'input': '$attachments',
				'cond': { '$and': [
					{ '$gte': [ '$$this.date', Date1] },
					{ '$lt': [ '$$this.date', Date2] },
					{ '$eq': [ '$$this.member.fullName', fullName]}
				]}
			}}
		}},
		{ "$unwind": "$attachments"},
		{ "$match": {
			"attachments.member.fullName": fullName
		}},
		{ "$count": "count"}
	]);

	if (result.alive == False):
		result = 0;
	else:
		result = result.next()['count'];
	return result;

def getCommentsNInList(collection, listName, Date1 = minDate, Date2 = maxDate):
	result = collection.aggregate([
		{ "$match": {
			"currentList": listName,
		}},
		{ "$project": {
			"comments": { '$filter': { # Фильтруем массив, чтобы он содержал только нужные нам записи по дате
				'input': '$comments',
				'cond': { '$and': [
					{ '$gte': [ '$$this.date', Date1] },
					{ '$lt': [ '$$this.date', Date2] },
				]}
			}}
		}},
		{ "$unwind": "$comments"},
		{ "$count": "count"}
	]);

	if (result.alive == False):
		result = 0;
	else:
		result = result.next()['count'];
	return result;

def getCommentsAvgNInList(collection, listName, Date1 = minDate, Date2 = maxDate):
	commN = getCommentsNInList(collection, listName);
	cardsN = getCardsNInListName(collection, listName);

	if (cardsN == 0):
		return 0;
	else:
		return commN/cardsN;

def getCommentsMaxNInList(collection, listName, Date1 = minDate, Date2 = maxDate):
	result = collection.aggregate([
		{ "$match": {
			"currentList": listName,
		}},
		{ "$project": {
			"comments": { '$filter': { # Фильтруем массив, чтобы он содержал только нужные нам записи по дате
				'input': '$comments',
				'cond': { '$and': [
					{ '$gte': [ '$$this.date', Date1] },
					{ '$lt': [ '$$this.date', Date2] },
				]}
			}}
		}},
		{ "$project": {
			"comments": { "$size": "$comments" }
		}},
		{ "$group": {
			"_id": None,
			"comments": { "$push": "$comments"}
		}},
		{ "$project": {
			"max": { "$max": "$comments" }
		}}
	]);
	# pprint(list(result));

	if (result.alive == False):
		result = 0;
	else:
		result = result.next()['max'];
	return result;

# Comments number from member with name "fullName"
def getCommentsNumberFromUserInList(collection, fullName, listName, Date1 = minDate, Date2 = maxDate):
	commentsNumber = collection.aggregate([
		{ "$match": {
			"currentList": listName
		}},
		{ '$project': {
			"count": { "$size": { # We put in field 'count' size of
				'$filter': { # Filtered 'comments' array
					'input': '$comments',
					# Elements of which matches this conditions:
					'cond': {'$and': [
						{'$eq': ['$$this.member.fullName', fullName]},
						{'$gte': ['$$this.date', Date1]},
						{'$lt': ['$$this.date', Date2]},
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
	if (commentsNumber.alive == False):
		commentsNumber = 0;
	else:
		commentsNumber = commentsNumber.next()['number'];
	return commentsNumber;




def getCommentsNumberFromUserGroupedByDate(collection, fullName, Date1, Date2):
	commentsNumber = collection.aggregate([
		{ '$project': {
			"comments": { # We put in field 'comments'
				'$filter': { # Filtered 'comments' array
					'input': '$comments',
					# Elements of which matches this conditions:
					'cond': {'$and': [
						{'$eq': ['$$this.member.fullName', fullName]},
						{'$gte': ['$$this.date', Date1]},
						{'$lt': ['$$this.date', Date2]},
					]}
				}
			}
		}},
		{ "$unwind": "$comments" },
		{ "$project" : {
			"datePartDay" : {"$concat" : [
			{"$substr" : [{"$dayOfMonth" : "$comments.date"}, 0, 2]}, "-",
			{"$substr" : [{"$month" : "$comments.date"}, 0, 2]}, "-",
			{"$substr" : [{"$year" : "$comments.date"}, 0, 4]}
		] }
		}},
		{ '$group': {
			"_id": "$datePartDay",
			"count": { "$sum": 1 }
		}},
	])
	return commentsNumber;

### Auxiliary
