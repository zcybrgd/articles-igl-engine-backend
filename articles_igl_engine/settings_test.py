from .settings import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'test_ArticlesBDD',
        'USER': 'postgres',
        'PASSWORD': 'TPIGL062023@//@',
        'HOST': '127.0.0.1',
        'PORT': '5432',
    }
}

TEST_RUNNER = 'django.test.runner.DiscoverRunner'