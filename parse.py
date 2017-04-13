from argparse import ArgumentParser
import sys

import texttable
import lxml.html

from datetime import datetime, timedelta
import requests


def scrape():
    parser = create_parser()
    namespace = parser.parse_args()
    validation(namespace)
    response = get_res(namespace)
    parse_responce(response)


def create_parser():
    parse = ArgumentParser()
    parse.add_argument('departure')
    parse.add_argument('destination')
    parse.add_argument('outboundDate', type=lambda s: datetime.strptime(s, '%Y-%m-%d'))
    parse.add_argument('returnDate', nargs='?', default='')
    return parse


def validation(namespace):
    date = datetime.now()
    current_date = date.strftime('%Y-%m-%d')
    # the maximum date that can be selected is limited to 365 days from the current date
    limit_date = date + timedelta(days=365)
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
    data_get_response = {'_ajax[templates][]': ('main',
                                                'priceoverview',
                                                'infos',
                                                'flightinfo'),
                         '_ajax[requestParams][departure]': namespace.departure.upper(),
                         '_ajax[requestParams][destination]': namespace.destination.upper(),
                         '_ajax[requestParams][outboundDate]': namespace.outboundDate.strftime('%Y-%m-%d'),
                         '_ajax[requestParams][returnDate]': namespace.returnDate,
                         '_ajax[requestParams][oneway]': ''}
    data_request = {'departure': namespace.departure.upper(),
                    'outboundDate': namespace.outboundDate.strftime('%Y-%m-%d'),
                    'returnDate': namespace.returnDate,
                    'oneway': '',
                    'adultCount': '1'}
    print data_request['outboundDate']
    if not namespace.returnDate:
        data_request['returnDate'] = namespace.outboundDate.strftime('%Y-%m-%d')
        data_request['oneway'] = 'on'
        data_get_response['_ajax[requestParams][returnDate]'] = namespace.outboundDate.strftime('%Y-%m-%d')
        data_get_response['_ajax[requestParams][oneway]'] = 'on'
    session = requests.Session()
    session_request = session.post(url, data=data_request, verify=False)
    get_response = session.post(session_request.url, data=data_get_response, verify=False)
    response = (get_response.json())
    if 'templates' in response:
        return response.get('templates').get('main')
    else:
        print "Flights not found"
        sys.exit()


