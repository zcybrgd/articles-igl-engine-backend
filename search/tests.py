#this file is for functional test for the search functionality
'''
Tests that use Selenium let us drive a real web browser, so they really let us see how the application functions from the user’s point
of view. That’s why they’re called functional tests. /*i brought this from a medium article i read while
learning about functional tests because i think it would be useful for students who will see this code*/
'''
#the client will open the page where the search bar appears, and s/he will enter a query
#the query gets executed and elastic search will decide the results
#the results will be displayed
import os
import unittest
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager


class NewVisitorTest(unittest.TestCase):
#we initialize the driver to remote our chrome browser
    def setUp(self):
        # creating temporary directory
        try:
            os.mkdir('temp')
        except FileExistsError:
            pass

        # creating directory to Append Driver
        try:
            os.mkdir('temp/driver')
        except FileExistsError:
            pass

        # initialize the browser
        self.driver = webdriver.Chrome(ChromeDriverManager(base_url='temp/driver').install())
    #when the test case is done
    def tearDown(self):
        self.driver.quit()

    # the unittest
    def test_start_web(self):
        url: str = 'http://127.0.0.1:8000/'
        self.driver.get(url=url)

        self.assertIn('Todo', self.driver.title)
        self.fail('test Finished')


if __name__ == '__main__':
    unittest.main()
'''
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from django.contrib.staticfiles.testing import StaticLiveServerTestCase

class SearchArticlesFunctionalTest(StaticLiveServerTestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.driver = webdriver.Chrome()

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()
        super().tearDownClass()

    def test_search_articles_functionality(self):
        self.driver.get(self.live_server_url)

        # Wait for the search input element by ID (replace 'search-input' with your actual ID)
        search_input = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, 'search-input'))
        )

        # Input the search term and press Enter
        search_term = 'your_search_term'
        search_input.send_keys(search_term + Keys.RETURN)

        # Wait for the search results container to load (replace 'search-results' with your actual ID or class)
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'search-results'))
        )

        # Assertions for validating search results
        self.assertIn(search_term, self.driver.page_source)

        # Check if the search results container is displayed
        search_results_container = self.driver.find_element(By.CLASS_NAME, 'search-results')
        self.assertTrue(search_results_container.is_displayed())

        # Additional assertions based on your specific search results structure
        # For example, check if specific search results are present in the page source
        self.assertIn('Result 1 Title', self.driver.page_source)
        self.assertIn('Result 2 Title', self.driver.page_source)
    '''