from urllib.parse import (
    quote,
    urlencode,
)
from lxml import html
import random
import requests
import re
from searx.utils import (
    eval_xpath_getindex,
    eval_xpath_list,
    extract_text,
)


about={
    "website": 'https://weixin.sogou.com/weixin',
    "wikidata_id": None,
    "official_api_documentation": None,
    "use_official_api": False,
    "require_api_key": False,
    "results": 'HTML',
}
categories = ['general', 'web']
paging = False
time_range_support = False


def request(query, params):
    base_url = 'https://weixin.sogou.com/weixin'
    args = urlencode(
        {
            'query':query,
            'page':1,
            'type':2,
        }
    )
    params['url'] = base_url + '?' + args


def parse_url(url_string):
    url = 'https://weixin.sogou.com' + url_string
    b = random.randint(0, 99)
    a = url.index('url=')
    a = url[a + 30 + b:a + 31 + b:]
    url += '&k=' + str(b) + '&h=' + a
    return url


def parse_url2(url_string):
    hder = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) \
        Chrome/122.0.0.0 Safari/537.36 Edg/122.0.0.0',
        'Cookie': 'ssuid=9651828800; SUID=A2FECF7C1AA7A20B000000006694AD27; cuid=AAHHUGJrTQAAAAuipikTpgEANgg=;\
        SUV=1721019689438419; ABTEST=0|1721019689|v1; SNUID=D18DBB0874756E366C36BF0B7401396F; SMYUV=1721022241781501;\
        IPLOC=CN1100; ariaDefaultTheme=undefined',
    }
    '''
    proxy = {
        'http':'127.0.0.1:****',
        'https':'127.0.0.1:****',
    }
    # set with your specific port
    '''
    resp = requests.get(url_string, headers=hder) # , proxies=proxy)
    parsed_url_list = re.findall(r"url \+= '(.+)'", resp.text)
    parsed_url = ''.join(parsed_url_list)
    parsed_url = re.sub(r'@', r'', parsed_url)
    return parsed_url



def response(resp):
    results = []
    dom = html.fromstring(resp.text)

    # parse results
    for result in eval_xpath_list(dom, '//div[contains(@class,"txt-box")]'):
        url = eval_xpath_getindex(result, './/h3/a/@href', 0, default=None)
        if url is None:
            continue
        url = parse_url(url)
        url = parse_url2(url)
        title1 = eval_xpath_getindex(result, './/h3//a/text()', 0, default='')
        title2 = eval_xpath_getindex(result, './/h3//a/text()', 1, default='')
        title_em1 = eval_xpath_getindex(result, './/h3//a/em/text()', 0, default='')
        title_em2 = eval_xpath_getindex(result, './/h3//a/em/text()', 1, default='')
        if title2 == '':
            title = extract_text(title_em1 + title1)
        else:
            title = extract_text(title1+title_em1+title2+title_em2)
        # title = '123'
        content = eval_xpath_getindex(result, './/p[contains(@class, "txt-info")]', 0, default='')
        content = extract_text(content, allow_none=True)

        # append result
        results.append({'url': url, 'title': title, 'content': content})
    return results