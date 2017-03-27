import json
from lxml import html

with open('Fiddler_0-46-47.json') as data_file:
    data = json.load(data_file)

response =  (data.get('templates').get('main'))

tree = html.fromstring(response.content)
