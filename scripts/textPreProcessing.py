#%%
import pymongo
import datetime
import re
import logging

logging.basicConfig(filename='example.log', encoding='utf-8', level=logging.DEBUG)
# client = pymongo.MongoClient("mongodb://ttds_user:IKV2jOEFyzY8PxFa@ttds0-shard-00-00.jt4gg.mongodb.net:27017,ttds0-shard-00-01.jt4gg.mongodb.net:27017,ttds0-shard-00-02.jt4gg.mongodb.net:27017/gutenburg?ssl=true&replicaSet=atlas-z0peja-shard-0&authSource=admin&retryWrites=true&w=majority")
client = pymongo.MongoClient("localhost", 27017)

db = client.preprocess_books
collection = db.book_paragraph
logging.info("db: preprocess_books")
logging.info("book_paragraph")

#%%
from nltk.stem import PorterStemmer

##### functions for text pre-processing #####
def tokeniser(context):
    '''Split on every non-letter characters. Returns a list of tokens'''

    non_letter_list = "!\"#$%″&′'’‘()*…+, —-./:;<=>?@[\]^_`{|}~0123456789“”"
    # change all the occurances of non letter characters into space and upper case letter into lower case letter
    # split the whole paragraph into a lists of words by using space as separator
    non_letter_table = context.maketrans(non_letter_list, ' '*len(non_letter_list))

    return context.translate(non_letter_table).lower().split()

def stopword_remover(word_list):
    '''Remove all the occurances of stopword from the word list. Return a list of words.'''
    
    # read stop word list
    f = open("englishST.txt","r")
    stopWord = [w.strip() for w in f.readlines()]
    f.close

    return [i for i in word_list if i not in stopWord]

def porter_stemmer(word_list):
    '''Stem the words in the word list by using Porter Stemmer. Return a list of stemmed words.'''

    porter = PorterStemmer()

    return [porter.stem(i) for i in word_list]

def dateParser(yearInStr):
    date = yearInStr[0:10]
    yy = date[0:4]
    mm = date[5:7]
    dd = date[8:10]

    return int(yy),int(mm),int(dd)

#%%
for i in collection.find():
    
    unique_id = i["_id"]
    logging.info(unique_id)
    
    title = i["title"]
    reParse_title = " ".join(title.replace("\r\n", "").split())

    content = i["content"]
    reParse_content = " ".join(content.replace("\r\n", "").split())
    tokens = porter_stemmer(stopword_remover(tokeniser(content)))

    collection.update_one({'_id' : unique_id}, {'$set' : {'title': reParse_title, 'content': reParse_content, 'tokens' : tokens}})

    date = i["year"]
    if not isinstance(date, datetime.datetime):
        yy,mm,dd = dateParser(date)
        year = datetime.datetime(yy, mm, dd)
        collection.update_one({'_id' : unique_id}, {'$set' : {'year':year}})
    # i["year"].date() will get date in the form of yy-mm-dd
    # i["year"].year returns yy
    # i["year"].month returns mm
    # i["year"].day returns dd

    author_list = i["author"]
    if not isinstance(author_list, dict):
        items = author_list.split(", ")
        items.reverse()
        name = ""
        year = ""
        length = len(items)
        for j in range(length):
            if items[j].lower() != "none" and items[j].lower() != "unknown":
                if not re.search('[0-9]+', items[j]):
                    name += items[j]
                    if j != length - 1:
                        name += " "
                else:
                    year = items[j]
            else:
                year = ""
                break
        
        collection.update_one({'_id' : unique_id}, {'$set' : {'author':{'name': name,'year':year}}})
#%%
client.close()

