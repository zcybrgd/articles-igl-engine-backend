import json
from django.core.management import call_command
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
from elasticsearch_dsl import connections, Index
from django.test import LiveServerTestCase
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from datetime import datetime


class FunctionalTest(LiveServerTestCase):
    fixtures = ["user_data.json"]
    #port to fix it in the frontend code too to let it know and work with the test server, or else it will be given a random free port
    port = 57262

    @classmethod
    def setUpClass(cls):
        #load the fixtures into the test database
        print("Loading fixtures...")
        call_command('loaddata', *cls.fixtures)
        print("Fixtures loaded successfully.")
        #creating the index for the testing articles and indexing them in elasticsearch
        connections.create_connection(alias='default', hosts=['http://localhost:9200'])
        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        index_name = f'test_index_{timestamp}'
        test_index = Index(index_name)
        test_index.create()
        cls.index_documents('search/test_articles.json', index_name)
        #set up the class and the selenium webdriver
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
        #connecting to the frontend server
        self.selenium.get("http://localhost:5173/login")
        #using the user_date information to login to the website using the testdatabase
        username_elem = self.selenium.find_element(By.XPATH, '//input[@placeholder="username"]')
        username_elem.send_keys("Marii")
        password_elem = self.selenium.find_element(By.XPATH, '//input[@placeholder="password"]')
        password_elem.send_keys("mariCLIENT")
        self.selenium.find_element(By.XPATH, '//button[contains(text(), "Log in")]').click()
        #waiting for the home page of the client to appear
        search_input = WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located((By.ID, "searchBar"))
        )
        #to test the ideal case , when the articles exist in the index
        #search_input.send_keys("article")
        #to test that when there is not an article verfiying the query , the website doesn't crush
        search_input.send_keys("TEST")
        #to be able to make the first query work, articles should be indexed using the command python manage.py update_elasticsearch and validated by the moderator
        self.selenium.implicitly_wait(10)
        search_button = self.selenium.find_element(By.ID, "search-button")
        search_button.click()
        #waiting for the search results to appear on the search page
        WebDriverWait(self.selenium, 10).until(
                EC.presence_of_element_located((By.ID, "search-results"))
            )
        self.selenium.implicitly_wait(10)
        #we verify if the test worked by confirming that it is currenlty in the search page
        self.assertEqual(self.selenium.current_url, 'http://localhost:5173/search', msg='something went wrong')

    @classmethod
    def tearDownClass(cls):
        #deleting the test index
        index_name = getattr(cls, 'current_index_name', None)
        if index_name:
            test_index = Index(index_name)
            test_index.delete()
        cls.selenium.quit()
        super().tearDownClass()

