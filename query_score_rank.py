from processingLib import porter_stemmer, stopword_remover, tokeniser
import math
from bson.objectid import ObjectId


def tfidf(n, tf, df):
    '''Returns the weight of term by using tf and IDF'''
    w = (1 + math.log10(tf)) * math.log10(n / df)
    return w


def tf(inverted_index, t, d):
    '''Returns the number of times term t appeared in document d'''
    tf = len(inverted_index.get(t)[d])
    return tf


def df(inverted_index, t):
    '''Returns the number of documents term t appeared in'''
    return len(inverted_index.get(t))


# return two query tokens, one is only tokenized and one is full preprocessed
def parse_query(query):
    """tokenize query string"""
    return (tokeniser(query, islower=False),
            porter_stemmer(stopword_remover(tokeniser(query))))


# TFIDF
def TFIDFscore(collection, inverted_index, n, q):
    '''
    q: query in [String]
    Ranked IR based on TFIDF. Returns a list of tuples (document ID,score) sorted by the score from largest score to smallest score
    '''
    score_dict = {}
    # loop through  f
    for t in q:
        # for each token, loop through all the documents contained the token
        for d in inverted_index[t].keys():
            if d in score_dict:
                score_dict[d].append(
                    tfidf(n, tf(inverted_index, t, d), df(inverted_index, t)))
            else:
                score_dict[d] = [
                    tfidf(n, tf(inverted_index, t, d), df(inverted_index, t))
                ]

    # for each document, sum over the weights of terms
    for d in score_dict.keys():
        score_dict[d] = round(sum(score_dict[d]), 4)

    # penalize if the token list is too long
    output = []
    for score in score_dict.items():
        data = collection.find({"_id": ObjectId(score[0])})[0]
        tokens = data["tokens"]
        if len(tokens) > 50:
            output.append((data, score[1] / 20))
        else:
            output.append((data, score[1]))

    # sort a list of tuples (document ID,score) by the score from largest score to smallest score
    return sorted(output, key=lambda x: x[1], reverse=True)


def phrase_search(collection, inverted_index, q):
    """
    q: list of tokens
    return a list of tuples (document,score)
    """
    print("running phrase search")

    def _positional_intersect(
            terms, k, distance_func=lambda pos1, pos2: abs(pos2 - pos1)):
        postings = [inverted_index[term] for term in terms]
        valid_set = set(postings[0].keys()).intersection(
            *[set(p.keys()) for p in postings])
        print("valid_set is ", len(valid_set))
        answer = set()
        for i, docId in enumerate(valid_set):
            if i + 1 < len(postings):
                l1, l2 = postings[i][docId], postings[i + 1][docId]
                # print(docID, l1, l2)
                for pos1 in l1:
                    if list(
                            filter(lambda x: 0 <= x <= k,
                                   [distance_func(pos1, pos2)
                                    for pos2 in l2])):
                        answer.add(docId)  # big number to rank first
        return answer

    return [(collection.find({"_id": ObjectId(docID)})[0], 50)
            for docID in _positional_intersect(q, 5)]


def search_rank(collection, inverted_index, field_list, n, q_t, q):
    # check the query contains any token in corpus
    flags = False
    for t in q:
        if field_list.get(t):
            flags = True

    if flags:
        # tfids
        tFIDF_lists = TFIDFscore(collection, inverted_index, n, q)[:20]
        # title field search - higher priority
        title_lists = fieldsearch(collection, field_list, q, "title")
        # author field search
        author_lists = fieldsearch(collection, field_list, q_t, "author")

        phrase_lists = phrase_search(collection, inverted_index, q)

        finallist = phrase_lists + tFIDF_lists + title_lists + author_lists
        print([(doc["_id"], score) for doc, score in finallist])

        return list(
            t[0] for t in sorted(finallist, key=lambda x: x[1], reverse=True))

    else:
        raise KeyError


def fieldsearch(collection, field_list, q, field):
    print("doing field search", field, "q: ", q)
    q_len = len(q)
    score = 50 / q_len / q_len

    score_dict = {}
    sets = []
    for t in q:
        # if token in field list
        if field_list.get(t):
            sets.append(set(field_list[t][field]))
    ## all intersections + intersetion of chunks + single if not enough
    res = [(docID, score * len(sets)) for docID in sets[0].intersection(*sets)]
    if len(res) <= 10:
        for i, docID in enumerate(intersection_in_chunks(sets, 2)):
            if i < 5:
                res.append((docID, score * 2))

    # remove dup
    output = []
    book_ids = set()
    for score in res:
        data = collection.find({"_id": ObjectId(score[0])})[0]
        book_id = data["book_id"]
        if book_id in book_ids:
            pass
        else:
            book_ids.add(book_id)
            output.append((data, score[1]))
    return output


def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


def intersection_in_chunks(lst, n):
    """
    
    """
    res = []
    for setlst in chunks(lst, n):
        res += list(setlst[0].intersection(*setlst))
    return res
