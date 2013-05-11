from flask import Flask
from flask import request
import requests
import json
from pymongo import MongoClient

app = Flask(__name__)

# Default route
@app.route("/")
def hello():
  return "Guardian API"

# Fetch news
@app.route("/fetch_news/")
def fetch_news():
  # First, get our search term
  search_term = request.args.get('term')
  if not search_term:
    # Search term is necessary
    return "No search term provided"
  
  # Attempt to connect to our database
  articles_collection = connect_db()
  
  # Access the Guardian API to grab results
  request_uri = "http://content.guardianapis.com/search?q=" + search_term + "&format=json&pageSize=5"
  try:
    guardian_response = requests.get(request_uri)
  except requests.ConnectionError:
    return "Connection Error"
  guardian_data = json.loads(guardian_response.text)
  if guardian_data["response"]["status"] == "ok" and guardian_data["response"]["results"]:
    for article in guardian_data["response"]["results"]:
      new_article = {"title":article["webTitle"],
                     "image_url":"",
                     "terms":[search_term]}
      articles_collection.insert(new_article)
  return "FETCHING NEWS with search term: '%s'" % search_term

# Articles
# Used to query the local MongoDB for articles
@app.route("/articles/")
def articles():
  # First, get our search term
  search_term = request.args.get('term')
  if not search_term:
    # Search term is necessary
    return "No search term provided"
    
  # Attempt to connect to our database
  articles_collection = connect_db()
  
  articles = []
  for a in articles_collection.find({"terms": search_term}):
    article = {}
    article['id'] = str(a['_id'])
    article['image_url'] = a['image_url']
    article['title'] = a['title']
    articles.append(article)
  
  return json.dumps(articles)
    
# Article retrieval
# Used to retrieve an article with the given 
# ObjectId from the MongoDB
@app.route("/article/<objectId>")
def article_retrieval(objectId):
  return "Retrieving article with objectId: %s" % objectId
    
# Article update
# Used via POST to update an article
@app.route("/article/", methods=['POST'])
def article_update():
  return "Updating article"

# Database connection
def connect_db():
  client = MongoClient("mongodb://guardian:johnkerry@dharma.mongohq.com:10019/guardian-api")
  db = client["guardian-api"]
  return db["articles"]

if __name__ == "__main__":
  app.debug = True
  app.run()
