import argparse
import re
import sys
import lxml
import requests
import lxml.html


def scrape():
    create_parser()
    input_validation()
    get_res()
    parse_res()


def create_parser():
    parse = argparse.ArgumentParser()
    parse.add_argument('departure', nargs='?')
    parse.add_argument('destination', nargs='?')
    parse.add_argument('outboundDate', nargs='?')
    parse.add_argument('returnDate', nargs='?', default='')
    return parse


if __name__ == '__main__':
    parser = create_parser()
    namespace = parser.parse_args()


def input_validation():
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


def get_res():
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


def parse_res():
    html = lxml.html.fromstring(get_res())
    out_bound = html.xpath('//div[@class="lowest"]/span[@title]')
    for i in out_bound:
        print (i)


scrape()
