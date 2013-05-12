from flask import Flask
from flask import request
import requests
import json
from pymongo import MongoClient
from bson.objectid import ObjectId

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
  request_uri = "http://content.guardianapis.com/search?q=" + search_term + "&format=json&pageSize=5&show-fields=thumbnail"
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
      # Check to make sure that the thumbnail field is included because
      # not all articles have thumbnails
      if "fields" in article.keys() and "thumbnail" in article["fields"].keys():
        new_article["image_url"] = article["fields"]["thumbnail"]
      # Check to see if an article with this title already exists:
      if not articles_collection.find_one({"title":new_article['title']}):
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
  # Attempt to connect to our database
  articles_collection = connect_db()
  
  # Find the article and prepare it for display
  a = articles_collection.find_one({'_id': ObjectId(objectId)})
  article = {}
  article['id'] = str(a['_id'])
  article['image_url'] = a['image_url']
  article['title'] = a['title']
  return json.dumps(article)
    
# Article update
# Used via POST to update an article
@app.route("/article/", methods=['POST'])
def article_update():
  if "id" not in request.form.keys() or not request.form['id'] or "title" not in request.form.keys():
    return "Both ObjectId and new title required"
  
  # Attempt to connect to our database
  articles_collection = connect_db()
  
  # Attempt to update article
  articles_collection.update({'_id':ObjectId(request.form['id'])},{"$set":{"title":request.form['title']}})
  
  return "Updating article with id %s to have title %s" % (request.form['id'], request.form['title'])

# Database connection
def connect_db():
  client = MongoClient("mongodb://guardian:johnkerry@dharma.mongohq.com:10019/guardian-api")
  db = client["guardian-api"]
  return db["articles"]

if __name__ == "__main__":
  app.debug = True
  app.run()
