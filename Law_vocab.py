import requests
import string
from bs4 import BeautifulSoup

keywords = open("Law_Vocabulary.txt","w+")
url = "https://thelawdictionary.org/letter/{}/page/{}"
letters = string.ascii_lowercase
for char in letters:
    num = 1
    while(1):
        print("Letter : {}\tPage : {}".format(char,num))
        response = requests.get(url.format(char,num))
        soup = BeautifulSoup(response.text,"html.parser")
        temp = soup.find_all("a",{"rel":"bookmark"})
        try:
            for i in temp:
                keywords.write(i.text+"\n")
        except:
            break
        num=num+1

keywords.close()