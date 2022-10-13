import httpx
from bs4 import BeautifulSoup
import asyncio

def clean_req(name):
	name=name.lower().replace(' ','-')
	return name

def clean_name(name):
	return name.replace('  ','').replace('\n','')

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
