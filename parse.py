import argparse
import sys
import lxml
import requests
import lxml.html
import datetime
import re


# 13.04.2017


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
    date = datetime.datetime.now()
    current_date = date.strftime('%Y-%m-%d')
    # comment magic number
    limit_date = date + datetime.timedelta(days=360)
    limit_date = limit_date.strftime('%Y-%m-%d')
    if not namespace.departure.isalpha() or len(namespace.departure) != 3:
        print ("The input is not correct. Example, DME")
        sys.exit()
    elif not namespace.destination.isalpha() or len(namespace.destination) != 3:
        print ("The input is not correct. Example, CGN")
        sys.exit()
    elif namespace.outboundDate.strftime('%Y-%m-%d') < current_date:
        print ("The input is not correct.")
        sys.exit()
    elif namespace.outboundDate.strftime('%Y-%m-%d') > limit_date:
        print ("The input is not correct.")
        sys.exit()
    else:
        print ("The input is correct.")


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

    # currency = html.xpath('//th[@class="faregrouptoggle ECO style-eco-comf"]/text()')
    # quotes_list = []
    for n, flight in enumerate(outbound_flights):
        price_eco = flight.xpath('./td[contains(@headers, "ECO_COMF")]/label/div[@class="lowest"]/span/text()')
        price_flex = flight.xpath('./td[contains(@headers, "ECO_PREM")]/label/div[@class="lowest"]/span/text()')
        price_business = flight.xpath('./td[contains(@headers, "BUS_FLEX")]/label/div[@class="lowest"]/span/text()')
        print price_eco, price_flex, price_business
        details_flight = flight.xpath('./../tr[@id="flightDetailsFi_{}"]/td/table/tbody'.format(n))[0]
        for details in details_flight:
            time_departure = details.xpath('./td/span/time/text()')
            flight_numbers = details.xpath('./td[@class="table-text-center"]/text()')
            city_departure = details.xpath('./td/span/text()')
            code_city = []
            flight_number = []
            for city in city_departure:
                code = re.findall(r'[A-Z]{3}', city)
                if code:
                    code_city.append(code)
            for number in flight_numbers:
                if number != " ":
                    flight_number.append(number)
            print time_departure, code_city, flight_number


"""
    for flight in outbound_flights:
        start_end = flight.xpath('./td/span/time/text()')
        duration = flight.xpath('./td[@class="table-text-left"]/span/text()')
        prices = flight.xpath('./td[@role="radio"]/label/div[@class="lowest"]/span/text()')
        prices1 = flight.xpath('//tbody/tr/td/span[@class="notbookable"]/text()')
        transplant = flight.xpath('//tbody/tr/td/span/text()')
        number_flight = flight.xpath('//table[@role="presentation"]/tbody/tr/td[@class="table-text-center"]/text()')

        quote = {"departure": start_end[0],
                 "arrival": start_end[1],
                 "segments:{segment_1:{} ,
                            segment_2:{}}
                 "duration of journey": duration[3],
                 "currency": currency,
                 "price": {"price_eco": [],
                           "price_flex": [],
                           "price_business": []},
                 }
"""

if __name__ == '__main__':
    scrape()
