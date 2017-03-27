import requests
import json
from lxml import html
from array import array
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
tree = html.fromstring(response)

pricesClassic = tree.xpath('//span[7]/text()')
pricesFlex = tree.xpath('//span[9]/text()')
duration_of_journey = tree.xpath('//span[6]/text()')
duration_of_journey1 = tree.xpath('//span/text()')
start = tree.xpath('//time[1]/text()')
end = tree.xpath('//time[2]/text()')
#start1 = tree.xpath('//time[7]/text()')
#end1 = tree.xpath('//time[8]/text()')

print "Start/end :", (start[0]), "-", (end[0]), "     Duration of journey :", (duration_of_journey[0]), "       Economy Classic :", (pricesClassic[0]), "     Economy Flex:", (pricesFlex[0])
#print "Start/end :", (start1[0]), "-", (end1[0]), "     Duration of journey :", ([0])
