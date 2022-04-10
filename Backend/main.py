from flask import Flask,jsonify,request,make_response
from flask_sqlalchemy import SQLAlchemy,inspect
from datetime import datetime
import json
import itertools
import sqlite3

import urllib3
from bs4 import BeautifulSoup
import requests
import os
import csv
import unicodedata
import pandas as pd
import time

# from scrape import fetch_links, fetch_articles, save_to_csv

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///crawler.db'
db = SQLAlchemy(app)
db.create_all()


class blogs(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    author = db.Column(db.String(255), nullable=False)
    details = db.Column(db.String(255), nullable=True)
    tags = db.Column(db.String(255), nullable=False)
    blog = db.Column(db.TEXT, nullable=False)
    comments = db.Column(db.String(255), nullable=True)
    publish_time = db.Column(db.String(255), nullable=True)
    link = db.Column(db.String(255), nullable=False)
    time_taken = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return '<blog %r>' % self.id
    
class search_history(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    search_tag = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    result_found = db.Column(db.Boolean, unique=False, default=True)
    
    def __repr__(self):
        return '<search_history %r>' % self.id
    
class tags(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tag = db.Column(db.String(255), nullable=False)
    
    def __repr__(self):
        return '<tags %r>' % self.id
    
@app.route('/get-blogs', methods=['GET'])
def retrieve_blog():
    records = blogs.query.all()
    print(records)
    return make_response(jsonify(records), 200)

def insert_blog(title, author, details, blog, tags, comments, publish_time, link, time_taken):
    # truncate tables first
    
    new_blog = blogs(title=title, author=author, details=details, blog=blog, tags=tags, comments=comments, publish_time=publish_time, link=link, time_taken=time_taken)
    db.session.add(new_blog)
    db.session.commit()
    
@app.route('/search', methods=['POST'])
def search():
    tag_to_search = request.json
    tag_to_search = tag_to_search['tag']
    print('tag to search'+tag_to_search)
    
    suffixes = ['', 'latest', 'archive/2000', 'archive/2001', 'archive/2002', 'archive/2003', 'archive/2004', 'archive/2005', 'archive/2006', 'archive/2007', 'archive/2008', 'archive/2009',
        'archive/2010', 'archive/2011', 'archive/2012', 'archive/2013', 'archive/2014', 'archive/2015', 'archive/2016', 'archive/2017', 'archive/2018'
    ]
    
    links = fetch_links(tag_to_search, suffixes)
    articles = fetch_articles(tag_to_search, links)
    return jsonify({"search_tag":tag_to_search, "links":links, "articles": articles})

def fetch_links(tag, suffix):
    print('inside fetch_link')
    count = 0
    url = 'https://medium.com/tag/' + tag
    urls = [url + '/' + s for s in suffix]
    print('urls',urls)
    links = []
    for url in urls:
        if(count == 10):
            break
        else:
            count += 1
            data = requests.get(url)
            soup = BeautifulSoup(data.content, 'html.parser')
            articles = soup.findAll('div', {"class": "postArticle-readMore"})
            print('articles--',articles)
            for i in articles:
                links.append(i.a.get('href'))
    return links

def fetch_articles(tag, links):
    print('links',links)
    count = 0
    # print("--- Links ---")
    # print(links)
    articles = []
    for link in links:
        if(count == 10): # only fetch 10 articles
            break
        else:
            # print("Count: " + str(count))
            start_time = time.time()
            count += 1
            article = {}
            data = requests.get(link)
            print('data',data)
            soup = BeautifulSoup(data.content, 'html.parser')
            print('soup',soup)
            # title = soup.findAll('title')[0]
            title = soup.findAll('meta', {"property": "og:title"})[0]
            title = title.get('content')
            author = soup.findAll('meta', {"name": "author"})[0]
            author = author.get('content')
            read = soup.findAll('meta', {"name": "twitter:data1"})[0]
            read = read.get('value')
            publish_timestamp = soup.findAll('meta', {"property": "article:published_time"})[0]
            publish_timestamp = publish_timestamp.get('content')
            # claps  = soup.findAll('button', {"data-action":"show-recommends"})[0].get_text()
            # article['claps'] = unicodedata.normalize('NFKD', claps)
            article['author'] = unicodedata.normalize('NFKD', author)
            article['link'] = link
            article['title'] = unicodedata.normalize('NFKD', title)
            article['read'] = unicodedata.normalize('NFKD', read)
            article['publish_time'] = unicodedata.normalize('NFKD', publish_timestamp)
            # print("--- Title ---")
            # print(title)
            paras = soup.findAll('p')
            text = ''
            nxt_line = '\n'
            for para in paras:
                text += unicodedata.normalize('NFKD',para.get_text()) + nxt_line
            article['blog'] = text
            # print("--- Blog content ---")
            # print(article['blog'])
            end_time = time.time()
            time_taken = end_time - start_time
            article['time_taken'] = time_taken
            articles.append(article)
            insert_blog(title, author, read, text, tag, None, publish_timestamp, link, time_taken)
    # print(articles)
    return articles
    
if __name__ == "__main__":
    app.run(debug=True)