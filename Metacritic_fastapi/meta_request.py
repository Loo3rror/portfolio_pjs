import httpx
import json
from bs4 import BeautifulSoup
import asyncio
from fastapi import FastAPI, HTTPException
from side_details_filtr import filtr_data,clean_name,clean_req
from new_user_agent import user_agent


meta_app=FastAPI()

#hello
@meta_app.get('/')
async def root():
	j={'welcome':'Welcome to the metacritic api',
	'help':'Please, research /docs file for your questions'}
	return j

#awailable platforms list
@meta_app.get('/platforms')
async def ret_platforms():
	p={'platforms':['pc',
	'playstation-5','playstation-4','playstation-3','playstation-vita',
	'xbox-360','xbox-one',
	'switch','wii-u','3ds',
	'ios']}
	return p

#search game and return its data in json (with console/platform as possible argument)
@meta_app.get('/games/{game}')
async def get_game_json(game,console='pc'):
	async with httpx.AsyncClient(headers={'User-Agent':user_agent()},params=None) as client:
			test=await client.get(f'https://www.metacritic.com/game/{console}/{clean_req(game)}')
			if test.status_code==404:
			 	raise HTTPException(status_code=404, detail=f"Game not found in {console} libary, be more specific with title or try anoter platform")
			soup = BeautifulSoup(test.content, 'html.parser')
			j={
			'publisher':clean_name(soup.find('li',"summary_detail publisher").find('a').text),
			'developer':filtr_data(soup.find('li','summary_detail developer'),'developer'),
			'metascore':filtr_data(soup.find('div',"score_summary metascore_summary").find('span',itemprop='ratingValue'),'metascore'),
			'userscore':filtr_data(soup.find('div','userscore_wrap feature_userscore'),'userscore'),
			'genre':filtr_data(soup.find('li','summary_detail product_genre'),'genre'),
			'rating':filtr_data(soup.find('li','summary_detail product_rating'),'rating'),
			'platforms':{'search was for':console, 'also awailable for':filtr_data(soup.find('li','summary_detail product_platforms'),'platforms')}
			}
			return j
