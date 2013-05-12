guardian-api
============

Simple API for querying The Guardian API

Dependencies:
 * requests
 * Flask
 * PyMongo
 
Files:
 * guardian_server.py:
   * A Flask app with 4 primary actions:
     * fetch_news: Accesses the Guardian API with the given search term populates the MongoHQ DB with the top 5 articles
     * articles: Queries the MongoHQ DB for articles that match the given search term. Returns JSON.
     * article: Given an ObjectID, fetch the associated article. Returns JSON.
     * article_update: Given an ObjectID and title, update the associated article with the new title.
   * Utilizes a MongoHQ hosted MongoDB
   * Includes a helper connect_db() that connects to the MongoHQ database
 * api_tests.py:
  * Very simple unit tests for the Flask app
  * Primarily consists of two tests:
    * One main test that tests news fetching, article querying, article retrieval, and article updating.
      * Includes testing to make sure that actions correctly return JSON or a reasonable response if JSON is not expected.
    * Secondary test to make sure that we don't store the same article multiple times
