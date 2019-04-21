"""
    AUTHOR: Daniel Fitzpatrick
    HOW TO RUN: python scraper.py -f [path to .env]
            EG: python scraper.py -f /opt/test/.env
                python scraper.py -f /opt/test/
                python scraper.py -f /opt/test

"""

import urllib.request as req
from html.parser import HTMLParser
import pandas as pd
import sys
import os
import boto3
import logging
from botocore.exceptions import ClientError
from dotenv import load_dotenv


def upload_file(file_name, bucket, object_name=None):
    """Upload a file to an S3 bucket

    :param file_name: File to upload
    :param bucket: Bucket to upload to
    :param object_name: S3 object name. If not specified then file_name is used
    :return: True if file was uploaded, else False
    """

    # If S3 object_name was not specified, use file_name
    if object_name is None:
        object_name = file_name

    # Upload the file
    s3_client = boto3.client('s3')
    try:
        response = s3_client.upload_file(file_name, bucket, object_name)
    except ClientError as e:
        logging.error(e)
        return False
    return True


class myhtmlparser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.reset()
        self.data = []

    def handle_data(self, _data):
        _data.replace('\\xa0', '')

        self.data.append(_data)

    def clean(self):
        self.data = []


CWD = os.getcwd()
DOTENV_PATH = os.path.join(CWD, '.env')

if '-f' not in sys.argv:
    print('No .env file provided - default {}'.format(DOTENV_PATH))
else:
    index = sys.argv.index('-f') + 1
    DOTENV_PATH = sys.argv[index]

DOTENV_PATH = DOTENV_PATH if '.env' in DOTENV_PATH else str(os.path.join(DOTENV_PATH, '.env'))

if not os.path.exists(DOTENV_PATH):
    print('{} does not exist'.format(DOTENV_PATH))
    exit()
load_dotenv(dotenv_path=DOTENV_PATH)

"""
    Scrape the Irish Chess Union ratings website for my rating using icu id
    Parse the HTML
    Find the index for my name
    Add it to the output list
"""
with req.urlopen('https://ratings.icu.ie/icu_ratings?icu_id={}'.format(os.getenv('ICU_ID'))) as response:
    html = response.read()
    parser = myhtmlparser()
    parser.feed(str(html))

# Extract data from parser
data = parser.data
ind = data.index('Fitzpatrick, Daniel')
output = [['Irish Chess Union', data[ind + 2], data[ind + 4]]]

"""
    Scrape the FIDE ratings website for my ratings using fide id
    Parse the HTML
    Find the index for std. (classical) rating
    Find the index for rapid rating
    find the index for blitz rating
"""

with req.urlopen('https://ratings.fide.com/card.phtml?event={}'.format(os.getenv('FIDE_ID'))) as response:
    html = response.read()
    parser = myhtmlparser()
    parser.feed(str(html))

data = parser.data
ind = data.index('std.')
output.append(['FIDE Classical', '', data[ind + 1].replace('\\n', '')])

ind = data.index('rapid')
output.append(['FIDE Rapid', '', data[ind + 1].replace('\\n', '')])

ind = data.index('blitz')
output.append(['FIDE blitz', '', data[ind + 1].replace('\\n', '')])

pd.DataFrame(output).to_csv("ratings.csv", index=False, header=False)
upload_file(os.path.join(CWD, 'ratings.csv'), os.getenv('BUCKET_NAME'), 'ratings.csv')
os.remove('ratings.csv')