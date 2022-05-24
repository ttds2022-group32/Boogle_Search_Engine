# %%
import pymongo

# get data from database by attribute and ID
def gotcontent(uniqID, attribute):
    client = pymongo.MongoClient("localhost", 27017)
    db = client.gutenburg
    collection = db.books
    output = collection.find_one({"_id":uniqID})[attribute]
    return output

# %%
## connect to the database
client = pymongo.MongoClient("localhost", 27017)

db = client.gutenburg
collection = db.books

# %%

## get the list of invert position list 
tokenlist = []
for terms in collection.find():
    tokens = terms["tokens"]
    id = terms["_id"]
    for i in range(len(tokens)):
        token_pos = [tokens[i], id, int(i+1)]
        tokenlist.append(token_pos)
client.close()

# sort the invert position list by first column to third
tokenlist.sort()
print(tokenlist[:5])

# %%

# now convert into dictionary
## {"token": {"df": int, "doc":{docId: [pos]}}}
pilist = {}

for token in tokenlist:
    token_term = token[0]
    token_docId = token[1]
    token_pos = token[2]
    # check the term is in dictionary
    if token_term in pilist:
        # check the doc is in dictionary
        if token_docId in pilist[token_term]["doc"]:
            pilist[token_term]["doc"][token_docId].append(token_pos)
        # if not, add df and the docId:pos
        else:
            pilist[token_term]["df"] += 1
            pilist[token_term]["doc"][token_docId] = [token_pos]
    # if not, add the token dictionary {"df": df, "doc":{docId: [pos]}}
    else:
        pilist[token_term] = {"df": int(1), "doc" : {token_docId : [token_pos]}}


# %%
# write the index.txt
filewriter = open("index.txt", "w", encoding="utf-8")
for key in pilist: 
    line = key + ":" + str(pilist[key]["df"]) + "\n"
    filewriter.write(line)
    for key2 in pilist[key]["doc"]:
        poslist = [str(x) for x in pilist[key]["doc"][key2]]
        pos = ",".join(poslist)
        line = "\t" + str(key2) + ": " + pos + "\n"
        filewriter.write(line)
filewriter.close()




