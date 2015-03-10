# -*- coding: utf-8 -*-

from firebase import firebase
from firebase_token_generator import create_token

import os
import datetime
import json
import logging
import pickle
import gzip
from boto.s3.connection import S3Connection
from boto.s3.key import Key

import gflags
import httplib2
import pprint

import config 

from apiclient.discovery import build
from apiclient.http import MediaFileUpload
from oauth2client.client import OAuth2WebServerFlow
from oauth2client.tools import run


# Set logging level
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info('Starting firebase data backup now...')

#Use UTC time in key name
now = datetime.datetime.utcnow()
name = config.FILE_PREFIX + now.strftime('%Y-%m-%d--%H-%M-%S.%f') + '.json' 
gzip_name = name + '.gz'

h = httplib2.Http()

auth_payload = {"uid": "backup-user"}
options = {"admin":True, "debug": True}
firebase_token = create_token(config.FIREBASE_SECRET, auth_payload, options)

firebase_url = config.FIREBASE_URL + '.json?format=export&auth=' + firebase_token
logger.info('firebase_url = ' + firebase_url)

(resp_headers, data) = h.request(firebase_url, "GET")

f_out = gzip.open(gzip_name, 'wb')
f_out.write(data)
f_out.close()

# Check https://developers.google.com/drive/scopes for all available scopes
OAUTH_SCOPE = 'https://www.googleapis.com/auth/drive'

# Redirect URI for installed apps
REDIRECT_URI = 'urn:ietf:wg:oauth:2.0:oob'

# This can be used to get and save the OAuth credentials

# flow = OAuth2WebServerFlow(config.CLIENT_ID, config.CLIENT_SECRET, OAUTH_SCOPE, REDIRECT_URI)
# authorize_url = flow.step1_get_authorize_url()
# print 'Go to the following link in your browser: ' + authorize_url
# code = raw_input('Enter verification code: ').strip()
# credentials = flow.step2_exchange(code)
# pickle.dump(credentials, open('gdrive-credential.p', 'wb'))
# print 'Saved credentials in gdrive-credential'

credentials = pickle.load( open( "gdrive-credential.p", "rb" ) )

# Create an httplib2.Http object and authorize it with our credentials
http = httplib2.Http()
http = credentials.authorize(http)

drive_service = build('drive', 'v2', http=http)

# This can be used to create a new folder for your backups
# body = {
#     'title': "your-folder-name",
#     'mimeType': "application/vnd.google-apps.folder"
# }
# root_folder = drive_service.files().insert(body=body).execute()
# print 'root_folder id = ' + str(root_folder['id'])

# Insert a file

media_body = MediaFileUpload(gzip_name, mimetype='application/gzip', resumable=True)
body = {
  'title': gzip_name,
  'description': 'Red Tricycle Firebase backup => ' + gzip_name,
  'mimeType': 'application/x-gzip',
    "parents": [{
    "kind": "drive#fileLink",
    "id": '0B5QoGPys8P2qZlhaOWViOEFvaEk', #root_folder['id'],
    }]
}

file = drive_service.files().insert(body=body, media_body=media_body).execute()
#pprint.pprint(file)

os.remove(gzip_name)

logger.info('Done.')
