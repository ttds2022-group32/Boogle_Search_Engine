import requests
from bs4 import BeautifulSoup
import re

URL_TMP = "https://www.gutenberg.org/ebooks/NUM"
BOOK_URL_TMP = "https://www.gutenberg.org/files/NUM/NUM-h/NUM-h.htm"
LIMIT = 67321

def is_fiction(subjects):
    return any(["fiction" in subject.text.lower() for subject in subjects])

def is_english(lang):
    lang = lang[0]["content"] if lang else "UNKNOWN"
    return True if lang=="en" else False

if __name__ == "__main__":
    import sys
    output = sys.argv[1]
    urls = []
    for i in range(LIMIT):
        url = re.sub(r"NUM", str(i+1), URL_TMP)
        book_url = re.sub(r"NUM",str(i+1),BOOK_URL_TMP)
        html = requests.get(url)
        source = html.content.decode("utf-8")
        soup = BeautifulSoup(source, "html.parser")
        
        subjects = soup.find_all("td",property="dcterms:subject")
        lang = soup.find_all("tr",property="dcterms:language")

        if is_fiction(subjects) and is_english(lang):
            print(url)
            s = str(i+1)+","+url+","+book_url+"\n"
            urls.append(s)
    
    with open(output,"w",encoding="utf-8") as f:
        f.writelines(urls)

        

