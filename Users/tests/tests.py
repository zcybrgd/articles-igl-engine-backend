from rest_framework import status
from rest_framework.test import APITestCase

from django.urls import reverse
from social_core.pipeline import user


class UserAPITest(APITestCase):
    def test_signup(self):
        url = 'http://127.0.0.1:8000/us/signup'
        data = {
            'userName': 'Maroumarou',
            'password': 'tp@igl@20',
            'firstName': 'This field is required.',
            'familyName': 'This field is required.',
            'email': 'This field is required@gmail.com'

        }

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)  # If a successful signup returns 201
        self.assertTrue('token' in response.data)  # Assuming the response includes a token


    def test_login(self):
        url = 'http://127.0.0.1:8000/us/login'
        data = {
            'userName': 'Maroumarou',
            'password': 'tp@igl@20', }

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, 200)  # Assuming a successful login returns 200


