import requests
import json
from lxml import html
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

Outbount = tree.xpath('//div[@class = "vacancy_route"]/text()')

pricesClassic = tree.xpath('//span[7]/text()')
pricesClassic1 = tree.xpath('//span[21]/text()')
pricesClassic2 = tree.xpath('//span[35]/text()')
pricesClassic3 = tree.xpath('//span[49]/text()')
pricesClassic4 = tree.xpath('//span[63]/text()')

pricesFlex = tree.xpath('//span[9]/text()')
pricesFlex1= tree.xpath('//span[23]/text()')
pricesFlex2= tree.xpath('//span[37]/text()')
pricesFlex3= tree.xpath('//span[51]/text()')
pricesFlex4= tree.xpath('//span[65]/text()')

duration_of_journey = tree.xpath('//span[6]/text()')
duration_of_journey1 = tree.xpath('//span[20]/text()')
duration_of_journey2 = tree.xpath('//span[34]/text()')
duration_of_journey3 = tree.xpath('//span[48]/text()')
duration_of_journey4 = tree.xpath('//span[62]/text()')

start = tree.xpath('//time[1]/text()')
start1 = tree.xpath('//time[8]/text()')
start2 = tree.xpath('//time[15]/text()')
start3 = tree.xpath('//time[21]/text()')
start4 = tree.xpath('//time[27]/text()')

end = tree.xpath('//time[2]/text()')
end1 = tree.xpath('//time[9]/text()')
end2 = tree.xpath('//time[18]/text()')
end3 = tree.xpath('//time[24]/text()')
end4 = tree.xpath('//time[30]/text()')

print "Outbound Flight :" , Outbount[0]
print "Start/end :", (start[0]), "-", end[0], "     Duration of journey :", duration_of_journey[0], "       Economy Classic :", pricesClassic[0], "     Economy Flex:", pricesFlex[0]
print "Start/end :", (start1[0]), "-", end1[0], "     Duration of journey :", duration_of_journey1[0], "       Economy Classic :", pricesClassic1[0], "     Economy Flex:", pricesFlex1[0]
print "Start/end :", (start2[0]), "-", end2[0], "     Duration of journey :", duration_of_journey2[0], "       Economy Classic :", pricesClassic2[0], "     Economy Flex:", pricesFlex2[0]
print "Start/end :", (start3[0]), "-", end3[0], "     Duration of journey :", duration_of_journey3[0], "       Economy Classic :", pricesClassic3[0], "     Economy Flex:", pricesFlex3[0]
print "Start/end :", (start4[0]), "-", end4[0], "     Duration of journey :", duration_of_journey4[0], "       Economy Classic :", pricesClassic4[0], "     Economy Flex:", pricesFlex4[0]

