from autocorrect import Speller


class Recommend:
    def __init__(self):
        with open("author1000.txt", "r") as f:
            author = f.read()
            names = author.split("\n")
        f.close()

        self.name_dic = {
        }  # key: first name / title, value: list of list of string of (middle) last name
        for n in names:
            list = n.split(" ")
            if list[0] not in self.name_dic:
                if len(list) > 1:
                    self.name_dic[list[0]] = [list[1:]]
                else:
                    self.name_dic[list[0]] = []
            else:
                copy = self.name_dic[list[0]]
                if len(list) > 1:
                    copy.append(list[1:])
                    self.name_dic[list[0]] = copy

    # input is a word and return a list of author names that have the word as title or first name
    def author(self, word):
        re = []
        w = word.capitalize()
        if w in self.name_dic:
            names = self.name_dic[w]
        for n in names:
            name = w + " " + " ".join(n)
            re.append(name)
        return re


def expand_query(query):
    is_sent = len(query.split(" ")) > 1
    r = Recommend()
    spell = Speller(lang='en')
    if not is_sent:
        try:
            expanded_query = r.author(query)[0]
        except:
            expanded_query = spell(query)
        return expanded_query, expanded_query
    else:
        s = []
        expanded_queries = []
        for word in query.split(" "):
            try:
                expanded_q = r.author(word)[0]
                expanded_queries.append(expanded_q)
            except:
                expanded_q = spell(word)
                expanded_queries.append(expanded_q)
            if expanded_q != word:
                s.append("*" + expanded_q + "*")
            else:
                s.append(expanded_q)
        return " ".join(expanded_queries), " ".join(s)


def expand_query_test(query):
    return query + "<b>_Yeah!!!!!!!!!</b>"
