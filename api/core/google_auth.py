from authlib.integrations.starlette_client import OAuth
import os
from dotenv import load_dotenv

load_dotenv()

class GoogleAuth:
    def __init__(self):
        self.oauth = OAuth()
        self.oauth.register(
            name='google',
            client_id=os.getenv('GOOGLE_CLIENT_ID'),
            client_secret=os.getenv('GOOGLE_CLIENT_SECRET'),
            server_metadata_url='https://accounts.google.com/.well-known/openid_configuration',
            client_kwargs={
                'scope': 'openid email profile'
            }
        )
    
    async def authorize_redirect(self, request, redirect_uri):
        return await self.oauth.google.authorize_redirect(request, redirect_uri)
    
    async def authorize_access_token(self, request):
        return await self.oauth.google.authorize_access_token(request)