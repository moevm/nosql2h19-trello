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
from matplotlib.ticker import MultipleLocator, FormatStrFormatter, AutoMinorLocator
import numpy as np
import re
from fpdf import FPDF
import os
import glob


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


    def write_in_pdf(self, pdf, txt='', font_size=9, line_width=9, tab=True):
        pdf.set_font('DejaVu', '', font_size)
        if tab:
            pdf.write(font_size, "      " + txt)
        else:
            pdf.write(font_size, txt)
        pdf.ln(line_width)
        return

    def add_image_in_pdf(self, pdf, image_path='statistic.png'):
        pdf.ln(1)
        pdf.cell(20)
        pdf.image(image_path, x=30, w=150)
        pdf.ln(1)
        return

    def generate_statistic(self, board_name):
        collection = getCollection()
        statistic_path = './trello/statistic/'
        days_of_week = {1: "Вс", 2: "Пн", 3: "Вт", 4: "Ср", 5: "Чт", 6: "Пт", 7: "Сб"}

        for file in glob.glob(statistic_path+'*.pdf'): # чистка pdf
            os.remove(file)


        pdf = FPDF(orientation='P', unit='mm', format='A4')
        pdf.add_font('DejaVu', '', 'DejaVuSansCondensed.ttf', uni=True)


        for list_name in self.start_list: # цикл по каждому выбранному списку
            pdf.add_page()
            pdf.set_font('DejaVu', '', 16)
            pdf.cell(200, 16, txt="Trello Статистика", ln=1, align="C")
            self.write_in_pdf(pdf=pdf, txt="Общая статистика списка", font_size=12, tab=False)
            self.write_in_pdf(pdf=pdf, txt="Название списка: {}".format(list_name))
            self.write_in_pdf(pdf=pdf, txt="Название доски, на которой расположен список: {}".format(board_name))
            self.write_in_pdf(pdf=pdf, txt="Текущее количество карточек в списке: {}".format(getCardsNInListName(collection, list_name)))

            self.write_in_pdf(pdf=pdf, txt="Статистика по меткам", font_size=12, tab=False)
            labels_on_board = getLabelsN(collection)
            names = []
            values = []
            for d in labels_on_board:
                names.append(d['_id'])
                values.append(d['count'])
            # поработать над цветом и подписями, подписи к осям
            fig, ax = plt.subplots()
            ax.bar(names, values)
            ax.set_title('Количество меток каждого вида в списке')
            ax.set_xlabel('цвет, название метки')
            ax.set_ylabel('количество меток, шт')
            plt.savefig(statistic_path+'Statistic1.png')
            self.add_image_in_pdf(pdf=pdf, image_path=statistic_path+'Statistic1.png')

            # не хватает статистики кол-ва карточек на даты

            self.write_in_pdf(pdf=pdf, txt="Статистика добавлений/перемещений карточек в список", font_size=12, tab=False)
            self.write_in_pdf(pdf=pdf, txt="Общее количество созданных карточек в списке за период с {from_date} по {to_date}: {N}".format(
                                  from_date=self.from_date.strftime("%d.%m.%y"), to_date=self.to_date.strftime("%d.%m.%y"),
                                  N=getCardsNCreatedInList(collection, list_name, self.from_date, self.to_date)))
            self.write_in_pdf(pdf=pdf,txt="Общее количество добавленных карточек в списке за период с {from_date} по {to_date}: {N}".format(
                                  from_date=self.from_date.strftime("%d.%m.%y"), to_date=self.to_date.strftime("%d.%m.%y"),
                                  N=getCardsNMovedToList(collection, list_name, self.from_date, self.to_date)))
            num_moved_create = getCardsNMovedOrCreatedInList(collection, list_name, self.from_date, self.to_date)
            self.write_in_pdf(pdf=pdf,txt="Общее количество созданных/добавленных карточек в списке за период с {from_date} по {to_date}: {N}".format(
                                  from_date=self.from_date.strftime("%d.%m.%y"), to_date=self.to_date.strftime("%d.%m.%y"),
                                  N=num_moved_create))
            self.write_in_pdf(pdf=pdf, txt="Среднее количество созданных/добавленных карточек за период с {from_date} по {to_date} в неделю: {N}".format(
                                  from_date=self.from_date.strftime("%d.%m.%y"), to_date=self.to_date.strftime("%d.%m.%y"),
                                  N=round(num_moved_create/((self.to_date-self.from_date).days)/7, 3)))
            self.write_in_pdf(pdf=pdf, txt="Среднее количество созданных/добавленных карточек за период с {from_date} по {to_date} в месяц: {N}".format(
                                  from_date=self.from_date.strftime("%d.%m.%y"), to_date=self.to_date.strftime("%d.%m.%y"),
                                  N=round(num_moved_create/((self.to_date-self.from_date).days)/30, 3)))
            self.write_in_pdf(pdf=pdf, txt="Максимальное количество созданных/добавленных карточек за день: {}".format(
                getMaxCardsNMovedToList(collection, list_name)))

            # статистика перемещений карточек в список по датам
            date_ncards = getCardsNMovedOrCreatedInListGroupedByDay(collection, list_name, self.from_date, self.to_date)
            curr_date = self.from_date
            names = []
            values = []
            while (curr_date < self.to_date):
                curr_date_to_string = curr_date.strftime("%d-%m-%y")
                names.append(curr_date_to_string)
                if curr_date_to_string in date_ncards.keys():
                    values.append(date_ncards[curr_date_to_string])
                else:
                    values.append(0)
                curr_date += timedelta(1)
            # поработать над надписями, которые слипаются внизу, подписи к осям
            fig, ax = plt.subplots()
            ax.plot(names, values)
            ax.xaxis.set_major_locator(MultipleLocator(round(len(names)/5)))
            ax.set_title('График зависимости появления новых карточек в списке от даты')
            ax.set_xlabel('Дата')
            ax.set_ylabel('Количество карточек, шт')
            plt.savefig(statistic_path+'Statistic2.png')
            self.add_image_in_pdf(pdf=pdf, image_path=statistic_path + 'Statistic2.png')

            # статистика перемещений карточек в список по дням недели
            day_ncards = getCardsNMovedOrCreatedInListGroupedByDayOfWeek(collection, list_name, self.from_date, self.to_date)
            names = []
            values = []
            for i in (2, 3, 4, 5, 6, 7, 1):
                names.append(days_of_week[i])
                if i in day_ncards.keys():
                    values.append(day_ncards[i])
                else:
                    values.append(0)
            # цвет и подписи осей
            fig, ax = plt.subplots()
            ax.bar(names, values)
            ax.set_title('График зависимости появления новых карточек в списке от дня недели')
            ax.set_xlabel('День недели')
            ax.set_ylabel('Количество карточек, шт')
            plt.savefig(statistic_path+'Statistic3.png')
            self.add_image_in_pdf(pdf=pdf, image_path=statistic_path + 'Statistic3.png')

            # ключевые слова ищутся по всей доске или в текущем списке?
            if(len(self.key_words) > 0):
                self.write_in_pdf(pdf=pdf, txt="Статистика по ключевым словам", font_size=12, tab=False)
                names = []
                values = []
                for keyword in self.key_words:
                    names.append(keyword)
                    values.append(getCardsNContainingKeyWord(collection, keyword))
                # цвет и подписи к осям
                fig, ax = plt.subplots()
                ax.bar(names, values)
                ax.set_title('Встречаемость ключевых слов в названии/описании карточек списка')
                ax.set_xlabel('Ключевое слово')
                ax.set_ylabel('Количество карточек, шт')
                plt.savefig(statistic_path+'Statistic4.png')
                self.add_image_in_pdf(pdf=pdf, image_path=statistic_path + 'Statistic4.png')

            self.write_in_pdf(pdf=pdf, txt="Cтатистика по срокам выполнения", font_size=12, tab=False)
            self.write_in_pdf(pdf=pdf, txt="Суммарное количество просроченных дней по всем карточкам списка: {}".format(
                getOverduedDaysNInList(collection, list_name)))
            self.write_in_pdf(pdf=pdf, txt="Среднее количество дней превышения срока по всем карточкам списка: {}".format(
                getOverduedDaysAvgNInList(collection, list_name)))

            # не хватает статистики карточек с превышением срока по датам

            self.write_in_pdf(pdf=pdf, txt="Статистика по исполнителям", font_size=12, tab=False)
            g_values = []
            g_names = []
            for member in self.executors:
                self.write_in_pdf(pdf=pdf, txt="Исполнитель: {}".format(member))
                self.write_in_pdf(pdf=pdf, txt="Количество выполненных задач за период с {from_date} по {to_date}: {N}".format(
                    from_date=self.from_date.strftime("%d.%m.%y"), to_date=self.to_date.strftime("%d.%m.%y"),
                    N=getTasksFinishedByUserN(collection, member, list_name, self.from_date, self.to_date)))

                # не хватает среднего за неделю и месяц

                tasks_member_date = getTasksFinishedByUserNGroupedByDay(collection, member, list_name)
                tmp = {}
                for d in tasks_member_date:
                    tmp[d['_id']] = d['count']
                curr_date = self.from_date
                names = []
                values = []
                while (curr_date != self.to_date):
                    curr_date_to_string = curr_date.strftime("%d-%m-%y")
                    names.append(curr_date_to_string)
                    if curr_date_to_string in tmp.keys():
                        values.append(tmp[curr_date_to_string])
                    else:
                        values.append(0)
                    curr_date += timedelta(1)
                g_names.append(names)
                g_values.append(values)
                # поработать над надписями, которые слипаются внизу, подписи к осям
                fig, ax = plt.subplots()
                ax.plot(names, values)
                ax.xaxis.set_major_locator(MultipleLocator(round(len(names) / 5)))
                ax.set_title('График зависимости количества выполненных исполнителем\n задач от даты')
                ax.set_xlabel('Дата')
                ax.set_ylabel('Количество выполненных задач, шт')
                plt.savefig(statistic_path+'Statistic5.png')
                self.add_image_in_pdf(pdf=pdf, image_path=statistic_path+'Statistic5.png')

            if len(self.executors) > 1:
                fig, ax = plt.subplots()
                ax.set_title('График сравнения продуктивности исполнителей')
                ax.set_xlabel('Дата')
                ax.set_ylabel('Количество выполненных задач, шт')
                for i in range(len(self.executors)):
                    ax.plot(g_names[i], g_values[i], label=self.executors[i])
                plt.savefig(statistic_path + 'Statistic5_1.png')
                self.add_image_in_pdf(pdf=pdf, image_path=statistic_path + 'Statistic5_1.png')

            if(self.attachment):
                self.write_in_pdf(pdf=pdf, txt="Статистика по вложениям", font_size=12, tab=False)
                self.write_in_pdf(pdf=pdf, txt="Суммарное количество вложений к карточкам в списке: {}".format(
                    getAttachmentsNInList(collection, list_name)))
                self.write_in_pdf(pdf=pdf, txt="Среднее количество вложений у одной карточки в списке: {}".format(
                    getAttachmentsAvgNInList(collection, list_name)))
                names = []
                values = []
                for member in self.executors:
                    names.append(member)
                    values.append(getAttachmentsNDoneInListByUser(collection, list_name, member))
                # поработать над надписями и цветом
                fig, ax = plt.subplots()
                ax.set_title('Количество добавленных вложений каждым пользователем')
                ax.set_xlabel('Пользователь')
                ax.set_ylabel('Количество добавленных вложений, шт')
                ax.bar(names, values)
                plt.savefig(statistic_path+'Statistic6.png')
                self.add_image_in_pdf(pdf=pdf, image_path=statistic_path+'Statistic6.png')

            if(self.comments):
                self.write_in_pdf(pdf=pdf, txt="Статистика по комментариям", font_size=12, tab=False)
                self.write_in_pdf(pdf=pdf, txt="Суммарное количество комментариев в карточках в списке: {}".format(
                    getCommentsNInList(collection, list_name)))
                self.write_in_pdf(pdf=pdf, txt="Среднее количество комментариев на одну карточку в списке: {}".format(
                    getCommentsAvgNInList(collection, list_name)))
                self.write_in_pdf(pdf=pdf, txt="Максимальное количество комментариев к одной карточке в списке: {}".format(
                    getCommentsMaxNInList(collection, list_name)))
                names = []
                values = []
                for member in self.executors:
                    names.append(member)
                    values.append(getCommentsNumberFromUserInList(collection, member, list_name))
                # поработать над надписями и цветом
                fig, ax = plt.subplots()
                ax.bar(names, values)
                ax.set_title('График зависимости количества комментариев исполнителей задач от даты')
                ax.set_xlabel('Дата')
                ax.set_ylabel('Количество комментариев, шт')
                plt.savefig(statistic_path+'Statistic7.png')
                self.add_image_in_pdf(pdf=pdf, image_path=statistic_path+'Statistic7.png')

                for file in glob.glob(statistic_path + '*.png'):  # чистка картиночек
                    os.remove(file)



        pdf.output(statistic_path+"Statistic.pdf", 'F') # сохранение PDF файла
