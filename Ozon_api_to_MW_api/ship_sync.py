import json
from requests.auth import HTTPBasicAuth
import httpx
import asyncio
from post_body import body_info

class Ozon_req():
	"""collecting and returning shipment data;
	currently allows to get list of products shipped in a day; 
	combine with post_body.py, containing jsonbody"""
	def __init__(self,org,now_time):#time now_time - [str YYYY-MM-DD]
		self.apiid=org['id']
		self.apikey=org['key']
		self.now_time=now_time

	#get shipment data form seller
	async def post_list(self,client,t):
			ozon_get=await client.post('https://api-seller.ozon.ru/v3/posting/fbs/unfulfilled/list',
				json=body_info(search_time=t)['day_ship'])
			#seller api is up to update, if legacy func return error, change post body and url to 'https://api-seller.ozon.ru/v3/posting/fbs/list'
			ozon_info=ozon_get.content
			check=json.loads(ozon_info)
			check=check["result"]
			m=client.headers["client-id"]
			return check

	#check, if product successfully on the way
	async def data_filtr(self,data):
			if data["status"]=="delivering": 
						books=[]
						for book in data["products"]:
							i=book["offer_id"],book["quantity"]
							books.append(i)
						valued_data=(data["posting_number"],books)
						return valued_data

	#main request to seller
	async def get_list_current(self):
		Headers={'Client-Id':self.apiid,'Api-Key':self.apikey}
		async with httpx.AsyncClient(headers=Headers) as client:
				orders=await asyncio.gather(*[self.post_list(client,t) for t in self.now_time])
				shiping_data=[]
				for order in orders:
					if order['postings']!=[]:#filter t with no shipments
						trail=asyncio.gather(*[self.data_filtr(data) for data in order['postings']])
						shiping_data.append(trail)
				fin_info=await asyncio.gather(*shiping_data)
				return fin_info


class MWapi_shipment():
	"""
	connects to MoySklad; 
	compile_shipment(data) creates new shipment with products in data
	"""
	def __init__(self,org):
		self.war_login=org['war_login']
		self.war_pass=org['war_pass']
		self.org_id=org['org_id']
		self.wareh_id=org['wareh_id']

	#get product data from DB api
	async def get_product_data(self,client,product):
					link=await 	client.get(f"https://online.moysklad.ru/api/remap/1.2/entity/product?search={product[0]}")
					r=json.loads(link.content)
					try:
						x=r['rows'][0]['meta']
					except IndexError:# if product id not in database
						with open(f'id {product[0]}error.log','w') as f:
							f.write(str(r))
					else:
						y={
						"quantity":product[1],
						"assortment":{
						'meta':
						{"href":x['href'],
						"type":"product",
						"mediaType":"application/json"}}}
						return y

	#connect product info with warehous shipment body dict
	async def create_shipment_json(self,client,shipment,org_id,wareh_id):
		#body of demand position
		j={
			'name':shipment[0],
			#client organization info
				"organization" : {
				"meta" : {
				"href" : f"https://online.moysklad.ru/api/remap/1.2/entity/organization/{org_id}",
				"metadataHref" : "https://online.moysklad.ru/api/remap/1.2/entity/organization/metadata",
				"type" : "organization",
				"mediaType" : "application/json",
				"uuidHref" : f"https://online.moysklad.ru/app/#mycompany/edit?id={org_id}"
				}},
			#seller info (static in this build)
				"agent" : {
				"meta" : {
				"href" : "https://online.moysklad.ru/api/remap/1.2/entity/counterparty/12a4fabd-89b4-11ec-0a80-05d400103362",
				"metadataHref" : "https://online.moysklad.ru/api/remap/1.2/entity/counterparty/metadata",
				"type" : "counterparty",
				"mediaType" : "application/json",
				"uuidHref" : "https://online.moysklad.ru/app/#company/edit?id=12a4fabd-89b4-11ec-0a80-05d400103362"
					}
					},
			#warehouse info
				"store" : {
				"meta" : {
				"href" : f"https://online.moysklad.ru/api/remap/1.2/entity/store/{wareh_id}",
				"metadataHref" : "https://online.moysklad.ru/api/remap/1.2/entity/store/metadata",
				"type" : "store",
				"mediaType" : "application/json",
				"uuidHref" : f"https://online.moysklad.ru/app/#warehouse/edit?id={wareh_id}"
				}
				}
		}
		pj=await asyncio.gather(*[self.get_product_data(client,product) for product in shipment[1]])
		i=(j,pj)
		return i

	#append product to warehouse shipment
	async def post_position(self,client,product,demand_link):
		p=await client.post(f'{demand_link}/positions',data=json.dumps(product))
		return p

	#create warehouse shipment
	async def post_demand(self,client,shipment):
			s=await client.post("https://online.moysklad.ru/api/remap/1.2/entity/demand",data=json.dumps(shipment[0]))
			ship_id=json.loads(s.content)
			i=ship_id['meta']
			link=i['href']
			end_task = await asyncio.gather(*[self.post_position(client,product,link) for product in shipment[1]])

	#main request to warehouse api
	async def compile_shipment(self,data):
		Auth=HTTPBasicAuth(self.war_login,self.war_pass)
		Headers={'Content-Type': 'application/json'}
		#warehouse api is up to update, takes only 5 connections by user simultaneously
		limits = httpx.Limits(max_connections=5, max_keepalive_connections=0)
		async with httpx.AsyncClient(auth=Auth,headers=Headers,limits=limits) as client:
			all_s=[]
			for shipments in data:
				all_s.append(asyncio.gather(*[self.create_shipment_json(client,shipment,self.org_id,self.wareh_id) for shipment in shipments]))
			all_s = await asyncio.gather(*all_s)
			for shipments in all_s:
				end_task=await asyncio.gather(*[self.post_demand(client,shipment) for shipment in shipments])


#~~~~~~~~~~~~~~~~~function to sync seller shipments to warehouse demand in set time
async def main(Clients,days):
		for org in Clients:
			data_get=await asyncio.gather(Ozon_req(org,days).get_list_current())
			for data in data_get:
				await asyncio.gather(MWapi_shipment(org).compile_shipment(data))
		
#~~~sample usage
#if __name__ == '__main__':
#	Clients1=json.load(open('Clients.json'))
#	days=[]
#	for i in range (17,30):
#		i=f'2022-10-{i}'
#		days.append(i)
#	asyncio.run(main(Clients1,days))