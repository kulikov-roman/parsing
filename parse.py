import requests
import argparse


def create_parser():
    parse = argparse.ArgumentParser()
    parse.add_argument('departure', nargs='?')
    parse.add_argument('destination', nargs='?')
    parse.add_argument('outboundDate', nargs='?')
    parse.add_argument('returnDate', nargs='?')
    return parse


if __name__ == '__main__':
    parser = create_parser()
    namespace = parser.parse_args()


def get_res():
    url = 'https://www.flyniki.com/en/booking/flight/vacancy.php?'
    data_res = {'_ajax[templates][]': ('main', 'priceoverview', 'infos', 'flightinfo'),
                '_ajax[requestParams][departure]': namespace.departure,
                '_ajax[requestParams][destination]': namespace.destination,
                '_ajax[requestParams][outboundDate]': namespace.outboundDate,
                '_ajax[requestParams][returnDate]': namespace.returnDate,
                '_ajax[requestParams][oneway]': ''}
    data_req = {'departure': 'DME', 'outboundDate': '2017-05-07',
                'returnDate': '2017-05-14',
                'oneway': '0',
                'adultCount': '1'}
    ses = requests.Session()
    ses_req = ses.post(url, data=data_req, verify=False)
    ses_res = ses.post(ses_req.url, data=data_res, verify=False)
    return ses_res
print get_res().text
