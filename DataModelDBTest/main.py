import pymongo;
import json;
# Keys from trello:
from APIKey import apiKey;
from tokenKey import tokenKey;

from TrelloUtility import TrelloUtility

def main():
	# Token key should be taken from user using UI.
	# Developer's token can be used for development (see https://trello.com/app-key).
	# API and Token keys must be kept in secret.
	trello = TrelloUtility(apiKey, tokenKey);

	# boards = trello.getBoards();
	# boardId = boards[2]['id'];
	# trello.getBoardInfo(boardId);

	# LOTR board from MMZ's example. Not really an id, but a short-link.
	boardId = 'tLvDmGT5';

	# lists = trello.getListsOnBoard(boardId);
	# cards = trello.getCardsOnList(lists[0]['id']);
	# print(json.dumps(trello.getCardInfo(cards[0]['id']), indent=3));
	actions = trello.getBoardActions(boardId);
	filterFunction = lambda x : ((x['type'] == 'updateCard') and ('listAfter' in x['data']));
	filteredList = list(filter(filterFunction, actions))
	# print(json.dumps(filteredList, indent=3));
	for it in filteredList:
		cardName = it['data']['card']['name'];
		fromList = it['data']['listBefore'];
		toList = it['data']['listAfter'];
		print('Moved card ', cardName, ' from ', fromList, ' to ', toList);

if __name__ == '__main__':
	main()
