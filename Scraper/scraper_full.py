import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient
import logging

URL_TMP = "https://www.gutenberg.org/ebooks/NUM"
BOOK_URL_TMP = "https://www.gutenberg.org/files/NUM/NUM-h/NUM-h.htm"

# setting MongoDB
client = MongoClient('localhost', 27017)
db = client.books
collection = db.book_paragraph

if __name__ == "__main__":
    import sys
    urls_list_file = sys.argv[1]
    
    # logging
    logging.basicConfig(level=logging.INFO, filename="scrape_full.log")

    # read urls list for scraping
    with open(urls_list_file, "r", encoding="utf-8") as f:
        urls_list = f.read()
    urls_list = urls_list.split("\n")
    
    # book loop
    for urls in urls_list:
        book_id, url, book_url  = urls.split(",")

        # scrape for book page
        html = requests.get(book_url)
        
        # UnicodeDecodeError
        try:
            source = html.content.decode("utf-8")
            txt_soup = BeautifulSoup(source, "html.parser")
        except:
            #print("UnicodeDecodeError")
            continue
        
        # 404 page not found
        if "<title>404 | Project Gutenberg</title>" in source:
            continue
        
        # scrape for cover page
        image_html = requests.get(url)
        image_source = image_html.content.decode("utf-8")
        image_soup = BeautifulSoup(image_source, "html.parser")

        # save html file
        path = "root_html/cover_"+str(book_id)+".html"
        with open(path, "w", encoding="utf-8") as f:
            f.write(image_source)
        
        path = "book_html/book_"+str(book_id)+".html"
        with open(path, "w", encoding="utf-8") as f:
            f.write(source)


        ###########################################################################################################################
        
        # prepare JSON
        jsondict = {}
        jsondict["book_id"] = int(book_id)

        # get cover image
        image_url_tag = image_soup.find_all("img",class_="cover-art")
        image_url = image_url_tag[0]["src"] if image_url_tag else "NOT_EXIST"
        jsondict["image_src"] = image_url

        # get title
        title = image_soup.find_all("td",itemprop="headline")[0].text
        jsondict["title"] = title

        # get author_info
        author_info = image_soup.find_all("a",itemprop="creator")
        if author_info:
            author_info = author_info[0]
            author = author_info.text
            author_url = author_info["href"]
        else:
            author = "UNKNOWN"
            author_url = "UNKNOWN"
        jsondict["author"] = author
        jsondict["author_url"] = author_url

        # get year of publication
        year = image_soup.find_all("tr",property="dcterms:issued")
        year = year[0]["content"] if year else "UNKNOWN"
        jsondict["year"] = year

        # get language
        lang = image_soup.find_all("tr",property="dcterms:language")
        lang = lang[0]["content"] if lang else "UNKNOWN"
        jsondict["language"] = lang

        # get subjects
        subjects = image_soup.find_all("td",property="dcterms:subject")
        subjects = ",".join([subject.text for subject in subjects]) if subjects else "UNKNOWN"
        jsondict["subjects"] = subjects


        # scrapr book pages
        paragraphs = txt_soup.find_all("p",class_=None)
        # remove paragraph with <15 to remove paragraph like "Chapter1"
        paragraphs = [p for p in paragraphs if len(p.text)>15]

        # paragraph loop
        for i,paragraph in enumerate(paragraphs):
            #print(paragraph.text)
            #print(len(paragraph.text))
            jsondict["paragraph_num"] = i+1
            jsondict["content"] = paragraph.text

            #logging.info("  Book_ID: "+str(jsondict["book_id"])+" Paragraph: "+str(jsondict["paragraph_num"]))
            collection.insert_one(jsondict.copy())

        #############################################################################################################################
        logging.info(urls)
    
