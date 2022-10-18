import httpx
from bs4 import BeautifulSoup
import re
from random import randrange
import json

#func to generate random browser user-agent
def user_agent():
	with httpx.Client() as client:
		i=client.get('https://seolik.ru/user-agents-list')
		soup=BeautifulSoup(i.content, 'html.parser')
		ua= [u.get_text() for u in soup.find_all('td',string=re.compile("Mozilla"),limit=3)]
		return ua[randrange(3)].replace('\n','')
