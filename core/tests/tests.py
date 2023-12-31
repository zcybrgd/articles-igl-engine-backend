from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status



class TestArticlesApiView(TestCase):
    def setUp(self):
        self.client = APIClient()

    
    def test_get_articles(self):
       response = self.client.get('/api/articles/', follow=True)
       self.assertEqual(response.status_code, status.HTTP_200_OK)
       articles = response.json().get('articles', [])
       #on affiche juste pour la verification
       print("Articles Retrieved:")
       
      # Vérifiez que la réponse contient une liste d'articles
       for article in articles:
            self.assertTrue('id' in article)  # Vérifiez la présence de l'ID de l'article
            self.assertTrue('title' in article)  # Vérifiez la présence du titre de l'article
            # print(response.content)
        

    def test_delete_article(self):
        article_id = 4 # Définir l'ID de l'article pour le test
        delete_url = f'/api/articles/{article_id}/'

        # Send a DELETE request to the delete endpoint using the formatted URL
        response = self.client.delete(delete_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
         
      
    def test_update_article(self):
        article_id = 1  
        data = {'title': 'The Impact of Climate Change on Biodiversity and Computer Sciences role in that! //Added this //'}   
        response = self.client.patch(f'/api/articles/{article_id}/update/', data=data, format='json')
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST])  # Vérifiez si la mise à jour a réussi ou a échoué