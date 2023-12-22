import json
from faker import Faker
import random

fake = Faker()

# Generate 100 JSON objects
articles = []
for i in range(100):
    article = {
        "title": f"Sample Title {i + 1}",
        "authors": [fake.name() for _ in range(random.randint(1, 3))],
        "summary": fake.sentence(),
        "institutions": [fake.company() for _ in range(random.randint(1, 2))],
        "keywords": [fake.word() for _ in range(random.randint(2, 4))],
        "content": fake.paragraph(),
        "releaseDate": fake.date_between(start_date='-1y', end_date='today').strftime('%Y-%m-%d'),
        "pdfUrl": f"https://example.com/article{i + 1}.pdf",
        "references": [fake.sentence() for _ in range(random.randint(1, 2))]
    }
    articles.append(article)

# Write the JSON objects to a file
with open('D:/1CS/IGL/TP/articles-igl-engine-backend/core/elasticsearch/indexing_scripts/articles.json', 'w') as file:
    json.dump(articles, file, indent=4)
