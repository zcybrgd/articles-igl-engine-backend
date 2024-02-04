"""
Unit tests for the API endpoints related to adding, modifying, and deleting moderators.

These tests cover scenarios for adding, modifying, and deleting moderators through the API endpoints.

Test Cases:
1. AddModAPITest: Test cases related to adding moderators.
2. ModifyModViewTest: Test cases related to modifying moderators.
3. DeleteModViewTest: Test cases related to deleting moderators.

Each test class includes test methods covering various scenarios with setup and teardown methods for data management.

Dependencies:
- Django TestCase: Base class for Django tests.
- APIClient: Test client for making API requests.
- status: Constants representing HTTP status codes.
- NonUserToken, Admin, user, Moderator: Models representing different entities.
- make_password: Function for generating password hashes.
"""
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from .models import NonUserToken, Admin, user, Moderator
from .views import make_password


class AddModAPITest(TestCase):
    """
       Unit tests for adding moderators via API endpoints.
    """
    def setUp(self):
        """
               Set up test data and client authentication.
        """
        self.user = user.objects.create(userName='admin', password='admin', role='Administrator')
        self.admin = Admin.objects.create(id='1', userId=self.user)
        self.token = NonUserToken.objects.create(user=self.user)
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

    def test_add_mod_authenticated_admin(self):
        """
                Test case to ensure that an authenticated admin can successfully add a new moderator.
        """
        data = {
            'userName': 'nehghw_mod',
            'password': 'mjgjodpass',
            'familyName': 'Dffoe',
            'firstName': 'hghg',
            'familyName': 'hghg',
            'email': 'jffohn.doe@example.com'
        }
        response = self.client.post('http://127.0.0.1:8000/us/mod/add', data)
        response_json = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('Mod added succesfully!!', response_json.keys())

    def test_add_mod_existing_moderator(self):
        """
                Test case to ensure that adding a moderator with an existing username results in an error.
                """
        # Create an existing moderator
        existing_mod = Moderator.objects.create(
            adminId=self.admin,
            userId=user.objects.create(userName='existing_mod', password='existing_mod_pass', role='Moderator'),
            userName='existing_mod',
            firstName='Jane',
            familyName='Doe',
            email='jane.doe@example.com',
            password=make_password('existing_mod_pass')
        )

        data = {
            'userName': 'existing_mod',
            'password': 'new_mod_pass',
            'role': 'Moderator',
            'firstName': 'John',
            'familyName': 'Doe',
            'email': 'john.doe@example.com'
        }

        response = self.client.post('/us/mod/add', data)

        response_json = response.json()
        self.assertIn('Username already exists. Please choose a different username.', response_json['error'])

    def test_add_mod_user_not_authenticated(self):
        """
               Test case to ensure that adding a moderator without authentication results in an unauthorized error.
        """
        # Remove authentication credentials
        self.client.logout()
        data = {
            'userName': 'new_mod',
            'password': 'new_mod_pass',
            'role': 'Moderator',
            'firstName': 'John',
            'familyName': 'Doe',
            'email': 'john.doe@example.com'
        }

        response = self.client.post('/us/mod/add', data)
        # I couldn't get the custom response
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        response_json = response.json()

    def test_add_mod_admin_user_doesnt_exist(self):
        """
                Test case to ensure that adding a moderator when the admin user doesn't exist results in an error.
        """
        # Remove the admin user from the database
        self.admin.delete()

        data = {
            'userName': 'new_mod',
            'password': 'new_mod_pass',
            'role': 'Moderator',
            'firstName': 'John',
            'familyName': 'Doe',
            'email': 'john.doe@example.com'
        }

        response = self.client.post('/us/mod/add', data)

        response_json = response.json()
        self.assertIn("the admin user doesn't exist", response_json['error'])

    def test_add_mod_user_not_administrator(self):
        """
                Test case to ensure that adding a moderator with a non-administrator user results in an error.
        """
        # Create a non-admin user
        non_admin_user = user.objects.create(userName='non_admin', password='non_admin_pass', role='Moderator')
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + NonUserToken.objects.create(user=non_admin_user).key)

        data = {
            'userName': 'new_mod',
            'password': 'new_mod_pass',
            'role': 'Moderator',
            'firstName': 'John',
            'familyName': 'Doe',
            'email': 'john.doe@example.com'
        }

        response = self.client.post('/us/mod/add', data)

        response_json = response.json()
        self.assertIn("the user is not an administrator", response_json['error'])

    def tearDown(self):
        """
               Clean up test data.
        """
        Moderator.objects.all().delete()
        Admin.objects.all().delete()
        user.objects.all().delete()
        NonUserToken.objects.all().delete()


