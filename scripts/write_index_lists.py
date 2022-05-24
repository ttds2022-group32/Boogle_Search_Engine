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


def generate_ivlist_flist(client, collection, session, index_db):
    '''return IO(token_dict: {token: {docId: [pos]}})'''
    '''field_dict {token:{docId: ["content","author","title"]}'''
    vocab_token, vocab_field = set(), set()
    token_dict = {}
    field_dict = {}
    refresh_time = datetime.now()
    # Loop through all the documents in the collection
    count = 0
    for i in collection.find(no_cursor_timeout=True, session=session):
        # refresh session if it is longer than 15 minutes
        elapsed = (datetime.now() - refresh_time).seconds / 60
        if elapsed > 15:
            logging.info("elapsed: {} refreshing session at {}".format(
                elapsed,
                datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
            client.admin.command('refreshSessions', [session.session_id],
                                 session=session)
            refresh_time = datetime.now()

        id = str(i["_id"])
        logging.info(id)
        tokens = i["tokens"]
        author = i["author"]
        title = i["title"]

        ## search for content
        if (len(tokens) == 0):
            continue

        for counter in range(len(tokens)):

            ## t is a token
            t = tokens[counter]

            ## for ivlist
            if t in token_dict:
                if id in token_dict[t]:
                    token_dict[t][id].append(counter)
                else:
                    token_dict[t][id] = [counter]
            else:
                token_dict[t] = {id: [counter]}

            ## for field list
            if t in field_dict:
                if id in field_dict[t]:
                    continue
                else:
                    field_dict[t][id] = ["content"]
            else:
                field_dict[t] = {id: ["content"]}

        # search for author and title field
        # assume the author and title are in right format
        # not preprocessing the Author so search for Auther would be different in content and title
        if author != None:
            ## the author is a dictionary {name:,year:}
            # I just split the name by space and no other preprocessing
            if author["name"] != "":
                tlist = author["name"].split()
                for t in tlist:
                    if t in field_dict:
                        if id in field_dict[t]:
                            field_dict[t][id].append("author")
                        else:
                            field_dict[t][id] = ["author"]
                    else:
                        field_dict[t] = {id: ["author"]}

        # search for title field
        # preprocessing the title as like content
        title = title.lower()
        titlelist = tokeniser(title)
        titlelist = stopword_remover(titlelist)
        titlelist = porter_stemmer(titlelist)

        ## added to field list
        for t in titlelist:
            if t in field_dict:
                if id in field_dict[t]:
                    field_dict[t][id].append("title")
                else:
                    field_dict[t][id] = ["title"]
            else:
                field_dict[t] = {id: ["title"]}

        count += 1
        ## seperate into 20 batches
        if count == 50:
            # write() and update vocab
            logging.info("The size of the dictionaries is {} and {} MB".format(
                sys.getsizeof(token_dict) / (1024 * 1024),
                sys.getsizeof(field_dict) / (1024 * 1024)))
            logging.info('Started writing')
            vocab_token, vocab_field = writeToMongo(token_dict, field_dict,
                                                    vocab_token, vocab_field,
                                                    index_db)
            logging.info('Writing finished')
            # clear()
            token_dict.clear()
            field_dict.clear()
            logging.info("The size of the dictionaries is {} and {} MB".format(
                sys.getsizeof(token_dict) / (1024 * 1024),
                sys.getsizeof(field_dict) / (1024 * 1024)))
            count = 0
    # write again when loop finished
    logging.info("The size of the dictionaries is {} and {} MB".format(
                sys.getsizeof(token_dict) / (1024 * 1024),
                sys.getsizeof(field_dict) / (1024 * 1024)))
    logging.info('Started final writing')
    vocab_token, vocab_field = writeToMongo(token_dict, field_dict,
                                            vocab_token, vocab_field,
                                            index_db)
    logging.info('Writing finished and function finished')
    

## function to write the two lists into MongoDB 
def writeToMongo(token_dict, field_dict, vocab_token, vocab_field, index_db):
    """write to mongodb, return new vocab"""
    for token, docIDs in token_dict.items():
        if token in vocab_token:
            # update
            for docID, pos in docIDs.items():
                index_db.iv.update_one(
                    {'_id': token}, {'$set': {
                        'docIDs.{}'.format(docID): pos
                    }},
                    upsert=False)
        else:
            # insert
            index_db.iv.insert_one({'_id': token, 'docIDs': docIDs})
            # update vocab
            vocab_token.add(token)

    for token, docIDs in field_dict.items():
        if token in vocab_field:
            # update
            for docID, l_of_fields in docIDs.items():
                index_db.field.update_one(
                    {'_id': token},
                    {'$set': {
                        'docIDs.{}'.format(docID): l_of_fields
                    }},
                    upsert=False)
        else:
            # insert
            index_db.field.insert_one({'_id': token, 'docIDs': docIDs})
            # update vocab
            vocab_field.add(token)
    return vocab_token, vocab_field








### main ###
## connect to the database

logging.basicConfig(filename='index.log', filemode='w', level=logging.DEBUG)
client = pymongo.MongoClient("localhost", 27017)

## open two new collections
index_db = client.index
iv, field = index_db.iv, index_db.field
logging.info("created db")
# read
db = client.book_information
collection = db.book_collection

logging.info("starting index")
with client.start_session() as session:
    generate_ivlist_flist(client, collection, session, index_db)

# # write the inverted index.txt
# filewriter = open("inverted_index.txt", "w", encoding="utf-8")
# for key in pvlist:
#     line = key + ":\n"
#     filewriter.write(line)
#     for key2 in pvlist[key]:
#         poslist = [str(x) for x in pvlist[key][key2]]
#         pos = ",".join(poslist)
#         line = "\t" + str(key2) + ": " + pos + "\n"
#         filewriter.write(line)
# filewriter.close()

# # write the field index.txt
# filewriter2 = open("field_index.txt", "w", encoding="utf-8")
# for key in flist:
#     line = key + ":\n"
#     filewriter2.write(line)
#     for key2 in flist[key]:
#         poslist = [str(x) for x in flist[key][key2]]
#         pos = ",".join(poslist)
#         line = "\t" + str(key2) + ": " + pos + "\n"
#         filewriter2.write(line)
# filewriter2.close()

client.close()

