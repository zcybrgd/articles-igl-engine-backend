#!/bin/bash


wait_for_elasticsearch() {
    echo "Waiting for Elasticsearch to be ready..."
    until response=$(curl -sSf "http://elasticsearch:9200" 2>&1); do
        if [[ $response == *"Failed to connect"* ]]; then
            >&2 echo "Elasticsearch is not yet ready - sleeping"
        else
            echo "Elasticsearch is ready!"
            echo "Response from Elasticsearch:"
            echo "$response"
            break
        fi
        sleep 1
    done
}


# Execute Elasticsearch check
wait_for_elasticsearch

echo "Creating Migrations..."
python ./backend/articles_igl_engine/manage.py makemigrations
echo "===================================="

echo "Starting Migrations..."
python ./backend/articles_igl_engine/manage.py migrate
echo "===================================="

echo "Checking for superuser..."
python ./backend/articles_igl_engine/manage.py shell <<EOF
from django.contrib.auth.models import User

if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'password')
    print("Superuser 'admin' created successfully.")
else:
    print("Superuser 'admin' already exists.")
EOF

echo "Executing initial admin creation..."
python ./backend/articles_igl_engine/manage.py shell <<EOF
from django.contrib.auth.models import User
from Users.models import Admin, user

admins = User.objects.all()
for ad in admins:
    adBdd, created = Admin.objects.get_or_create(id=ad.id)
    if created:
        userAdmin = user(userName=ad.username, password=ad.password, role='Administrator')
        userAdmin.save()
        Admin.objects.filter(id=adBdd.id).update(userId=userAdmin.pk)
EOF

echo "Updating Elasticsearch index..."
python ./backend/articles_igl_engine/manage.py update_elasticsearch
echo "===================================="

echo "Starting Server..."
python ./backend/articles_igl_engine/manage.py runserver 0.0.0.0:8000
