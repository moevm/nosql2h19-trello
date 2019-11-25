from django.db import models

# from pymongo import MongoClient;
from datetime import datetime, timezone, timedelta, date
from pprint import pprint # Pretty printing
import json

# Keys from trello, should be kept in private:
from .APIKey import apiKey
from .tokenKey import tokenKey
from .TrelloUtility import TrelloUtility

from .TrelloToMongoAdapter import TrelloToMongoAdapter, getCollection, getDB
from .MongoDBUtility import *

import matplotlib.pyplot as plt
import numpy as np
import re
from fpdf import FPDF


class Link():
    def __init__(self, link):
        self.link = link


class Settings:
    def __init__(self, start_list, final_list, key_words, labels, executors, due_date, from_date, to_date, attachment, comments):
        self.start_list = start_list
        self.final_list = final_list
        self.key_words = key_words
        self.labels = labels
        self.executors = executors
        self.due_date = due_date
        self.from_date = from_date
        self.to_date = to_date
        self.attachment = attachment
        self.comments = comments


    def generate_statistic(self):
        collection = getCollection()

        pdf = FPDF(orientation='P', unit='mm', format='A4')
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt="Welcome to Python!", ln=1, align="C")
        pdf.add_page()
        pdf.image('Statistic1.png', x=10, y=8, w=100)
        # pdf.set_font("Arial", size=12)
        # pdf.ln(85)  # ниже на 85
        # pdf.cell(200, 10, txt="{}".format('Statistic1.png'), ln=1)
        pdf.output("Statistic.pdf")


        Date3 = datetime(2019, 10, 25)
        Date4 = datetime(2019, 10, 31)
        member = "Denmey"

        print("#### Paper1 stats ####")
        list_name = "DEF"
        board_name = "Test"
        print("Название списка: ", list_name)
        print("Название доски, на которой расположен список: ", board_name)
        print("Текущее количество карточек в списке", getCardsNInListName(collection, list_name))

        print("Статистика по меткам:")
        labels_in_doard = getLabelsN(collection)
        pprint(labels_in_doard)
        names = []
        values = []
        for d in labels_in_doard:
            names.append(d['_id'])
            values.append(d['count'])
        print(names, values)

        # поработать над цветом и подписями, подписи к осям
        fig, axs = plt.subplots()
        axs.bar(names, values)
        plt.savefig('Statistic1.png')

        # не хватает статистики кол-ва карточек на даты

        print("#### Paper2 stats ####")
        # спросить у Дениса как это расшифровать
        print("Created cards N:")
        pprint(getCardsNCreatedInList(collection, list_name))
        print("Moved cards N:")
        pprint(getCardsNMovedToList(collection, list_name))
        print("Moved or created cards N:")
        pprint(getCardsNMovedOrCreatedInList(collection, list_name))
        print("AVG moved or created cards at last week:")
        currday = datetime(2019, 11, 23)  # datetime.utcnow()
        lastweek = currday - timedelta(weeks=1)
        lastmonth = currday - timedelta(days=31)
        pprint(getCardsNMovedOrCreatedInList(collection, list_name, lastweek, currday) / 7)
        print("Max moved cards in all days")
        pprint(getMaxCardsNMovedToList(collection, list_name))

        # статистика перемещений карточек в список по датам
        print("Количество карточек, добавленных в список, с группировкой по дате: ")
        Date_from = date(2019, 10, 25)
        Date_to = date(2019, 11, 30)
        date_ncards = getCardsNMovedOrCreatedInListGroupedByDay(collection, list_name)  # сюда передаются даты
        pprint(date_ncards)
        curr_date = Date_from
        names = []
        values = []
        while (curr_date != Date_to):
            curr_date_to_string = curr_date.strftime("%d-%m-%Y")
            names.append(curr_date_to_string)
            if curr_date_to_string in date_ncards.keys():
                values.append(date_ncards[curr_date_to_string])
            else:
                values.append(0)
            curr_date += timedelta(1)

        # поработать над надписями, которые слипаются внизу, подписи к осям
        fig, axs = plt.subplots()
        axs.plot(names, values)
        plt.savefig('Statistic2.png')

        # статистика перемещений карточек в список по дням недели
        print("Количество карточек, добавленных в список, с группировкой по дате: ")
        print("1 - Sunday, 7 - Saturday")
        day_ncards = getCardsNMovedOrCreatedInListGroupedByDayOfWeek(collection, list_name)  # можно указывать даты
        pprint(day_ncards)

        days_of_week = {
            1: "Воскресенье",
            2: "Понедельник",
            3: "Вторник",
            4: "Среда",
            5: "Четверг",
            6: "Пятница",
            7: "Суббота"
        }

        names = []
        values = []
        for i in (2, 3, 4, 5, 6, 7, 1):
            names.append(days_of_week[i])
            if i in day_ncards.keys():
                values.append(day_ncards[i])
            else:
                values.append(0)

        # цвет и подписи осей
        fig, axs = plt.subplots()
        axs.bar(names, values)
        plt.savefig('Statistic3.png')

        print("#### Paper3 stats ####")
        print("-")

        print("#### Paper4 stats ####")
        print("Статистика по ключевым словам:")
        keywords = ["Test4", "test"]

        # ключевые слова ищутся по всей доске или в текущем списке?
        names = []
        values = []
        for keyword in keywords:
            names.append(keyword)
            values.append(getCardsNContainingKeyWord(collection, keyword))

        # цвет и подписи к осям
        fig, axs = plt.subplots()
        axs.bar(names, values)
        plt.savefig('Statistic4.png')

        print("Стеатистика по срокам выполнения")
        print("Overdued cards number:")
        print("?")
        print("Суммарное количество просроченных дней по всем карточкам списка: ")
        pprint(getOverduedDaysNInList(collection, list_name))
        print("Среднее количество дней превышения срока по всем карточкам списка: ")
        pprint(getOverduedDaysAvgNInList(collection, list_name))

        # не хватает статистики карточек с превышением срока по датам

        print("#### Paper5 stats ####")
        print("Статистика по исполнителям")
        print("Исполнитель: ", member)
        print("Количество выполненных задач за период с по: ")
        pprint(getTasksFinishedByUserN(collection, member, list_name))

        # не хватает среднего за неделю и месяц

        # сделать по членам и в конце сравнительный график
        print("Tasks that were done by user in period grouped by days:")
        tasks_member_date = getTasksFinishedByUserNGroupedByDay(collection, member, list_name)
        pprint(tasks_member_date)
        tmp = {}
        for d in tasks_member_date:
            tmp[d['_id']] = d['count']
        curr_date = Date_from
        names = []
        values = []
        while (curr_date != Date_to):
            curr_date_to_string = curr_date.strftime("%d-%m-%Y")
            names.append(curr_date_to_string)
            if curr_date_to_string in tmp.keys():
                values.append(tmp[curr_date_to_string])
            else:
                values.append(0)
            curr_date += timedelta(1)

        # поработать над надписями, которые слипаются внизу, подписи к осям
        fig, axs = plt.subplots()
        axs.plot(names, values)
        plt.savefig('Statistic5.png')

        print("#### Paper6 stats ####")
        print("Суммарное количество вложений к карточкам в списке:")
        pprint(getAttachmentsNInList(collection, list_name))
        print("Среднее количество вложений у одной карточки в списке:")
        pprint(getAttachmentsAvgNInList(collection, list_name))

        print("#### Paper7 stats ####")

        print("Статистика по количеству добавленных вложений пользователями:")
        members = ["Denmey", "Sonya"]
        names = []
        values = []
        for member in members:
            names.append(member)
            values.append(getAttachmentsNDoneInListByUser(collection, list_name, member))

        # поработать над надписями и цветом
        fig, axs = plt.subplots()
        axs.bar(names, values)
        plt.savefig('Statistic6.png')

        print("Статистика по комментариям")
        print("Суммарное количество комментариев в карточках в списке:")
        # pprint(getCommentsNInList(collection, "DEF", Date1, Date2));
        pprint(getCommentsNInList(collection, list_name))
        print("Среднее количество комментариев на одну карточку в списке: ")
        pprint(getCommentsAvgNInList(collection, list_name))
        print("Максимальное количество комментариев к одной карточке в списке: ")
        pprint(getCommentsMaxNInList(collection, list_name))

        print("Статистика по количеству добавленных комментариев пользователями:")
        members = ["Denmey", "Sonya"]
        names = []
        values = []
        for member in members:
            names.append(member)
            values.append(getCommentsNumberFromUserInList(collection, member, list_name))

        # поработать над надписями и цветом
        fig, axs = plt.subplots()
        axs.bar(names, values)
        plt.savefig('Statistic7.png')
