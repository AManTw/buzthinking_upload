"""Uploads or downloads files between Google Cloud Storage and the filesystem.
The file is transfered in CHUNKSIZE pieces, and the process can resume in case
of some failures.
Usage examples:
  $ python chunked_transfer.py gs://bucket/object ~/Desktop/filename
  $ python chunked_transfer.py ~/Desktop/filename gs://bucket/object
"""

import httplib2
import os
import random
import sys
import time
import re
from os import listdir
from os.path import isfile, isdir, join
from apiclient.discovery import build as discovery_build
from apiclient.errors import HttpError
from apiclient.http import MediaFileUpload
from apiclient.http import MediaIoBaseDownload
from json import dumps as json_dumps
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage as CredentialStorage
from oauth2client.tools import run_flow as run_oauth2


# CLIENT_SECRETS_FILE, name of a file containing the OAuth 2.0 information for
# this application, including client_id and client_secret. You can acquire an
# ID/secret pair from the API Access tab on the Google APIs Console
#   <http://code.google.com/apis/console#access>
# For more information about using OAuth2 to access Google APIs, please visit:
#   <https://developers.google.com/accounts/docs/OAuth2>
CLIENT_SECRETS_FILE = 'client_secrets.json'

# File where we will store authentication credentials after acquiring them.
CREDENTIALS_FILE = '/home/jerrychen/Downloads/FireShot/credentials.json'

# Message describing how to use the script.
USAGE = """
Usage examples:
  $ python chunked_transfer.py gs://bucket/object ~/Desktop/filename
  $ python chunked_transfer.py ~/Desktop/filename gs://bucket/object
"""

RW_SCOPE = 'https://www.googleapis.com/auth/devstorage.read_write'
RO_SCOPE = 'https://www.googleapis.com/auth/devstorage.read_only'

# Helpful message to display if the CLIENT_SECRETS_FILE is missing.
MISSING_CLIENT_SECRETS_MESSAGE = """
WARNING: Please configure OAuth 2.0
To make this sample run you will need to populate the client_secrets.json file
found at:
   %s
with information from the APIs Console
<https://code.google.com/apis/console#access>.
""" % os.path.abspath(os.path.join(os.path.dirname(__file__),
                                   CLIENT_SECRETS_FILE))

# Retry transport and file IO errors.
RETRYABLE_ERRORS = (httplib2.HttpLib2Error, IOError)

# Number of times to retry failed downloads.
NUM_RETRIES = 5

# Number of bytes to send/receive in each request.
CHUNKSIZE = 2 * 1024 * 1024

# Mimetype to use if one can't be guessed from the file extension.
DEFAULT_MIMETYPE = 'application/octet-stream'


def get_authenticated_service(scope):
  print ('Authenticating...')
  flow = flow_from_clientsecrets(CLIENT_SECRETS_FILE, scope=scope,message=MISSING_CLIENT_SECRETS_MESSAGE)

  credential_storage = CredentialStorage(CREDENTIALS_FILE)
  credentials = credential_storage.get()
  if credentials is None or credentials.invalid:
    credentials = run_oauth2(flow, credential_storage)

  print ('Constructing Google Cloud Storage service...')
  http = credentials.authorize(httplib2.Http())
  return discovery_build('storage', 'v1', http=http)


def handle_progressless_iter(error, progressless_iters):
  if progressless_iters > NUM_RETRIES:
    print ('Failed to make progress for too many consecutive iterations.')
    raise error

  sleeptime = random.random() * (2**progressless_iters)
  print ('Caught exception (%s). Sleeping for %s seconds before retry #%d.'
         % (str(error), sleeptime, progressless_iters))
  time.sleep(sleeptime)


def print_with_carriage_return(s):
  sys.stdout.write('\r' + s)
  sys.stdout.flush()


def upload(filename,gc):
  #filename = argv[1]
  bucket_name, object_name = gc[5:].split('/', 1)
  assert bucket_name and object_name

  service = get_authenticated_service(RW_SCOPE)

  print ('Building upload request...')
  media = MediaFileUpload(filename, chunksize=CHUNKSIZE, resumable=True)
  if not media.mimetype():
    media = MediaFileUpload(filename, DEFAULT_MIMETYPE, resumable=True)
  request = service.objects().insert(bucket=bucket_name, name=object_name, media_body=media)

  print ('Uploading file: %s to bucket: %s object: %s ' % (filename, bucket_name, object_name))

  progressless_iters = 0
  response = None
  while response is None:
    error = None
    try:
      progress, response = request.next_chunk()
      if progress:
        print_with_carriage_return('Upload %d%%' % (100 * progress.progress()))
    except HttpError as err:
      error = err
      if err.resp.status < 500:
        raise
    except RETRYABLE_ERRORS as err:
      error = err

    if error:
      progressless_iters += 1
      handle_progressless_iter(error, progressless_iters)
    else:
      progressless_iters = 0

  print ('\nUpload complete!')

  print ('Uploaded Object:')
  print (json_dumps(response, indent=2))

def name_restting(rename):
    cut = " - PressPlay 訂閱學習，時刻精進"
    name = re.sub(cut,'',rename)
    name = re.sub("｜",'|',name)
    name = re.sub("【",'[',name)
    name = re.sub("】",']',name)
    name = re.sub("\.", " ", name)
    name = name.split(" ")
    for i in range(len(name)):
        if i == 0 :
            rename=name[i]
            rename+='.'
        elif i == len(name)-1:
            rename+='.'
            rename+=name[i]
        else :
            rename+=name[i]

    print (rename)
    return rename

def main():

    mypath="/home/jerrychen/Downloads/FireShot/150_size"
    files = listdir(mypath)

    # 以迴圈處理
    for filePDF in files:
        # 產生檔案的絕對路徑
        fullpath = join(mypath, filePDF)
        # fullpath 是檔案
        if isfile(fullpath):
            name=name_restting(filePDF)
            new_fullpath = join(mypath,name)
            os.rename(fullpath, new_fullpath)
            print("=====執行上傳檔案=====")
            upload(filename=new_fullpath, gc="gs://bucket/object")
            print("=====上傳檔案完成=====")
            exit(0)


if __name__ == '__main__':
    main()

