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
            'firstName': 'MAROU',
            'familyName': 'DJ',
            'email': 'MAROUdJ@gmail.com'

        }

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)  # If a successful signup returns 201
        self.assertTrue('token' in response.data)  # Assuming the response includes a token
        if response.status_code == status.HTTP_201_CREATED:
         token = response.data.get('token')
         if token:
            print(f"Signup successful! Token obtained: {token}")
         else:
            print("Token not found in the response data.")
        else:
         print("Signup failed. Check the signup endpoint or data provided.")

    def test_login(self):
        url = 'http://127.0.0.1:8000/us/login'
        data = {
             
             "password":"my_test_nchalah_ymchi_1"
            }

        response = self.client.post(url, data, format='json')
        print(f"Response content: {response.content}")
        self.assertEqual(response.status_code,400)  # Assuming a successful login returns 200
        
        

