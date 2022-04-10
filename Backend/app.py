from flask import Flask, request, jsonify, g
import sqlite3
import random
from flask_cors import CORS
import datetime
import time
from scrape import fetch_links, fetch_articles

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

@app.route('/test', methods=['GET'])
def test_db():
    ct = datetime.datetime.now() 
    insert_search_history("Sci", ct, "1")
    insert_tags("Painting")
    query_string = "delete FROM tags;"
    cur = get_db().cursor() # SQLITE cursor
    cur.execute(query_string)
    get_db().commit()
    cur.close()
    return 'ok'

@app.route('/search', methods=['POST'])
def search():
    # truncate blogs first
    query_string = "delete FROM blogs;"
    cur = get_db().cursor() # SQLITE cursor
    cur.execute(query_string)
    get_db().commit()
    cur.close()
    
    # truncate tags second
    query_string = "delete FROM tags;"
    cur = get_db().cursor() # SQLITE cursor
    cur.execute(query_string)
    get_db().commit()
    cur.close()

    
    tag_to_search = request.json
    tag_to_search = tag_to_search['tag']
    # print(tag_to_search)
    
    suffixes = ['', 'latest', 'archive/2000', 'archive/2001', 'archive/2002', 'archive/2003', 'archive/2004', 'archive/2005', 'archive/2006', 'archive/2007', 'archive/2008', 'archive/2009',
        'archive/2010', 'archive/2011', 'archive/2012', 'archive/2013', 'archive/2014', 'archive/2015', 'archive/2016', 'archive/2017', 'archive/2018'
    ]
    
    links = fetch_links(tag_to_search, suffixes)
    # print('--links--')
    # print(links)
    articles = fetch_articles(tag_to_search, links)
    ct = datetime.datetime.now()
    
    if not articles:
        insert_search_history(tag_to_search, ct, 0)
        # insert_tags(tag_to_search)
        # search for related tags and inform the user about it!
        popular = [
            'startup', 'art', 'life', 'politics', 'travel', 'entrepreneurship', 'life lessons',
            'poetry', 'health', 'education', 'love', 'design', 'music', 'writing', 'technology',
            'business', 'self improvement', 'social media', 'Sports', 'Food'
        ]
        tag_to_search = random.choice(popular)
        print("No results found, will search for " + str(tag_to_search))
        links = fetch_links(tag_to_search, suffixes)
        articles = fetch_articles(tag_to_search, links)
    else:
        insert_search_history(tag_to_search, ct, 1)
        # insert_tags(tag_to_search)
    
    return jsonify({"search_tag":tag_to_search, "links":links, "articles": articles})

@app.route('/get-blogs', methods=['GET'])
def retrieve_blog():
    # cursor = mysql.connection.cursor()
    cursor = get_db().cursor() # SQLITE cursor
    query_string = "SELECT * FROM blogs"
    cursor.execute(query_string)
    data = cursor.fetchall()
    cursor.close()
    
    cursor = get_db().cursor() # SQLITE cursor
    query_string = "SELECT * FROM tags"
    cursor.execute(query_string)
    tags = cursor.fetchall()
    cursor.close()
    
    return jsonify({"data": data, "tags": tags})

@app.route('/get-search-results', methods=['GET'])
def get_search_history():
    # cursor = mysql.connection.cursor()
    cursor = get_db().cursor() # SQLITE cursor
    query_string = "SELECT * FROM search_history"
    cursor.execute(query_string)
    data = cursor.fetchall()
    cursor.close()
    return jsonify({"data":data})

@app.route('/get-related-tags', methods=['GET'])
def get_related_tags():
    # cursor = mysql.connection.cursor()
    cursor = get_db().cursor() # SQLITE cursor
    query_string = "SELECT * FROM tags"
    cursor.execute(query_string)
    data = cursor.fetchall()
    cursor.close()
    return jsonify({"tags":data})


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

def insert_search_history(search_tag, created_at, result_found):
    cur2 = get_db().cursor() # SQLITE cursor
    cur2.execute(
        'INSERT INTO search_history(search_tag, created_at, result_found) VALUES (?,?,?)',
        (
            search_tag, created_at, result_found,
        )
    )
    get_db().commit()
    cur2.close()
    
if __name__ == '__main__':
    app.run(debug=True, use_reloader=True)
