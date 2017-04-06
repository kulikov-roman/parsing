import argparse
import sys
import lxml
import requests
import lxml.html


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
    parse.add_argument('outboundDate')
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
                '_ajax[requestParams][outboundDate]': namespace.outboundDate,
                '_ajax[requestParams][returnDate]': namespace.returnDate,
                '_ajax[requestParams][oneway]': ''}
    data_req = {'departure': namespace.departure.upper(),
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


def parse_responce(responce):
    html = lxml.html.fromstring(responce)
    out_bound = html.xpath('//div[@class="lowest"]/span/@title')
    currency = html.xpath('//th[@class="faregrouptoggle ECO style-eco-comf"]/text()')
    list_fly = {"departure": [],
                "arrival": [],
                "duration of journey": [],
                "price": [],
                "class type": [],
                "currency": currency}
    for u in out_bound:
        u = u.split(",")
        dep_arriv = u[1].split("-")
        class_flight = u[3].split(":")
        list_fly["departure"].append(dep_arriv[0])
        list_fly["arrival"].append(dep_arriv[1])
        list_fly["duration of journey"].append(u[2])
        list_fly["class type"].append(class_flight[0])
        list_fly["price"].append(class_flight[1].strip())

if __name__ == '__main__':
    scrape()

