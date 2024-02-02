import json
import threading
from django.core.handlers.wsgi import WSGIHandler
from django.core.servers.basehttp import ThreadedWSGIServer, WSGIRequestHandler
from django.utils.functional import classproperty
from django.test.testcases import _MediaFilesHandler
from Users.models import user
from django.db import connection
import sys
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.core.management import call_command
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
from elasticsearch_dsl import connections, Index
from selenium import webdriver
from django.test import LiveServerTestCase
from selenium.common import TimeoutException
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from datetime import datetime
from django_selenium import settings
from search.search_indexes import TestArticleIndex
from selenium.webdriver.common.keys import Keys
from django.test import modify_settings



class FunctionalTest(LiveServerTestCase):
    fixtures = ["user_data.json"]
    port = 57262

    @classmethod
    def setUpClass(cls):
        print("Loading fixtures...")
        call_command('loaddata', *cls.fixtures)
        print("Fixtures loaded successfully.")
        connections.create_connection(alias='default', hosts=['http://localhost:9200'])
        # index derto date et heure besh officiel ykon unique , pcq kan ydirli beli hed l'index y'existi deja
        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        index_name = f'test_index_{timestamp}'

        test_index = Index(index_name)
        test_index.create()

        cls.index_documents('search/test_articles.json', index_name)
        # Connect to the test Elasticsearch index
        #connections.create_connection(alias='default', hosts=['localhost:9200'])
        # Create or index test data
        #es = Elasticsearch(['http://localhost:9200'],)
        #index = TestArticleIndex._index._name
        #es.indices.delete(index=index) # Décommenter cette instruction en cas de dupplications(permet de supprimer l'index existant)
        # Lecture des données par
        #with open('search/test_articles.json') as json_file:
            #articles_data = json.load(json_file)
        #Préparation des paramètres à indexer
        #actions = [
            #{
                #'_op_type': 'index',
                #'_index': index,
                #Définition d'un Id automatique
                #'_source': {
                    #'title': data.get('title', ''),
                    #'authors': data.get('authors', ''),
                    #'institutions': data.get('institutions', ''),
                    #'keywords': data.get('keywords', ''),
                    #'pdf_url': data.get('pdf_url', ''),
                    #'bibliographie': data.get('bibliographie', ''),
                    #'abstract': data.get('abstract', ''),
                    #'text': data.get('text', ''),
                    #'date': data.get('date', ''),
                    #'status': 'unreviewed'
                #}
            #}
            #for data in articles_data
        #]
        # Indexation à l'aide de la fonction Bulk
        #success, failed = bulk(es, actions)
        # Message de réussite de l'indexation
        #print(f'Successfully indexed {success} documents')
        #print(f'Failed to index {failed} documents')
        #test_index = Index('test_index')
        #test_index.create()
        super().setUpClass()
        cls.selenium = WebDriver()
        cls.selenium.implicitly_wait(10)

    @classmethod
    def index_documents(cls, json_file_path, index_name):
        es = Elasticsearch(['http://localhost:9200'])
        with open(json_file_path) as json_file:
            documents_data = json.load(json_file)
        actions = [
            {
                '_op_type': 'index',
                '_index': index_name,
                '_source': document,
            }
            for document in documents_data
        ]
        success, failed = bulk(es, actions)
        # Print the results
        print(f'Successfully indexed {success} documents')
        print(f'Failed to index {failed} documents')

    def test_search_functionality(self):
        self.selenium.get("http://localhost:5173/login")
        username_elem = self.selenium.find_element(By.XPATH, '//input[@placeholder="username"]')
        username_elem.send_keys("Marii")
        password_elem = self.selenium.find_element(By.XPATH, '//input[@placeholder="password"]')
        password_elem.send_keys("mariCLIENT")
        self.selenium.find_element(By.XPATH, '//button[contains(text(), "Log in")]').click()
        #self.selenium.implicitly_wait(10)
        #try:
            #query_input = self.selenium.find_element(By.XPATH, '//input[@placeholder="Search"]')
            #print("Successfully logged in, and the page is the home page.")
        #except:
            #print("Login might have failed or the page is not the home page.")
        search_input = WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located((By.ID, "searchBar"))
        )
        search_input.send_keys("article")
        self.selenium.implicitly_wait(10)
        search_button = self.selenium.find_element(By.ID, "search-button")
        search_button.click()

        WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located((By.ID, "search-results-indicator"))
        )

        # Check if results are present using JavaScript
        results_present = self.selenium.execute_script(
            'return document.getElementById("search-results-indicator") !== null;'
        )

        self.assertTrue(results_present, "Search results are not present.")

        # displaying results
        search_results = self.selenium.find_elements(By.CLASS_NAME, "search-result")

        for result in search_results:
            print(result.text)

        self.assertTrue(len(search_results) > 0, "No search results found")
        #search_button = self.selenium.find_element(By.ID, "search-button")
        #search_button.click()
        #self.selenium.implicitly_wait(100)
        #try:
            #self.selenium.find_element(By.XPATH, '//input[@placeholder="Search"]')
            #print("Successfully logged in, and the page is the home page.")
        #except:
            #search_results_indicator = WebDriverWait(self.selenium, 10).until(
                #EC.presence_of_element_located((By.ID, "search-results-indicator"))
            #)
            #self.assertIsNotNone(search_results_indicator)
        #except TimeoutException:
            #print("No result for this search")
        #query_input = self.selenium.find_element(By.NAME, "query")
        #query_input.send_keys("myquery")
        #self.selenium.find_element(By.XPATH, '//input[@value="search"]').click()
        #print(self.selenium.current_url)
        #self.assertEqual(self.selenium.current_url, 'http://localhost:5173/search', msg='something went wrong')
        #assert 'Django' in self.browser.title

    @classmethod
    def tearDownClass(cls):
        # Optionally, clean up the test Elasticsearch index after the tests
        #es = Elasticsearch(['http://localhost:9200'],)
        #index = TestArticleIndex._index._name
        #es.indices.delete(index=index)
        #test_index = Index('test_index')
        #test_index.delete()
        index_name = getattr(cls, 'current_index_name', None)
        if index_name:
            test_index = Index(index_name)
            test_index.delete()
        cls.selenium.quit()
        super().tearDownClass()

