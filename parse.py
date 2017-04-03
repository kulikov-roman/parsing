import requests
import argparse
import sys
import re


#def scrape():
    #create_parser()
    #request = get_res()


def create_parser():
    parse = argparse.ArgumentParser()
    parse.add_argument('departure', nargs='?')
    parse.add_argument('destination', nargs='?')
    parse.add_argument('outboundDate', nargs='?')
    parse.add_argument('returnDate', nargs='?', default=sys.argv[3])
    return parse


if __name__ == '__main__':
    parser = create_parser()
    namespace = parser.parse_args()


def input_validation():
    enter_dep = re.findall(r'[A-Z]{1,3}', namespace.departure)
    enter_des = re.findall(r'[A-Z]{1,3}', namespace.destination)

    if sys.argv[1] == enter_dep[0] and sys.argv[2] == enter_des[0]:
        print ("The data is entered correctly")
    else:
        print ("The data entered is not correct")
        sys.exit()


input_validation()


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
    ses = requests.Session()
    ses_req = ses.post(url, data=data_req, verify=False)
    ses_res = ses.post(ses_req.url, data=data_res, verify=False)
    return ses_res


print get_res().text
