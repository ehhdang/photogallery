import os

AWS_ACCESS_KEY_ID = os.environ['AWS_ACCESS_KEY_ID']
AWS_SECRET_ACCESS_KEY = os.environ['AWS_SECRET_ACCESS_KEY']
BUCKET_NAME = os.environ['BUCKET_NAME']

DB_HOSTNAME = os.environ['DB_HOSTNAME']
DB_USERNAME = "root"
DB_PORT = 3306
DB_PASSWORD = os.environ['DB_PASSWORD']
DB_NAME = "mydb"
TABLE_NAME = "photogallery"
REGION = os.environ['REGION']