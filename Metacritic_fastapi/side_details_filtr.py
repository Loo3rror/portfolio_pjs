import httpx
from bs4 import BeautifulSoup
import asyncio

#clean possible spaces in game search
def clean_req(name):
	name=name.lower().replace(' ','-')
	return name

#clean names from BeautifulSoup find
def clean_name(name):
	return name.replace('  ','').replace('\n','')

#dict of BeautifulSoup funct search, depending on key
def filtr_data(data,body):
	if data!=None:
		b={#add this list as seperate file
		'metascore':lambda data:float(data.text)/10,
		'userscore':lambda data:float(data.find('a').find('div').text),
		'developer':lambda data:data.find('a','button').text,
		'rating':lambda data:data.find('span','data').text,
		'genre':lambda data:[d.get_text() for d in data.find_all('span','data')],
		'platforms':lambda data:[d.get_text() for d in data.find_all('a','hover_none')]
	}
		return {body:b[body](data)}
	return None
