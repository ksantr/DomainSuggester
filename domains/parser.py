import itertools
import grequests
from bs4 import BeautifulSoup as bs

url = 'http://www.registered-domains-list.com/info-2013/{}.html'

pages = []

for page in range(1, 10000):
    pages.append(url.format(page))

def grouper(n, iterable):
    """Group iterable into groups by n number"""
    args = [iter(iterable)] * n
    return ([e for e in t if e is not None] for t in
            itertools.izip_longest(*args))

def exception_handler(request, exception):
    print request.url

def parse_page(response):
    if not response.status_code == 200:
        return

    domains = bs(response.text)
    res = domains.td.getText()
    res = res.encode('utf-8')
    domains = res.split()
    with open('info.txt', 'a+') as f:
        f.write('\n'.join(domains))

groups = grouper(50, pages)

for group in groups:
    rs = (grequests.get(page,
        timeout=8) for page in group)
    responses = grequests.map(rs,
            exception_handler=exception_handler)

    for response in responses:
        parse_page(response)
