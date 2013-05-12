from flask import Flask
import guardian_server
import unittest
import pprint
import json

class GuardianServerTestCase(unittest.TestCase):

  def setUp(self):
    # Create test client
    self.app = guardian_server.app.test_client()
    # Drop all records from DB
    self.articles_collection = guardian_server.connect_db()
    self.articles_collection.remove()

  def tearDown(self):
    pass
  
  def test_welcome(self):
    rv = self.app.get('/')
    assert 'Guardian API' in rv.data
    assert self.articles_collection.count() == 0
    
  # Test to make sure that we don't store the same article multiple times
  def test_double_fetch(self):
    assert self.articles_collection.count() == 0
    rv = self.app.get('/fetch_news/?term=john+kerry')
    assert "FETCHING NEWS with search term: 'john kerry'" in rv.data
    assert self.articles_collection.count() == 5
    rv = self.app.get('/fetch_news/?term=john+kerry')
    assert self.articles_collection.count() == 5
    
  # Simple test for making sure that the article fetching, querying,
  # and updating works
  def test_articles(self):
    # First, let's test fetching news
    assert self.articles_collection.count() == 0
    rv = self.app.get('/fetch_news/?term=john+kerry')
    assert "FETCHING NEWS with search term: 'john kerry'" in rv.data
    assert self.articles_collection.count() == 5
    rv = self.app.get('/fetch_news/?term=obama')
    assert self.articles_collection.count() == 10
    
    # Now that we have some stuff, let's test
    # querying our DB
    rv = self.app.get('/articles/?term=john+kerry')
    json_data = json.loads(rv.data)
    # Check that the data format is correct
    assert len(json_data) == 5
    assert "title" in json_data[2].keys()
    assert "image_url" in json_data[2].keys()
    assert "id" in json_data[2].keys()
    
    # Now, let's try retrieving a single article
    rv = self.app.get('/article/'+json_data[2]['id'])
    json_article = json.loads(rv.data)
    # Check that the data format is correct
    assert "title" in json_article.keys()
    assert "image_url" in json_article.keys()
    assert "id" in json_article.keys()
    # Check to make sure that the data itself is correct
    assert json_article["title"] == json_data[2]["title"]
    assert json_article["image_url"] == json_data[2]["image_url"]
    assert json_article["id"] == json_data[2]["id"]
    
    # Now let's update the article title
    rv = self.app.post('/article/',data=dict(
      id=json_article["id"],
      title="New Title"
      ))
    assert "Updating article with id " + json_article["id"] + " to have title New Title"
    # Retrieve the article again and make sure that the title was
    # actually changed
    rv = self.app.get('/article/'+json_data[2]['id'])
    json_article = json.loads(rv.data)
    # Check that the data format is correct
    assert "title" in json_article.keys()
    assert "image_url" in json_article.keys()
    assert "id" in json_article.keys()
    # Check to make sure that the data itself is correct
    assert json_article["title"] == "New Title"
    assert json_article["image_url"] == json_data[2]["image_url"]
    assert json_article["id"] == json_data[2]["id"]

if __name__ == '__main__':
    unittest.main()
