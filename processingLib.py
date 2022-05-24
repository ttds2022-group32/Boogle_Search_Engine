from nltk.stem import PorterStemmer


#%%
##### functions for text pre-processing #####
def tokeniser(context, islower=True):
    '''Split on every non-letter characters. Returns a list of tokens'''

    non_letter_list = "!\"#$%″&′'’‘()*…+, —-./:;<=>?@[\]^_`{|}~0123456789“”"
    # change all the occurances of non letter characters into space and upper case letter into lower case letter
    # split the whole paragraph into a lists of words by using space as separator
    non_letter_table = context.maketrans(non_letter_list,
                                         ' ' * len(non_letter_list))
    if islower:
        return context.translate(non_letter_table).lower().split()
    else:
        return context.translate(non_letter_table).split()


def stopword_remover(word_list):
    '''Remove all the occurances of stopword from the word list. Return a list of words.'''

    # read stop word list
    f = open("englishST.txt", "r")
    stopWord = [w.strip() for w in f.readlines()]
    f.close

    return [i for i in word_list if i not in stopWord]


def porter_stemmer(word_list):
    '''Stem the words in the word list by using Porter Stemmer. Return a list of stemmed words.'''

    porter = PorterStemmer()

    return [porter.stem(i) for i in word_list]


def output_Frontend(content, word, words_num=50, isExact=False):
    """[[pos,string]]"""
    w_list = content.split()

    # preprocess word list for index searching
    preproc_w_list = tokeniser(content)
    if not isExact:
        word = PorterStemmer().stem(word)
        preproc_w_list = porter_stemmer(tokeniser(content))

    # find all the occurances of word in preprocessed word list
    w_idx = []
    for index, w in enumerate(preproc_w_list):
        if w == word:
            w_idx.append(index)
            if len(w_idx) == 10:
                break
    lo_up_list = []
    for i in w_idx:
        lower = 0 if (i - words_num) < 0 else i - words_num
        upper = len(w_list) if (i + words_num) > len(w_list) else i + words_num
        sentence = " ".join(w_list[lower:upper + 1])
        lo_up_list.append([(lower, upper), sentence])

    return "...".join(l[1] for l in lo_up_list)


def output_using_pos(content, tokens, index, docID, words_num=50):
    contents = []
    for token in tokens:
        if index.get(token):
            postings = index.get(token)["docIDs"]
            # first position
            if docID in postings:
                pos = postings[docID][0]
                contents.append(content[pos:pos + words_num])
    return "...".join(contents)