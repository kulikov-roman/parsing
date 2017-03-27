import requests
import json
url = 'https://www.flyniki.com/en/booking/flight/vacancy.php?'
DataGet = {}
DataGet['_ajax[templates][]'] = 'main', 'priceoverview', 'infos', 'flightinfo'
DataGet['_ajax[requestParams][departure]'] = 'Moscow - Domodedovo'
DataGet['_ajax[requestParams][destination]'] = 'Cologne/Bonn'
DataGet['_ajax[requestParams][returnDeparture]'] = ''
DataGet['_ajax[requestParams][returnDestination]'] = ''
DataGet['_ajax[requestParams][outboundDate]'] = '2017-05-07'
DataGet['_ajax[requestParams][returnDate]'] = '2017-05-14'
DataGet['_ajax[requestParams][adultCount]'] = '1'
DataGet['_ajax[requestParams][childCount]'] = '0'
DataGet['_ajax[requestParams][infantCount]'] = '0'
DataGet['_ajax[requestParams][openDateOverview]'] = ''
DataGet['_ajax[requestParams][oneway]'] = ''


headers={'User-Agent': 'Mozilla/5.0'}
Data = {}
Data['departure'] = 'DME'
Data['outboundDate'] = '2017-05-07'
Data['returnDate']='2017-05-14'
Data['oneway'] = '0'
Data['openDateOverview'] = '0'
Data['adultCount'] = '1'
Data['infantCount'] = '0'

session = requests.Session()
request = session.post(url, data=Data, verify=False, headers=headers)
request = session.post(request.url, data=DataGet, verify=False, headers=headers)
response = (request.json().get('templates').get('main'))
print (response)
