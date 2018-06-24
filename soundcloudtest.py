from soundcloud import *
import flask
# create client object with app credentials
client = Client(client_id='cceef6fde2f4b727afc26fb48ea314c3',
               client_secret='7aff3322f29c4f3f7659a23dd2aa0102',
               redirect_uri='http://localhost:8880/')
print(client.__dict__)
# redirect user to authorize URL
flask.redirect(client.authorize_url())

# # exchange authorization code for access token
# code = params['code']
# access_token = client.exchange_token(code)