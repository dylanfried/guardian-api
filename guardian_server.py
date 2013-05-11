from flask import Flask
app = Flask(__name__)

# Default route
@app.route("/")
def hello():
    return "Guardian API"

# Fetch news
@app.route("/fetch_news/")
def fetch_news():
    return "FETCHING NEWS"

# Articles
# Used to query the local MongoDB for articles
@app.route("/articles/")
def articles():
    return "Retrieving matching articles"
    
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

if __name__ == "__main__":
    app.run()