def parse_responce(res):
    html_res = lxml.html.fromstring(res)
    outbound_flights = html_res.xpath('//div[@class="outbound block"]//tbody/tr[contains(@class, "flightrow")]')
    return_flights = html_res.xpath('//div[@class="return block"]//tbody/tr[contains(@class, "flightrow")]')
    currency = html_res.xpath('//th[@class="faregrouptoggle ECO style-eco-comf"]/text()')
    quotes_list_outbound = []
    quotes_list_return = []
    quotes_sum = []
    for n, flight_outnbound in enumerate(outbound_flights):
        price_eco = flight_outnbound.xpath(
            "./td[contains(@headers, \"ECO_COMF\")]/label/div[@class=\"lowest\"]/span/text()")
        if price_eco:
            price_eco = float(price_eco[0])
        price_flex = flight_outnbound.xpath('./td[contains(@headers, "ECO_PREM")]/label/div['
                                            '@class="lowest"]/span/text()')
        if price_flex:
            price_flex = float(price_flex[0])
        price_business = flight_outnbound.xpath('./td[contains(@headers, "BUS_FLEX")]//div['
                                                '@class="lowest"]/span/text()')
        if price_business:
            price_business = float(price_business[0])
        start_end = flight_outnbound.xpath('./td/span/time/text()')
        duration = flight_outnbound.xpath('./td[@class="table-text-left"]/span/text()')
        quote = {"departure": start_end[0],
                 "arrival": start_end[1],
                 "duration of journey": duration[3],
                 "currency": currency,
                 "price": {"price_eco": price_eco,
                           "price_flex": price_flex,
                           "price_business": price_business}, }
        quotes_list_outbound.append(quote)

    for n, flight_return in enumerate(return_flights):
        price_eco = flight_return.xpath("./td[contains(@headers, \"ECO_COMF\")]/label/div["
                                        "@class=\"lowest\"]/span/text()")
        if price_eco:
            price_eco = float(price_eco[0])
        price_flex = flight_return.xpath('./td[contains(@headers, "ECO_PREM")]/label/div['
                                         '@class="lowest"]/span/text()')
        if price_flex:
            price_flex = float(price_flex[0])
        price_business = flight_return.xpath('./td[contains(@headers, "BUS_FLEX")]/label/div['
                                             '@class="lowest"]/span/text()')
        if price_business:
            price_business = float(price_business[0])
        start_end = flight_return.xpath('./td/span/time/text()')
        duration = flight_return.xpath('./td[@class="table-text-left"]/span[contains(@id, "flightDurationFi")]/text()')
        quote = {"departure": start_end[0],
                 "arrival": start_end[1],
                 "duration of journey": duration[0],
                 "currency": currency,
                 "price": {"price_eco": price_eco,
                           "price_flex": price_flex,
                           "price_business": price_business}, }
        quotes_list_return.append(quote)

    if not quotes_list_return:
        table = texttable.Texttable()
        table.set_cols_dtype(['t', 't', 't', 'a', 'a', 'a', 'a'])
        table.set_cols_align(["c", "c", "c", "c", "c", "c", "c"])
        table.set_cols_width([9, 7, 19, 15, 12, 13, 8])
        table.add_rows([["departure",
                         "arrival",
                         "duration of journey",
                         "economy classic",
                         "economy flex",
                         "business flex",
                         "currency"], ])
        print table.draw()
        for quote_list in quotes_list_outbound:
            table = texttable.Texttable()
            table.set_cols_dtype(['t', 't', 't', 'a', 'a', 'a', 'a'])
            table.set_cols_align(["c", "c", "c", "c", "c", "c", "c"])
            table.set_cols_width([9, 7, 19, 15, 12, 13, 8])
            table.add_rows([[quote_list["departure"],
                             quote_list["arrival"],
                             quote_list["duration of journey"],
                             quote_list["price"]["price_eco"],
                             quote_list["price"]["price_flex"],
                             quote_list["price"]["price_business"],
                             quote_list["currency"][0]]])
            print table.draw()
    else:
        for quote_list_outbound in quotes_list_outbound:
            for quote_list_return in quotes_list_return:
                sum_classic = 0
                sum_flex = 0
                sum_business = 0
                quotes = {'departure_outbound': quote_list_return['departure'],
                          'arrival_outbound': quote_list_return['arrival'],
                          'duration_of_journey_outbound': quote_list_return['duration of journey'],
                          'price_outbound': {'price_eco': quote_list_return['price']['price_eco'],
                                             'price_flex': quote_list_return['price']['price_flex'],
                                             'business_flex': quote_list_return['price']['price_business']},
                          'departure_return': quote_list_outbound['departure'],
                          'arrival_return': quote_list_outbound['arrival'],
                          'duration_of_journey_return': quote_list_outbound['duration of journey'],
                          'currency': quote_list_outbound['currency'],
                          'price_return': {'price_eco': quote_list_outbound['price']['price_eco'],
                                           'price_flex': quote_list_outbound['price']['price_flex'],
                                           'business_flex': quote_list_outbound['price']['price_business']},
                          'amount_classic': sum_classic,
                          'amount_flex': sum_flex,
                          'amount_business': sum_business}
                if quote_list_return['price']['price_eco'] and quote_list_outbound['price']['price_eco']:
                    sum_classic = quote_list_return['price']['price_eco'] + quote_list_outbound['price']['price_eco']
                    quotes['amount_classic'] = sum_classic
                if quote_list_return['price']['price_flex'] and quote_list_outbound['price']['price_flex']:
                    sum_flex = quote_list_return['price']['price_flex'] + quote_list_outbound['price']['price_flex']
                    quotes['amount_flex'] = sum_flex
                if quote_list_return['price']['price_business'] and quote_list_outbound['price']['price_business']:
                    price_business_outbound = quote_list_outbound['price']['price_business']
                    price_business_return = quote_list_return['price']['price_business']
                    sum_business = price_business_outbound + price_business_return
                    quotes['amount_business'] = sum_business
                quotes_sum.append(quotes)
        sorted(quotes_sum, 'amount_classic')
        for quote_sum in quotes_sum:
            table = texttable.Texttable()
            table.set_cols_dtype(['t', 't', 't', 'a', 'a', 'a', 'a'])
            table.set_cols_align(["c", "c", "c", "c", "c", "c", "c"])
            table.set_cols_width([9, 7, 19, 15, 12, 13, 8])
            table.add_rows([["departure",
                             "arrival",
                             "duration of journey",
                             "economy classic",
                             "economy flex",
                             "business flex",
                             "currency"],
                            [quote_sum["departure_outbound"],
                             quote_sum["arrival_outbound"],
                             quote_sum["duration_of_journey_outbound"],
                             quote_sum["price_outbound"]["price_eco"],
                             quote_sum["price_outbound"]["price_flex"],
                             quote_sum["price_outbound"]["business_flex"],
                             quote_sum["currency"][0]],
                            [quote_sum["departure_return"],
                             quote_sum["arrival_return"],
                             quote_sum["duration_of_journey_return"],
                             quote_sum["price_return"]["price_eco"],
                             quote_sum["price_return"]["price_flex"],
                             quote_sum["price_return"]["business_flex"],
                             quote_sum["currency"][0]],
                            ["",
                             "",
                             "the amount:",
                             quote_sum["amount_classic"],
                             quote_sum["amount_flex"],
                             quote_sum["amount_business"],
                             quote_sum["currency"][0]]])
            print table.draw() + "\n"


if __name__ == '__main__':
    scrape()


