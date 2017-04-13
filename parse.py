from argparse import ArgumentParser
import sys

import texttable
import lxml.html

from datetime import datetime, timedelta
import requests

from time import sleep


CLASS_MAPPING = {
    'ECO_COMF': 'Economy Classic',
    'ECO_PREM': 'Economy Flex',
    'BUS_FLEX': 'Business Flex'
}


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
    quotes = []

    html = lxml.html.fromstring(res)
    outbound_list = html.xpath('//div[@class="outbound block"]//tbody/tr[contains(@class, "flightrow")]')
    return_list = html.xpath('//div[@class="return block"]//tbody/tr[contains(@class, "flightrow")]')

    currency = list(set(html.xpath('//th[contains(@class, "faregrouptoggle")]/text()')))[0]
    for out_info in outbound_list:
        quote = {}
        outbound_fares = out_info.xpath(".//td[contains(@class, 'fare') and not(./span[@class='notbookable'])]")
        for out_fare in outbound_fares:
            start_end = out_info.xpath('./td/span/time/text()')
            duration = out_info.xpath('./td[@class="table-text-left"]'
                                      '/span[contains(@id, "flightDurationFi")]/text()')[0]
            price = out_fare.xpath('.//div[@class="lowest"]'
                                   '/span[contains(@id, "price")]/text()')[0]
            outbound_leg = {
                "departure": start_end[0],
                "arrival": start_end[1],
                "flight_duration": duration,
                "currency": currency,
                "price": float(price),
                "class": [CLASS_MAPPING[x] for x in CLASS_MAPPING.keys()
                          if x in out_fare.xpath('./@class')[0]][0]
                }
            quote['outbound_leg'] = outbound_leg
            # quote['total_price'] = outbound_leg['price']
            print outbound_leg['price']

            if return_list:
                for in_info in return_list:
                    inbound_fares = in_info.xpath(
                        ".//td[contains(@class, 'fare') and not(./span[@class='notbookable'])]")
                    for in_fare in inbound_fares:
                        start_end = in_info.xpath('./td/span/time/text()')
                        duration = in_info.xpath('./td[@class="table-text-left"]'
                                                 '/span[contains(@id, "flightDurationFi")]/text()')[0]
                        price = in_fare.xpath('.//div[@class="lowest"]'
                                              '/span[contains(@id, "price")]/text()')
                        # print "="*5, price, "="*5
                        inbound_leg = {
                            "departure": start_end[0],
                            "arrival": start_end[1],
                            "flight_duration": duration,
                            "currency": currency,
                            "price": float(price[0]),
                            "class": [CLASS_MAPPING[x] for x in CLASS_MAPPING.keys()
                                      if x in in_fare.xpath('./@class')[0]][0]
                        }
                        quote['inbound_leg'] = inbound_leg
                        # total_price = outbound_leg['price'] + inbound_leg['price']
                        quote['total_price'] = outbound_leg['price'] + inbound_leg['price']
                        quotes.append(quote)
            else:
                quote['total_price'] = outbound_leg['price']
                quotes.append(quote)

    for i in outbound_list:
        print i
    """
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
                amount = 0

                quotes = {'departure_return': quote_list_return['departure'],
                          'arrival_return': quote_list_return['arrival'],
                          'duration_of_journey_return': quote_list_return['duration of journey'],
                          'price_return': {'price_eco': quote_list_return['price']['price_eco'],
                                           'price_flex': quote_list_return['price']['price_flex'],
                                           'business_flex': quote_list_return['price']['price_business']},
                          'departure_outbound': quote_list_outbound['departure'],
                          'arrival_outbound': quote_list_outbound['arrival'],
                          'duration_of_journey_outbound': quote_list_outbound['duration of journey'],
                          'currency': quote_list_outbound['currency'],
                          'price_outbound': {'price_eco': quote_list_outbound['price']['price_eco'],
                                             'price_flex': quote_list_outbound['price']['price_flex'],
                                             'business_flex': quote_list_outbound['price']['price_business']},
                          'amount': amount}

                if quote_list_return['price']['price_eco'] and quote_list_outbound['price']['price_eco']:
                    amount = quote_list_return['price']['price_eco'] + quote_list_outbound['price']['price_eco']
                    quotes['amount'] = amount
                    quotes_sum.append(quotes)
                if quote_list_return['price']['price_eco'] and quote_list_outbound['price']['price_flex']:
                    amount = quote_list_return['price']['price_eco'] + quote_list_outbound['price']['price_flex']
                    quotes['amount'] = amount
                    quotes_sum.append(quotes)
                if quote_list_return['price']['price_eco'] and quote_list_outbound['price']['price_business']:
                    amount = quote_list_return['price']['price_eco'] + quote_list_outbound['price']['price_business']
                    quotes['amount'] = amount
                    quotes_sum.append(quotes)
                if quote_list_return['price']['price_flex'] and quote_list_outbound['price']['price_eco']:
                    amount = quote_list_return['price']['price_eco'] + quote_list_outbound['price']['price_eco']
                    quotes['amount'] = amount
                    quotes_sum.append(quotes)
                if quote_list_return['price']['price_flex'] and quote_list_outbound['price']['price_flex']:
                    amount = quote_list_return['price']['price_eco'] + quote_list_outbound['price']['price_flex']
                    quotes['amount'] = amount
                    quotes_sum.append(quotes)
                if quote_list_return['price']['price_flex'] and quote_list_outbound['price']['price_business']:
                    amount = quote_list_return['price']['price_eco'] + quote_list_outbound['price']['price_business']
                    quotes['amount'] = amount
                    quotes_sum.append(quotes)
                if quote_list_return['price']['price_business'] and quote_list_outbound['price']['price_eco']:
                    amount = quote_list_return['price']['price_business'] + quote_list_outbound['price']['price_eco']
                    quotes['amount'] = amount
                    quotes_sum.append(quotes)
                if quote_list_return['price']['price_business'] and quote_list_outbound['price']['price_flex']:
                    amount = quote_list_return['price']['price_business'] + quote_list_outbound['price']['price_flex']
                    quotes['amount'] = amount
                    quotes_sum.append(quotes)
                if quote_list_return['price']['price_business'] and quote_list_outbound['price']['price_business']:
                    amount = quote_list_return['price']['price_business'] + quote_list_outbound['price'][
                        'price_business']
                    quotes['amount'] = amount
                    quotes_sum.append(quotes)
        for i in quotes_sum:
            print i

        for quote_sum in sorted(quotes_sum, key=lambda d: d['amount_classic']):
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
        """


if __name__ == '__main__':
    scrape()
