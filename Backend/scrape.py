import urllib3
from bs4 import BeautifulSoup
import requests
import os
import csv
import unicodedata
import pandas as pd
import time
from flask import Flask, request, jsonify, g
import sqlite3
from random import randint
from time import sleep
import re
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# app.config['MYSQL_HOST'] = 'localhost'
# app.config['MYSQL_USER'] = 'root'
# app.config['MYSQL_PASSWORD'] = ''
# app.config['MYSQL_DB'] = 'crawler'

# mysql = MySQL(app)

DATABASE = 'crawler.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


def fetch_links(tag, suffix):
    count = 0
    url = 'https://medium.com/tag/' + tag
    urls = [url + '/' + s for s in suffix]
    links = []
    for url in urls:
        if(count == 10):
            break
        else:
            count += 1
            data = requests.get(url)
            soup = BeautifulSoup(data.content, 'html.parser')
            articles = soup.findAll('div', {"class": "postArticle-readMore"})
            for i in articles:
                links.append(i.a.get('href'))
                # print(links)
    return links

def fetch_articles(tag, links):
    count = 0
    # print("--- Links ---")
    # print(links)
    articles = []
    for link in links:
        if(count == 10): # only fetch 10 articles
            break
        else:
            start_time = time.time()
            count += 1
            article = {}
            data = requests.get(link)
            print(data)
            soup = BeautifulSoup(data.content, 'html.parser')
            sleep(randint(1,10)) # introducing delay to avoid blocking.
            
            # find related tags from page
            a = ''
            for ul in soup.find_all('div'):
                for ul in soup.find_all('ul'):
                    for li in ul.find_all('li'):
                        a = li.find('a')
            
            # insert related tags to db
            if a :
                # print('inside if')
                insert_tags(a.get_text())
                    
            title = soup.find('h1', class_="pw-post-title")
            title = title.get_text()
            author = soup.find('div', class_="pw-author")
            print(author)
            author = author.get_text()
            read = soup.find('div', class_="pw-reading-time")
            # print('read value')
            # print(read)
            read = read.get_text()

            publish_timestamp = soup.find('p', class_="pw-published-date")
            publish_timestamp = publish_timestamp.get_text()
            article['author'] = unicodedata.normalize('NFKD', author)
            article['link'] = link
            article['title'] = unicodedata.normalize('NFKD', title)
            # article['read'] = unicodedata.normalize('NFKD', read)
            article['publish_time'] = unicodedata.normalize('NFKD', publish_timestamp)
            paras = soup.findAll('p')
            text = ''
            nxt_line = '\n'
            for para in paras:
                text += unicodedata.normalize('NFKD',para.get_text()) + nxt_line
            article['blog'] = text
            end_time = time.time()
            time_taken = int(end_time - start_time)
            article['time_taken'] = time_taken
            articles.append(article)
            insert_blog(title, author, read, text, tag, None, publish_timestamp, link, time_taken)
    # print(articles)
    return articles

def insert_tags(tag):
    cursor1 = get_db().cursor() # SQLITE cursor
    cursor1.execute(
        'INSERT INTO tags(tag) VALUES (?)',
        (
            tag,
        )
    )
    get_db().commit()
    cursor1.close()
    return 'ok'

def insert_blog(title, author, details, blog, tags, comments, publish_time, link, time_taken):
    cur = get_db().cursor() # SQLITE cursor
    cur.execute(
        'INSERT INTO blogs(title, author, details, blog, tags, comments, publish_time, link, time_taken) VALUES (?,?,?,?,?,?,?,?,?)',
        (
            title, author, details, blog, tags, comments, publish_time, link, time_taken,
        )
    )
    get_db().commit()
    cur.close()
    return 'ok'

def save_to_csv(articles, csv_file,  should_write = True):
    csv_columns = ['author', 'link', 'title', 'read', 'publish_time', 'blog']
    # print(csv_file)
    if should_write:
        with open(csv_file, 'w', encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=csv_columns, delimiter=',')
            writer.writeheader()
            for data in articles:
                writer.writerow(data)
            csvfile.close()
            print("file write successful")
    else:
        with open(csv_file, 'a+', encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=csv_columns,  delimiter=',')
            for data in articles:
                writer.writerow(data)
            csvfile.close()
            print("file append successful")


def main():
    should_write = True
    tag = input('\n Input tag: ')
    file_name = input('\n Input filename: ')
    if len(file_name.split('.')) == 1:
        file_name += '.csv'
    suffixes = ['', 'latest', 'archive/2000', 'archive/2001', 'archive/2002', 'archive/2003', 'archive/2004', 'archive/2005', 'archive/2006', 'archive/2007', 'archive/2008', 'archive/2009',
            'archive/2010', 'archive/2011', 'archive/2012', 'archive/2013', 'archive/2014', 'archive/2015', 'archive/2016', 'archive/2017', 'archive/2018']
    links = fetch_links(tag, suffixes)
    articles = fetch_articles(tag, links)
    save_to_csv(articles, file_name, should_write)
    should_write = False
if __name__ == '__main__':
    main()