import argparse
import sys
import lxml
import requests
import lxml.html
import datetime


def scrape():
    parser = create_parser()
    namespace = parser.parse_args()
    validation(namespace)
    responce = get_res(namespace)
    parse_responce(responce)


def create_parser():
    parse = argparse.ArgumentParser()
    parse.add_argument('departure')
    parse.add_argument('destination')
    parse.add_argument('outboundDate', type=lambda s: datetime.datetime.strptime(s, '%Y-%m-%d'))
    parse.add_argument('returnDate', nargs='?', default='')
    return parse


def validation(namespace):
    if not namespace.departure.isalpha() or len(namespace.departure) != 3:
        print ("The input is not correct. Example, DME")
        sys.exit()
    elif not namespace.destination.isalpha() or len(namespace.destination) != 3:
        print ("The input is not correct. Example, CGN")
        sys.exit()
    else:
        print (namespace.departure, namespace.destination, namespace.outboundDate, namespace.returnDate)
        print ("The data is entered correctly")


def get_res(namespace):
    url = 'https://www.flyniki.com/en/booking/flight/vacancy.php'
    data_res = {'_ajax[templates][]': ('main', 'priceoverview', 'infos', 'flightinfo'),
                '_ajax[requestParams][departure]': namespace.departure.upper(),
                '_ajax[requestParams][destination]': namespace.destination.upper(),
                '_ajax[requestParams][outboundDate]': namespace.outboundDate.strftime('%Y-%m-%d'),
                '_ajax[requestParams][returnDate]': namespace.returnDate,
                '_ajax[requestParams][oneway]': ''}
    data_req = {'departure': namespace.departure.upper(),
                'outboundDate': namespace.outboundDate.strftime('%Y-%m-%d'),
                'returnDate': namespace.returnDate,
                'oneway': '',
                'adultCount': '1'}
    print data_req['outboundDate']
    if not namespace.returnDate:
        data_req['returnDate'] = namespace.outboundDate.strftime('%Y-%m-%d')
        data_req['oneway'] = 'on'
        data_res['_ajax[requestParams][returnDate]'] = namespace.outboundDate.strftime('%Y-%m-%d')
        data_res['_ajax[requestParams][oneway]'] = 'on'
    ses = requests.Session()
    ses_req = ses.post(url, data=data_req, verify=False)
    ses_res = ses.post(ses_req.url, data=data_res, verify=False)
    res = (ses_res.json().get('templates').get('main'))
    return res


def parse_responce(responce):
    html = lxml.html.fromstring(responce)
    outbound_flights = html.xpath('//tbody[@role="radiogroup"]/tr[contains(@class, "flightrow")]')
    quotes_list = []
    for flight in outbound_flights:
        start_end = flight.xpath('./td/span/time/text()')
        duration = flight.xpath('./td[@class="table-text-left"]/span/text()')
        prices = flight.xpath('./td[@role="radio"]/label/div[@class="lowest"]/span/text()')
        sdfsdf = flight.xpath('//tbody/tr/td/span/text()')
        number_flight = flight.xpath('//table[@role="presentation"]/tbody/tr/td[@class="table-text-center"]/text()')
        currency = html.xpath('//th[@class="faregrouptoggle ECO style-eco-comf"]/text()')
        print prices
        print duration[3]
        print start_end
        print sdfsdf[6]
        print number_flight[0], number_flight[3]
        quote = {"departure": start_end[0],
                 "arrival": start_end[1],
                 "duration of journey": duration[3],
                 "currency": currency,
                 "price": {"price_eco": [],
                           "price_flex": [],
                           "price_business": []},
                 }
        quote["price"]["price_eco"].append(float(prices[0]))
        quote["price"]["price_flex"].append(float(prices[1]))
        if len(prices) == 3:
            quote["price"]["price_business"].append(float(prices[2]))
        print quote
        quotes_list.append(quote)
    print quotes_list


if __name__ == '__main__':
    scrape()
