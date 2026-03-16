import requests
from bs4 import BeautifulSoup

def google_search(query):

    url=f"https://www.google.com/search?q={query}"

    headers={
        "User-Agent":"Mozilla/5.0"
    }

    r=requests.get(url,headers=headers)

    soup=BeautifulSoup(r.text,"html.parser")

    results=[]

    for g in soup.select(".BNeawe")[:5]:

        results.append(g.text)

    return "\n".join(results)