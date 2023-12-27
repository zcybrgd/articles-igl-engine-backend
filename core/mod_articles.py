import hashlib
import json
class ModArticles:
    def __init__(self, json_file_path='core/pdf_unreviewed.json'):
        self.json_file_path = json_file_path
        self.articles = self.load_articles()

    def load_articles(self):
        with open(self.json_file_path) as json_file:
            return json.load(json_file)

    def save_articles(self):
        with open(self.json_file_path, 'w') as json_file:
            json.dump(self.articles, json_file, indent=2)

    def update_article(self, article_id, updated_data):
        for article in self.articles:
            if article.get('id') == article_id:
                article.update(updated_data)
                break
        self.save_articles()

    def delete_article(self, article_id):
        print("\ndid we enter here\n")
        self.articles = [article for article in self.articles if article.get('id') != article_id]
        print("\nand what about hr; : ", self.articles)
        self.save_articles()

    def add_article(self, new_article_data):
        # Assuming each article has a unique identifier ('id')
        new_article_data['id'] = hashlib.md5(str(new_article_data).encode('utf-8')).hexdigest()
        self.articles.append(new_article_data)
        self.save_articles()