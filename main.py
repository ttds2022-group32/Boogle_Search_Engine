import logging
from collections import deque
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from query_score_rank import parse_query, TFIDFscore, search_rank
from pymongo import MongoClient
from processingLib import output_Frontend, output_using_pos
import json
from fastapi.middleware.cors import CORSMiddleware
from query_expansion import expand_query
from bson.objectid import ObjectId
import random
import re
import requests

app = FastAPI()
logger = logging.getLogger('uvicorn')

# CORS
origins = [
    "http://localhost.tiangolo.com", "https://localhost.tiangolo.com",
    "http://localhost", "http://localhost:8000", "http://localhost:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# build inverted index and field list by write_index_lists.py which is pre-runned
client = MongoClient('localhost', 27017)

## open inverted list and field list
index_db = client.index
iv, field = index_db.iv, index_db.new_field
"""iv: {"_id": token, "docIDs":{id:[pos]}}
field: {"_id": token, "author": [], "title" : []}"""

# read small
db = client.book_information
collection = db.book_collection

# count the number of the doc in contents
n = collection.count()


class IndexQ:
    def __init__(self, k, index_coll, is_field):
        self.index_coll = index_coll
        self.q = deque()  # queue of tokens
        self.iv = {}  # {token:{id:[pos]}} or {token: {author: [], title:[]}}
        self.limit = k
        self.is_field = is_field
        count = 0
        for i in self.index_coll.find():
            count += 1
            token = i["_id"]
            self.q.append(token)
            self.append(token)
            if count >= k * 2 // 3:  # take 2/3 of limit
                break

    def get(self, token):
        """return a dictionary of {token:[pos]}"""
        if token not in self.iv:
            self.append(token)
        item = self.iv.get(
            token, {})  # return empty dict when the token is not in database
        return item

    def append(self, token):
        print("accessing database")
        if len(self.q) > self.limit:
            key = self.q.popleft()
            self.iv.pop(key)
        postings = self.index_coll.find_one({"_id": token})
        if postings:  # only append when token is in database
            if self.is_field:
                cur_dict = self.iv.get(token, {})
                cur_dict["author"] = postings["author"]
                cur_dict["title"] = postings["title"]
                self.iv[token] = cur_dict
            else:
                self.iv[token] = postings["docIDs"]
            # logger.info("posting is {}".format(postings))
            print("access complete")
        else:
            logger.info("token {} returned none".format(token))

    def __getitem__(self, item):
        return self.get(item)


print("Server Starting, loading index")
iv_q = IndexQ(10000, iv, is_field=False)
field_q = IndexQ(10000, field, is_field=True)
print("finished loading index")


def get_data(books, q):
    """List of token -> List of JSON from MongoDB (Search Results)"""
    jsons = {}
    # print("taking:", object_ids)
    # count can jump when the query fails
    count = 0
    # TODO
    for data in books:
        try:
            print("Title: ", data["title"])
            # print("Paragraph number: ", data["paragraph_num"])
            # print("data", data)
            data["_id"] = str(data["_id"])
            # print("should print data", data)
            ## process content to be
            #data["content"] = output_using_pos(data["content"], q, iv_q, id)
            # if too long, dont run the function
            if len(data["content"]) > 500:
                c = []
            else:
                c = output_Frontend(data["content"], q[0], 100)
            data["content"] = c if c else data["content"][:500]
            # drop token
            data.pop("tokens")
            jsons[count] = data
            count += 1
        except KeyError:
            print("check object_ids:", id)
    return jsons


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/search/")
def search_item(query=None):
    print("using ordinary search")
    expanded_query, expanded_expression = expand_query(query)
    parsed_query = parse_query(expanded_query)
    logger.info("query is {}".format(parsed_query[1]))
    # return {"expand":expanded_query,
    #         "original":query}
    try:
        books = search_rank(collection, iv_q, field_q, n, parsed_query[0],
                            parsed_query[1])
        # logger.info(iv_q.iv)
        jsons = get_data(books, parsed_query[1])
        # logger.info("response is:", jsons)
        jsons["expand"] = expanded_expression
        jsons["original"] = query
    except Exception as e:
        print(e)
        return "None"

    #jsons = json.dumps(jsons)

    return jsons


@app.get("/solid_search/")
def solid_search_item(query=None):
    print("using solid search")
    parsed_query = parse_query(query)
    try:
        object_ids = search_rank(collection, iv_q, field_q, n, parsed_query[0],
                                 parsed_query[1])
        # logger.info("scores:", scores)
        jsons = get_data(object_ids, parsed_query[0])
        # logger.info("response is:", jsons)
    except Exception as e:
        print(e)
        return "None"
    #jsons = json.dumps(jsons)

    return jsons


@app.get("/book/")
def read_book(book_id=0, response_class=HTMLResponse):
    with open("html//book_" + str(book_id) + ".html", "r",
              encoding="utf-8") as f:
        html = f.read()
    return HTMLResponse(content=html, status_code=200)


@app.get("/random_author/")
def random_author():
    with open("author1000.txt", "r", encoding="utf-8") as f:
        s = f.read()
    authors = s.split("\n")
    authors = [a for a in authors if a]
    rand_author = random.choice(authors)
    url = "https://en.wikipedia.org/wiki/" + re.sub(" ", "_", rand_author)
    response = requests.get(url)
    if response.status_code == 200:
        print(url)
        return (rand_author, url)
    else:
        return (rand_author, "None")


# @app.get("/search/{method}")
# def read_item(method, query=None):
#     ########################################################
#     # implement the code for self.parse_query()
#     # parse the query string
#     parsed_query = parse_query(query)
#     try:
#         scores = TFIDFscore(iv_q, n, parsed_query)
#         # logger.info("scores:", scores)
#         object_ids = [s[0] for s in scores]
#         jsons = get_data(object_ids)
#         # logger.info("response is:", jsons)
#     except KeyError:
#         jsons = {0: []}  # no result

#         print(jsons)
#         jsons = json.dumps(jsons)

#     return jsons
