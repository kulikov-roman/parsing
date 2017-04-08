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
    for flight in outbound_flights:
        start_end = flight.xpath('./td/span/time/text()')
        duration = flight.xpath('./td[@class="table-text-left"]/span/text()')
        price = flight.xpath('./td[@role="radio"]/label/div[@class="lowest"]/span/text()')
        sdfsdf = flight.xpath('//tbody/tr/td/span/text()')
        number_flight = flight.xpath('//table[@role="presentation"]/tbody/tr/td[@class="table-text-center"]/text()')
        print price
        print duration[3]
        print start_end
        print sdfsdf[24]
        print number_flight[0], number_flight[3]
    """
    currency = html.xpath('//th[@class="faregrouptoggle ECO style-eco-comf"]/text()')
    quotes_list = []
    # list_fly = {"departure": [],
    #             "arrival": [],
    #             "duration of journey": [],
    #             "price_list": [],
    #             "price_float": [],
    #             "class type": [],
    #             "currency": currency}
    for u in out_bound:
        segment_info = u.xpath
        u = u.split(",")
        dep_arriv = u[1].split("-")
        class_flight = u[3].split(":")
        dep_time = dep_arriv[0]
        arr_time = dep_arriv[1]
        price = float((class_flight[1].strip())
        flight = {
            "out_bound": {
                out_
            }
                     "departure": dep_time,
                "arrival": arr_time,
                "duration of journey": ,
                "price": ,
                "class type": ,
                "currency": currency}
        list_fly["departure"].append(dep_arriv[0])
        list_fly["arrival"].append(dep_arriv[1])
        list_fly["duration of journey"].append(u[2])
        list_fly["class type"].append(class_flight[0])
        list_fly["price_list"].append(class_flight[1].strip())
        quotes_list.append(flight)
    print list_fly["price_list"]
    for i in list_fly["price_list"]:
        list_fly["price_float"].append(float(i))
    print list_fly["price_float"]
    print list_fly
"""
if __name__ == '__main__':
    scrape()
