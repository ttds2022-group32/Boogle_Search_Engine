# %%
import pymongo
from processingLib import *

##### function for creating a ivlsit and field list #####


def generate_ivlist_flist(collection):
    '''return token_dict: {token: {docId: [pos]}}'''
    '''field_dict {token:{docId: ["content","author","title"]}'''
    token_dict = {}
    field_dict = {}

    # Loop through all the documents in the collection
    for i in collection.find():

        id = i["_id"]
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


    return token_dict, field_dict

# %%

## score function for different method
## now finished tfidf 
# TODO other score function and final ranking fucntion
def rankscore():

    return 0



# %%
## connect to the database
client = pymongo.MongoClient("localhost", 27017)

db = client.gutenburg
collection = db.books

pvlist, flist = generate_ivlist_flist(collection)

client.close()


# %%
