import argparse
import re
import sys
import lxml
import requests
import lxml.html


def scrape():
    parser = create_parser()
    namespace = parser.parse_args()
    input_validation(namespace)
    get_r = get_res(namespace)
    parse_res(get_r)


def create_parser():
    parse = argparse.ArgumentParser()
    parse.add_argument('departure', nargs='?')
    parse.add_argument('destination', nargs='?')
    parse.add_argument('outboundDate', nargs='?')
    parse.add_argument('returnDate', nargs='?', default='')
    return parse


def input_validation(namespace):
    enter_dep = re.findall(r"[A-Z]{1,3}", namespace.departure)
    enter_des = re.findall(r"[A-Z]{1,3}", namespace.destination)
    enter_out = re.findall(r"[0-3]?[0-9].[0-3]?[0-9].[0-3]?[0-9].(?:[0-9]{2})?[0-9]{2}$", namespace.outboundDate)
    enter_return = re.findall(r"[0-3]?[0-9].[0-3]?[0-9].[0-3]?[0-9].(?:[0-9]{2})?[0-9]{2}$", namespace.returnDate)

    if namespace.departure != enter_dep[0]:
        print ("The input is not correct. Example, DME")
        sys.exit()
    elif namespace.destination != enter_des[0]:
        print ("The input is not correct. Example, CGN")
        sys.exit()
    elif namespace.outboundDate != enter_out[0]:
        print ("The input is not correct. Example, 2017-05-07")
        sys.exit()
    else:
        print (enter_dep, enter_des, enter_out, enter_return)
        print ("The data is entered correctly")


def get_res(namespace):
    url = 'https://www.flyniki.com/en/booking/flight/vacancy.php?'
    data_res = {'_ajax[templates][]': ('main', 'priceoverview', 'infos', 'flightinfo'),
                '_ajax[requestParams][departure]': namespace.departure,
                '_ajax[requestParams][destination]': namespace.destination,
                '_ajax[requestParams][outboundDate]': namespace.outboundDate,
                '_ajax[requestParams][returnDate]': namespace.returnDate,
                '_ajax[requestParams][oneway]': ''}
    data_req = {'departure': namespace.departure,
                'outboundDate': namespace.outboundDate,
                'returnDate': namespace.returnDate,
                'oneway': '',
                'adultCount': '1'}
    if namespace.returnDate == '':
        data_req['returnDate'] = namespace.outboundDate
        data_req['oneway'] = 'on'
        data_res['_ajax[requestParams][returnDate]'] = namespace.outboundDate
        data_res['_ajax[requestParams][oneway]'] = 'on'
    ses = requests.Session()
    ses_req = ses.post(url, data=data_req, verify=False)
    ses_res = ses.post(ses_req.url, data=data_res, verify=False)
    res = (ses_res.json().get('templates').get('main'))
    return res


def parse_res(get_r):
    html = lxml.html.fromstring(get_r)
    out_bound = html.xpath('//div[@class="lowest"]/span/@title')
    price = html.xpath('//th[@class="faregrouptoggle ECO style-eco-comf"]/text()')
    list_fly = {"departure: ": [], "arrival: ": [], "duration of journey: ": [], "price:": [], "class type: ": []}
    print " departure:", "   ", "arrival:", "      duration of journey:", "      price:", "         class type:"
    for u in out_bound:
        u = u.split(",")
        dep_arriv = u[1].split("-")
        class_flight = u[3].split(":")
        list_fly["departure: "] = dep_arriv[0]
        list_fly["arrival: "] = dep_arriv[1]
        list_fly["duration of journey: "] = u[2]
        list_fly["class type: "] = class_flight[0]
        list_fly["price : "] = class_flight[1].strip()
        print " ", list_fly["departure: "], "       ", list_fly["arrival: "], "          ", list_fly[
            "duration of journey: "], "         ", price[0].strip(), list_fly[
            "price : "], "     ", list_fly["class type: "]


if __name__ == '__main__':
    scrape()
