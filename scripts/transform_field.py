import pymongo
from processingLib import *
import logging
import sys
from datetime import datetime
## SPIMI
## 2 mongodb collections
## 1. token (UniqueID) : Dict[Docid]: [pos]
## 2. token (UniqueID) : Dict[Docid]: [content, author, title]
## merge:  when write: for each check if in mongodb

##### function for creating a ivlsit and field list #####


def transform_field(client, session, field, new_field):
    """
    field_dict {token:{docId: ["content","author","title"]}
    to
    {token: {author: set(docId)]},{title: set(docId)]}}
    """
    refresh_time = datetime.now()
    for i in field.find(no_cursor_timeout=True, session=session):
        # refresh session if it is longer than 15 minutes
        elapsed = (datetime.now() - refresh_time).seconds / 60
        if elapsed > 15:
            logging.info("elapsed: {} refreshing session at {}".format(
                elapsed,
                datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
            client.admin.command('refreshSessions', [session.session_id],
                                 session=session)
            refresh_time = datetime.now()

        token = i["_id"]

        # for each token: transform the other dict
        author, title = [], []
        for docId, tag_list in i["docIDs"].items():
            if "author" in tag_list:
                author.append(docId)
            if "title" in tag_list:
                title.append(docId)
        logging.info(f"processing token {token}")
        new_field.insert_one({'_id': token, 'author': author, 'title': title})
        # clear set
        author.clear()
        title.clear()


### main ###
## connect to the database

logging.basicConfig(filename='new_field_index.log',
                    filemode='w',
                    level=logging.DEBUG)
client = pymongo.MongoClient("localhost", 27017)

## open two new collections
index_db = client.index
field, new_field = index_db.field, index_db.new_field
logging.info("created db")

with client.start_session() as session:
    transform_field(client, session, field, new_field)

client.close()
