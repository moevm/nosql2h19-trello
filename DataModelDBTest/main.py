from pymongo import MongoClient;
from pprint import pprint;
import json;
# Keys from trello:
from APIKey import apiKey;
from tokenKey import tokenKey;

from TrelloUtility import TrelloUtility
from TrelloToMongoAdapter import TrelloToMongoAdapter

def main():
	# LOTR board from MMZ's example. Not really an id, but a short-link.
	# boardId = 'tLvDmGT5'; # Board is copied from another one, so there's no 'create card' actions and adapter can't fill in creation date
	# My test board:
	# boardId = 'VoCJJodK';
	# https://trello.com/b/qhgryS9a/
	boardId = 'qhgryS9a'
	collection = TrelloToMongoAdapter(boardId, apiKey, tokenKey);


if __name__ == '__main__':
	main()
