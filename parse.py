"""Scraper module for Flyniki website https://www.flyniki.com"""

import datetime
import sys
from argparse import ArgumentParser

import texttable
from lxml import html
from requests import Session

CLASS_MAPPING = {
    'ECO_COMF': 'Economy Classic',
    'ECO_PREM': 'Economy Flex',
    'BUS_FLEX': 'Business Flex'
}


def scrape():
    """Main function with scraper functions calls"""
    parser = create_parser()
    namespace = parser.parse_args()
    validation(namespace)
    response, one_way = get_res(namespace)
    quotes = parse_response(response)
    print_result(quotes, one_way)


def create_parser():
    """Parse user search arguments"""
    parse = ArgumentParser()
    parse.add_argument('departure')
    parse.add_argument('destination')
    parse.add_argument('outboundDate', type=lambda s: datetime.datetime.strptime(s, '%Y-%m-%d'))
    parse.add_argument('returnDate', nargs='?', default='')
    return parse


def validation(namespace):
    """Validate user input"""
    current_date = datetime.datetime.now()
    current_date_str = current_date.strftime('%Y-%m-%d')
    # the maximum date that can be selected is limited to 365 days from the current date
    limit_date = current_date + datetime.timedelta(days=365)
    limit_date = limit_date.strftime('%Y-%m-%d')
    if not namespace.departure.isalpha() or len(namespace.departure) != 3:
        print 'The input is not correct. Example, DME'
        sys.exit()
    elif not namespace.destination.isalpha() or len(namespace.destination) != 3:
        print 'The input is not correct. Example, CGN'
        sys.exit()
    elif namespace.outboundDate.strftime('%Y-%m-%d') < current_date_str:
        print 'The input is not correct.'
        sys.exit()
    elif namespace.outboundDate.strftime('%Y-%m-%d') > limit_date:
        print 'The input is not correct.'
        sys.exit()
    else:
        print 'The input is correct.'


def get_res(namespace):
    """
    Construct request to the website and receive response
    """
    one_way = False
    url = 'https://www.flyniki.com/en/booking/flight/vacancy.php'
    data_get_response = {'_ajax[templates][]': ('main',
                                                'priceoverview',
                                                'infos',
                                                'flightinfo'),
                         '_ajax[requestParams][departure]': namespace.departure.upper(),
                         '_ajax[requestParams][destination]': namespace.destination.upper(),
                         '_ajax[requestParams][outboundDate]':
                             namespace.outboundDate.strftime('%Y-%m-%d'),
                         '_ajax[requestParams][returnDate]': namespace.returnDate,
                         '_ajax[requestParams][oneway]': ''}
    data_request = {'departure': namespace.departure.upper(),
                    'outboundDate': namespace.outboundDate.strftime('%Y-%m-%d'),
                    'returnDate': namespace.returnDate,
                    'oneway': '',
                    'adultCount': '1'}
    if not namespace.returnDate:
        one_way = True
        data_request['returnDate'] = namespace.outboundDate.strftime('%Y-%m-%d')
        data_request['oneway'] = 'on'
        data_get_response['_ajax[requestParams][returnDate]'] = \
            namespace.outboundDate.strftime('%Y-%m-%d')
        data_get_response['_ajax[requestParams][oneway]'] = 'on'
    session = Session()
    session_request = session.post(url, data=data_request, verify=False)
    get_response = session.post(session_request.url, data=data_get_response, verify=False)
    response = get_response.json()
    if 'templates' in response:
        return response.get('templates').get('main'), one_way

    else:
        print 'Flights not found'
        exit()


def parse_response(res):
    """Parse response"""
    quotes = []
    res_html = html.fromstring(res)
    outbound_list = res_html.xpath('//div[@class="outbound block"]//tbody'
                                   '/tr[contains(@class, "flightrow")]')
    return_list = res_html.xpath('//div[@class="return block"]//tbody'
                                 '/tr[contains(@class, "flightrow")]')
    currency = list(set(res_html.xpath('//th[contains(@class, "faregrouptoggle")]/text()')))[0]
    for out_info in outbound_list:

        outbound_fares = out_info.xpath('.//td[contains(@class, "fare")'
                                        'and not(./span[@class="notbookable"])]')
        for out_fare in outbound_fares:
            outbound_leg = create_leg(out_info, out_fare, currency)

            if return_list:
                for in_info in return_list:

                    inbound_fares = in_info.xpath(
                        './/td[contains(@class, "fare") and not(./span[@class="notbookable"])]')
                    for in_fare in inbound_fares:
                        inbound_leg = create_leg(in_info, in_fare, currency)
                        quote = {
                            'outbound_leg': outbound_leg,
                            'inbound_leg': inbound_leg,
                            'total_price': outbound_leg['price'] + inbound_leg['price']
                        }
                        quotes.append(quote)

            else:
                quote = {
                    'outbound_leg': outbound_leg,
                    'total_price': outbound_leg['price']
                }
                quotes.append(quote)
    return quotes


def create_leg(info, fare, currency):
    """Create leg object"""
    start_end = info.xpath('./td/span/time/text()')
    duration = info.xpath('./td[@class="table-text-left"]'
                          '/span[contains(@id, "flightDurationFi")]/text()')[0]
    price = fare.xpath('.//div[@class="lowest"]'
                       '/span[contains(@id, "price")]/text()')[0]
    leg = {
        'departure': start_end[0],
        'arrival': start_end[1],
        'flight_duration': duration,
        'currency': currency,
        'price': float(price),
        'class': [CLASS_MAPPING[x] for x in CLASS_MAPPING.keys()
                  if x in fare.xpath('./@class')[0]][0]
    }

    return leg


def print_result(quotes, one_way):
    """Print list of quotes as table"""
    header_table = ('departure', 'arrival', 'duration of journey',
                    'class', 'price', 'currency')

    for quote_list in sorted(quotes, key=lambda d: d['total_price']):
        table = make_table()
        flight_row = [header_table, get_flight_row(quote_list, 'outbound_leg')]
        if not one_way:
            flight_row.extend([get_flight_row(quote_list, 'inbound_leg'),
                               ['', '', '', 'Total amount:',
                                quote_list['total_price'],
                                quote_list['outbound_leg']['currency']]])
        table.add_rows(flight_row)
        print table.draw() + '\n'


def make_table():
    """Setting table for output"""
    table = texttable.Texttable()
    table.set_cols_dtype(['t', 't', 't', 'a', 'a', 'a'])
    table.set_cols_align(["c", "c", "c", "c", "c", "c"])
    table.set_cols_width([9, 7, 19, 15, 12, 13])
    return table


def get_flight_row(flight_dict, leg):
    """Returns a list of values to substitute in the output"""
    return [flight_dict[leg]['departure'],
            flight_dict[leg]['arrival'],
            flight_dict[leg]['flight_duration'],
            flight_dict[leg]['class'],
            flight_dict['total_price'],
            flight_dict[leg]['currency']]


if __name__ == '__main__':
    scrape()
