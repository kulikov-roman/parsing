import argparse
import sys
import lxml.html

from datetime import datetime, timedelta

from requests import Session


def scrape():
    parser = create_parser()
    namespace = parser.parse_args()
    validation(namespace)
    res = get_res(namespace)
    parse_responce(res)


def create_parser():
    parse = argparse.ArgumentParser()
    parse.add_argument('departure')
    parse.add_argument('destination')
    parse.add_argument('outboundDate', type=lambda s: datetime.strptime(s, '%Y-%m-%d'))
    parse.add_argument('returnDate', nargs='?', default='')
    return parse


def validation(namespace):
    date = datetime.now()
    current_date = date.strftime('%Y-%m-%d')
    # the maximum date that can be selected is limited to 360 days from the current date
    limit_date = date + timedelta(days=360)
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
    ses = Session()
    ses_req = ses.post(url, data=data_req, verify=False)
    ses_res = ses.post(ses_req.url, data=data_res, verify=False)
    res = (ses_res.json().get('templates').get('main'))
    return res


def parse_responce(res):
    html_res = lxml.html.fromstring(res)
    outbound_flights = html_res.xpath('//div[@class="outbound block"]//tbody/tr[contains(@class, "flightrow")]')
    return_flights = html_res.xpath('//div[@class="return block"]//tbody/tr[contains(@class, "flightrow")]')
    currency = html_res.xpath('//th[@class="faregrouptoggle ECO style-eco-comf"]/text()')
    quotes_list_outbound = []
    quotes_list_return = []
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
                           "price_business": price_business},
                 }
        quotes_list_outbound.append(quote)

    for n, flight_return in enumerate(return_flights):
        price_eco = flight_return.xpath(
            "./td[contains(@headers, \"ECO_COMF\")]/label/div[@class=\"lowest\"]/span/text()")
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
        start_end = flight_outnbound.xpath('./td/span/time/text()')
        duration = flight_outnbound.xpath('./td[@class="table-text-left"]/span/text()')
        quote = {"departure": start_end[0],
                 "arrival": start_end[1],
                 "duration of journey": duration[3],
                 "currency": currency,
                 "price": {"price_eco": price_eco,
                           "price_flex": price_flex,
                           "price_business": price_business},
                 }
        quotes_list_return.append(quote)

    if not quotes_list_return:
        print ('                                   {}'.format("outbound flight:"))
        print (
            '{}'.format("__________________________________________________________________________________________"))
        print ('{}   {}   {}   {}   {}   {}'.format('departure',
                                                    'arrival',
                                                    'duration of journey',
                                                    'Economy Classic',
                                                    'Economy Flex',
                                                    'Business Flex'))
        for quote_list in quotes_list_outbound:
            print ('  {}      {}      {}            {}            {}            {}'.format(quote_list["departure"],
                                                                                           quote_list['arrival'],
                                                                                           quote_list[
                                                                                               "duration of journey"],
                                                                                           quote_list["price"][
                                                                                               "price_eco"],
                                                                                           quote_list["price"][
                                                                                               "price_flex"],
                                                                                           quote_list["price"][
                                                                                               "price_business"]))
    else:
        print ('                                   {}'.format("outbound flight:"))
        print (
            '{}'.format("__________________________________________________________________________________________"))
        print ('{}   {}   {}   {}   {}   {}'.format('departure',
                                                    'arrival',
                                                    'duration of journey',
                                                    'Economy Classic',
                                                    'Economy Flex',
                                                    'Business Flex'))
        for quote_list in quotes_list_outbound:
            print ('  {}      {}      {}            {}            {}            {}'.format(quote_list["departure"],
                                                                                           quote_list['arrival'],
                                                                                           quote_list[
                                                                                               "duration of journey"],
                                                                                           quote_list["price"][
                                                                                               "price_eco"],
                                                                                           quote_list["price"][
                                                                                               "price_flex"],
                                                                                           quote_list["price"][
                                                                                               "price_business"]))
        print ('                                   {}'.format("return flight:"))
        print (
            '{}'.format("__________________________________________________________________________________________"))
        for quote_list in quotes_list_return:
            print ('  {}      {}      {}            {}            {}            {}'.format(quote_list["departure"],
                                                                                           quote_list['arrival'],
                                                                                           quote_list[
                                                                                               "duration of journey"],
                                                                                           quote_list["price"][
                                                                                               "price_eco"],
                                                                                           quote_list["price"][
                                                                                               "price_flex"],
                                                                                           quote_list["price"][
                                                                                               "price_business"]))


if __name__ == '__main__':
    scrape()