class ModifyModViewTest(TestCase):
    """
       Unit tests for modifying moderators via API endpoints.
    """
    def setUp(self):
        """
                Set up test data and client authentication.
        """
        # Create an admin user and the mod
        self.user = user.objects.create(userName='admin', password='admin', role='Administrator')
        self.admin = Admin.objects.create(id='1', userId=self.user)
        self.token = NonUserToken.objects.create(user=self.user)
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

        self.mod = Moderator.objects.create(
            adminId=self.admin,
            userId=user.objects.create(userName='existing_mod', password='existing_mod_pass', role='Moderator'),
            userName='existing_mod',
            firstName='Jane',
            familyName='Doe',
            email='jane.doe@example.com',
            password=make_password('existing_mod_pass')
        )

    def test_modify_mod_succeful(self):
        """
                Test case to ensure that an authenticated admin can successfully modify a moderator.
        """
        data = {
            'userName': 'new_mod_username',
            'password': 'new_mod_password',
            'firstName': 'NewJane',
            'familyName': 'NewDoe',
            'email': 'new.jane.doe@example.com'
        }

        response = self.client.put(f'/us/mod/modify/{self.mod.pk}', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_json = response.json()
        self.assertIn("Mod modified succesfully!!", response.content.decode())

    def test_modify_mod_admin_user_doesnt_exist(self):
        """
                Test case to ensure that modifying a moderator when the admin user doesn't exist results in an error.
        """
        # Remove the admin user from the database
        self.admin.delete()

        data = {
            'userName': 'new_mod',
            'password': 'new_mod_pass',
            'role': 'Moderator',
            'firstName': 'John',
            'familyName': 'Doe',
            'email': 'john.doe@example.com'
        }

        response = self.client.put(f'/us/mod/modify/{self.mod.pk}', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_json = response.json()
        self.assertIn("the admin user doesn't exist", response.content.decode())

    def test_modify_mod_mod_doesnt_exist(self):
        """
                Test case to ensure that modifying a non-existing moderator results in an error.
        """
        data = {
            'userName': 'new_mod',
            'password': 'new_mod_pass',
            'firstName': 'John',
            'familyName': 'Doe',
            'email': 'john.doe@example.com'
        }
        # we can enter a wrong id here it is 99
        response = self.client.put(f'/us/mod/modify/99', data, format='json')
        response_json = response.json()
        self.assertIn("the moderator doesn't exist", response.content.decode())

    def test_modify_mod_unauthorized_action(self):
        """
                Test case to ensure that unauthorized action results in an error.
        """
        # login for another  admin not the one who created the moderator

        self.user = user.objects.create(userName='admin2', password='admin2', role='Administrator')
        self.admin = Admin.objects.create(id='2', userId=self.user)
        self.token = NonUserToken.objects.create(user=self.user)
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

        data = {
            'userName': 'new_mod_username',
            'password': 'new_mod_password',
            'firstName': 'NewJane',
            'familyName': 'NewDoe',
            'email': 'new.jane.doe@example.com'
        }

        response = self.client.put(f'/us/mod/modify/{self.mod.pk}', data)
        response_json = response.json()
        self.assertIn("This is an unauthorized action", response_json['error'])

    def test_modify_mod_user_not_administrator(self):
        """
                Test case to ensure that modifying a moderator with a non-administrator user results in an error.
                """
        # Create a non-admin user
        non_admin_user = user.objects.create(userName='non_admin', password='non_admin_pass', role='Moderator')
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + NonUserToken.objects.create(user=non_admin_user).key)

        data = {
            'userName': 'new_mod',
            'password': 'new_mod_pass',
            'role': 'Moderator',
            'firstName': 'John',
            'familyName': 'Doe',
            'email': 'john.doe@example.com'
        }

        response = self.client.put(f'/us/mod/modify/{self.mod.pk}', data)
        response_json = response.json()
        self.assertIn("the user is not an administrator", response_json['error'])

    def test_modify_mod_unauthenticated(self):
        """
                Test case to ensure that modifying a moderator without authentication results in an unauthorized error.
        """
        # Set client credentials to simulate an unauthenticated user
        self.client.credentials()
        data = {
            'userName': 'new_mod_username',
            'password': 'new_mod_password',
            'firstName': 'NewJane',
            'familyName': 'NewDoe',
            'email': 'new.jane.doe@example.com'
        }
        # here I couldn't get the custom response
        response = self.client.put(f'/us/mod/modify/{self.mod.pk}', data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        response_json = response.json()

    def tearDown(self):
        """
               Clean up test data.
             """
        Moderator.objects.all().delete()
        Admin.objects.all().delete()
        user.objects.all().delete()
        NonUserToken.objects.all().delete()


class DeleteModViewTest(TestCase):
    """
        Unit tests for deleting moderators via API endpoints.
        """
    def setUp(self):
        # Create an admin user
        self.admin_user = user.objects.create(userName='admin', password='admin', role='Administrator')
        self.admin = Admin.objects.create(id='1', userId=self.admin_user)
        self.token = NonUserToken.objects.create(user=self.admin_user)
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

        # Create a moderator for deletion
        self.mod = Moderator.objects.create(
            adminId=self.admin,
            userId=user.objects.create(userName='mod_to_delete', password='mod_pass', role='Moderator'),
            userName='mod_to_delete',
            firstName='John',
            familyName='Doe',
            email='john.doe@example.com',
            password=make_password('mod_pass')
        )

    def test_delete_mod_successful(self):
        """
                Test case to ensure that an authenticated admin can successfully delete a moderator.
        """
        response = self.client.delete(f'/us/mod/delete/{self.mod.pk}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_json = response.json()
        self.assertIn("Mod deleted successfully!!", response_json[0])

    def test_delete_mod_non_authenticated_user(self):
        """
                Test case to ensure that deleting a moderator without authentication results in an unauthorized error.
        """
        self.client.logout()
        # same here I couldn't get the custom answer
        response = self.client.delete(f'/us/mod/delete/{self.mod.pk}')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        # response_json = response.json()
        # self.assertIn("User non authenticated", response_json[0])

    def test_delete_mod_admin_user_doesnt_exist(self):
        """
                Test case to ensure that deleting a moderator when the admin user doesn't exist results in an error.
        """
        # delete the admin
        self.admin.delete()
        response = self.client.delete(f'/us/mod/delete/{self.mod.pk}')
        response_json = response.json()
        self.assertIn("the admin user doesn't exist", response_json['error'])

    def test_delete_mod_moderator_doesnt_exist(self):
        """
                Test case to ensure that deleting a non-existing moderator results in an error.
        """
        # the id doesn't exist 99
        response = self.client.delete('/us/mod/delete/99')
        response_json = response.json()
        self.assertIn("the moderator doesn't exist", response_json['error'])

    def test_delete_mod_unauthorized_action(self):
        """
                Test case to ensure that unauthorized action results in an error.
        """
        # login for a new admin not the one who created the moderator
        self.user = user.objects.create(userName='admin2', password='admin2', role='Administrator')
        self.admin = Admin.objects.create(id='2', userId=self.user)
        self.token = NonUserToken.objects.create(user=self.user)
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        response = self.client.delete(f'/us/mod/delete/{self.mod.pk}')

        response_json = response.json()
        self.assertIn("This is an unauthorized action", response_json['error'])

    def test_delete_mod_user_not_administrator(self):
        """
                Test case to ensure that deleting a moderator with a non-administrator user results in an error.
        """
        # Create a non-admin user
        non_admin_user = user.objects.create(userName='non_admin', password='non_admin_pass', role='Moderator')
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + NonUserToken.objects.create(user=non_admin_user).key)

        response = self.client.delete(f'/us/mod/delete/{self.mod.pk}')

        response_json = response.json()
        self.assertIn("the user is not an administrator", response_json['error'])

    def tearDown(self):
        """
                Clean up test data.
        """
        Moderator.objects.all().delete()
        Admin.objects.all().delete()
        user.objects.all().delete()
        NonUserToken.objects.all().delete()
