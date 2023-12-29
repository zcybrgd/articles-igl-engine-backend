from rest_framework.authentication import TokenAuthentication as BaseTokenAuthentication
from .models import NonUserToken


#to make the nonUserToken model created by us used in the authentication
class TokenAuthentication(BaseTokenAuthentication):
    model = NonUserToken