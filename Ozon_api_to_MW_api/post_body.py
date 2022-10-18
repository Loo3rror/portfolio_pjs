#function returning formatted body for post
def body_info(search_time=None):
	PB={
	#0 shipments in a search_time
	'day_ship':{"dir": "ASC", 
					'filter':{
					'cutoff_from':f'{search_time}T00:00:00.000Z',
					'cutoff_to':f'{search_time}T19:00:00.000Z'
					},
					'limit':300
				},
	#returns in search_time
	'day_returns':{
					'filter':{
					'delivering_date_from':f'{search_time}T00:00:00.000Z'
					},
					'limit':100
				}}
	return PB
