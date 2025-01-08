from abc import ABC, abstractmethod, abstractproperty
import ast
import codecs
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
import math
import re
from typing import Any
import requests
from requests import Response
from bs4 import BeautifulSoup
import time
import random
import json 
from urllib.parse import urlparse, parse_qs
from requests.exceptions import ConnectTimeout, ReadTimeout
from django.utils import timezone


user_agents = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36',
	'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 YaBrowser/22.9.1 Yowser/2.5 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36 Edg/106.0.1370.52',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36 Vivaldi/5.5.2805.38',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36 OPR/92.0.4561.21',

    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 13_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36 Edg/106.0.1370.52',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 13_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 YaBrowser/22.9.1 Yowser/2.5 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 13_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36 Vivaldi/5.5.2805.38',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 13_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 13_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36 OPR/92.0.4561.21',

    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.5351.0 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36 OPR/92.0.4561.21',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36 Vivaldi/5.5.2805.38',
]


@dataclass
class Info:
    url: str
    host: str
    title: str
    img_url: str
    currency: str
    date_time: datetime
    archive: bool = False
    in_stock: bool = None
    price: float = None

    @property
    def price(self) -> float:
        return self._price

    @price.setter
    def price(self, p: float) -> None:
        if type(p) in [int, float]:
            self._price = p
            self.in_stock = True
        else:
            self._price = None
            self.in_stock = False


class BaseParser(ABC):
    def __init__(self, url: str = '') -> None:
        self.url = url
        self.title    = None
        self.img_url  = None
        self.price    = None
        self.currency = None
        self.archive  = False
        self.in_stock = None
        pass

    def get_response(self, url: str = '', method: str = 'get',
                     *args, **kwargs) -> Response | None:
        if not url:
            url = self.url

        for _ in range(2):
            user_agent = random.choice(user_agents)
            headers = {
                'User-Agent': user_agent,
                'Content-type': 'application/text; charset=utf-8',
                }
            request = requests
            try:
                if method == 'get':
                    response = request.get(url=url, headers=headers,
                                           timeout=(5, 5), *args, **kwargs)
                elif method == 'post':
                    if 'headers' in kwargs:
                        kwargs['headers']['User-Agent'] = user_agent
                    else:
                        kwargs['headers'] = headers
                    response = request.post(url=url,
                                            timeout=(5, 5), *args, **kwargs)
                if response.status_code == 200:
                    return response
            except ConnectTimeout:
                time.sleep(1)
            except ReadTimeout:
                time.sleep(1)
            except Exception as inst:
                time.sleep(1)
        return None

    def get_beautiful_soup(self, html: str = None) -> BeautifulSoup | None:
        if not html:
            return None

        soup = BeautifulSoup(html, 'lxml')
        return soup

    @abstractproperty
    def host() -> str:
        pass

    @abstractmethod
    def scraping_info(self, data: Any = None) -> bool:
        pass

    @abstractmethod
    def create_info(self):
        pass

    def get_info(self) -> Info | None:
        if not self.create_info():
            return None
        info = Info(
            url      = self.url,
            host     = self.host,
            title    = self.title,
            img_url  = self.img_url,
            price    = self.price,
            currency = self.currency,
            archive  = self.archive,
            in_stock = self.in_stock,
            date_time = timezone.now()
        )
        return info


class BaseSoupParser(BaseParser):
    def create_info(self) -> bool:
        html = self.get_response(self.url)
        if not html:
            return False
        soup = self.get_beautiful_soup(html=html.text)
        if not soup:
            return False
        if not self.scraping_info(data=soup):
            return False
        return True


class BaseJSONParser(BaseParser, ABC):
    def create_info(self, *args, **kwargs) -> bool:
        url = kwargs.get('url', None)
        response = self.get_response(url=url)
        if response is None:
            return False
        try:
            json = response.json()
        except Exception:
            return False

        if not self.scraping_info(data=json, *args, **kwargs):
            return False
        return True


class Parser(BaseParser):
    host = ''

    def scraping_info(self) -> None:
        return None

    def create_info(self) -> bool:
        return False


class Sulpak(BaseSoupParser):
    host = 'www.sulpak.kz'

    def scraping_info(self, data: BeautifulSoup) -> bool:
        product_info = data.find_all(name='script', type='application/ld+json')[1]
        product_info = json.loads( product_info.text.replace('\n', ''))

        try:
            self.img_url = product_info['image']
            self.title   = product_info['name']
            self.price   = product_info['offers']['price']
            available    = True if product_info['offers']['availability'] == 'https://schema.org/InStock' else False
            self.currency = '₸'

            if self.price != 'null':
                self.price = float(self.price)
        except:
            return False
        return True


class Technodom(BaseSoupParser):
    host = 'www.technodom.kz'

    def scraping_info(self, data: BeautifulSoup) -> bool:
        soup = data

        product_info = data.find_all(name='script', type='application/ld+json')[0]
        product_info = json.loads( product_info.text.replace('\n', ''))

        try:
            self.img_url = product_info['image'][0][0]
            self.title   = product_info['name']
            self.price   = product_info['offers']['price']
            available    = True if product_info['offers']['availability'] == 'https://schema.org/InStock' else False
            self.currency = '₸'

            if self.price != 'null':
                self.price = float(self.price)
        except:
            return False
        return True


class ShopKz(BaseSoupParser):
    host = 'shop.kz'

    def scraping_info(self, data: BeautifulSoup) -> bool: 

        product_info = data.find_all(name='script', type='application/ld+json')[1]
        product_info = json.loads( product_info.text.replace('\n', ''))
        
        self.img_url = product_info['image'][0]
        self.title   = product_info['name']
        self.price   = product_info['offers']['price']
        available    = True if product_info['offers']['availability'] == 'https://schema.org/InStock' else False
        self.currency = '₸'

        if self.price != 'null':
            try:
                self.price = float(self.price)
            except Exception:
                return False
        return True


class WildberriesRu(BaseJSONParser):
    host = 'www.wildberries.ru'
    # https://www.wildberries.ru/catalog/242981772/detail.aspx
    def create_info(self, nm=''):
        if not nm:
            url_parse = urlparse(self.url)
            nm = url_parse.path.split('/')[-2]

        destination = [123589446, -1257786]

        for dest in destination:
            url = f'https://card.wb.ru/cards/v2/detail?appType=128&curr=kzt&lang=ru&dest={dest}&spp=30&nm={nm}'
            if super().create_info(url=url, nm=nm):
                return True
        return False


    def scraping_info(self, data, *args, **kwargs):
        nm = kwargs.get('nm')
        if len(nm) == 8:
            vol = nm[:3]
            part = nm[:5]
        if len(nm) == 9:
            vol = nm[:4]
            part = nm[:6]

        vol = int(vol)
        part = int(part)

        response = self.get_response('https://cdn.wbbasket.ru/api/v3/upstreams?schema=https')
        if response is None:
            return False
        try:
            json = response.json()
        except Exception:
            return False
        
        hosts = json['origin']['mediabasket_route_map'][0]['hosts']

        j = next(
            (host for host in hosts if host["vol_range_from"] <= vol <= host["vol_range_to"]),
            None)

        # https://basket-17.wbbasket.ru/vol2831/part283118/283118104/images/big/2.webp
        self.img_url = f'{j["host"]}/vol{vol}/part{part}/{nm}/images/big/1.webp'
        
        try:
            self.title   = data['data']['products'][0]['name']
            self.price   = data['data']['products'][0]['sizes'][0]['price']['total']/100
            self.currency = '₸'
        except Exception:
            return False
        return True


class GlobalWildberriesRu(WildberriesRu):
    host = 'global.wildberries.ru'
    # https://global.wildberries.ru/product/noutbuk-igrovoj-thin-a15-b7uc-405xru-9s7-16rk11-405-283118104?option=433985712
    # https://card.wb.ru/cards/v2/detail?appType=128&curr=kzt&lang=ru&dest=123589446&spp=30&nm=283118104

    def create_info(self):
        url_parse = urlparse(self.url)
        nm = url_parse.path.split('-')[-1]

        return super().create_info(nm=nm)


class OlxKz(BaseSoupParser):
    host = 'www.olx.kz'

    def scraping_info(self, data: BeautifulSoup) -> bool:
        if not data:
            return False

        el = data.find(id='olx-init-config')
        l = el.text.strip().split('\n')
        l = list(map(str.strip, l))
        t = l[3].strip()[31:-2]
        k = ast.literal_eval(f"'{t}'")

        j = json.loads(k)

        try:
            if j['ad']:
                self.title = j['ad']['ad']['title']
                isActive = j['ad']['ad']['isActive']
                status = j['ad']['ad']['status']
                self.price = j['ad']['ad']['price']['regularPrice']['value']
                self.img_url = j['ad']['ad']['photos'][0]
                self.currency = j['ad']['ad']['price']['regularPrice']['currencySymbol']
            else:
                self.price = None
                # self.archive = True
        except Exception:
            return False
        return True


class AlserKz(BaseJSONParser):
    host = 'alser.kz'
    
    #https://alser.kz/p/rb33a32n0elwtholodilnik-samsung
    def get_response(self, url=''):
        keyword = self.url.split('/')[-1]
        url = f'https://alser.kz/api/v2/product-detail?keyword={keyword}'
        response = super().get_response(url=url)
        return response

    def scraping_info(self, data: Any = None) -> bool:
        if not data.get('message') == 'mobapi':
            return False
        if not data.get('data', {}):
            return False

        data = data.get('data')

        self.title = data.get('title')
        self.img_url = data.get('photos')[0]

        self.in_stock = int(data.get('shops_count', 0)) > 0
        try:
            self.price = float(data.get('price'))
        except Exception:
            self.price = None

        return True


class ObyavleniyaKaspiKz(BaseSoupParser):
    host = 'obyavleniya.kaspi.kz'

    def scraping_info(self, data: BeautifulSoup) -> bool:

        #el_img_url = data.find(name='picture', class_='slider__picture')
       # el_img_url = el_img_url.find(name='source', type='image/jpeg')

        el_img_url = data.xpath('//*[@id="splide01-slide01"]/picture')

        self.img_url = el_img_url.attrs['srcset'].split(',')[0][:-3]

        title = data.find(name='h1', class_='header__title').string
        self.title = title.strip()
        price = data.find(name='p', class_='price__text').string
        price = re.sub(r'\s+', '', price, flags=re.UNICODE)[:-1]

        self.currency = '₸'

        if price:
            try:
                self.price = float(price)
            except Exception:
                return False
        return True


class KaspiKz(BaseJSONParser):
    host = 'kaspi.kz'

    def get_response(self, url=''):
        response = super().get_response()
        soup = BeautifulSoup(response.text, 'lxml')

        el_img_url = soup.find(name='link', rel='image_src')
        self.img_url = el_img_url.attrs['href']

        el_title = soup.find(name='title')

        start = el_title.text.find("Купить") + len("Купить")
        end = el_title.text.find("в кредит")

        self.title = el_title.text[start:end].strip()

        url_parse = urlparse(self.url)

        id = url_parse.path.split('-')[-1][:-1]
        query = parse_qs(url_parse.query)

        url = f'https://kaspi.kz/yml/offer-view/offers/{id}'
        payload = {
            'cityId': query['c'][0],
            'limit': 1,
            'page': 0,
            'sort': 'true'
        }

        headers = {
            "Content-Type": "application/json; charset=UTF-8",
            "Referer":
                f'{url_parse.scheme}://{url_parse.hostname}{url_parse.path}'
        }

        response = super().get_response(url=url, method='post', json=payload,
                                        headers=headers)

        return response

    def scraping_info(self, data: Any = None) -> bool:
        if data['offersCount'] == 0:
            self.price = None
            return True

        offer = data['offers'][0]
        self.price = offer['price']
        self.currency = '₸'

        return True


class KolesaKz(BaseJSONParser):
    host = 'kolesa.kz'

    def get_response(self, url=''):
        id = self.url.split('/')[-1]
        url = f'https://kolesa.kz/a/average-price/{id}'
        for _ in range(2):
            user_agent = random.choice(user_agents)
            headers = {
                'User-Agent': user_agent,
                'Content-type': 'application/text; charset=utf-8',
                }
            request = requests
            try:
                response = request.get(
                    url=url, headers=headers, timeout=(5, 5))
                if response.status_code in [200, 404]:
                    return response
            except ConnectTimeout:
                time.sleep(1)
            except ReadTimeout:
                time.sleep(1)
            except Exception:
                time.sleep(1)
        return None

    def scraping_info(self, data: Any = None) -> bool:
        if data.get('message', '') == 'Not Found':
            self.archive = True
            return True

        try:
            img_url = data['data']['photoUrl'].split('/')
            img_url[-1] = '1-750x470.jpg'

            self.img_url = '/'.join(img_url)
            self.title   = data['data']['name']
            self.price   = data['data']['currentPrice'] * 1.0
            self.currency = '₸'
        except Exception:
            return False
        return True


class KrishaKz(BaseSoupParser):
    host = 'krisha.kz'

    def scraping_info(self, data: BeautifulSoup) -> bool:
        product_info = data.select('#jsdata')[0].text[23:-6]
        product_info = json.loads(product_info)
        
        self.img_url  = product_info['advert']['photos'][0]['src']
        self.title    = product_info['advert']['title']
        self.currency = '₸'
        status        = product_info['advert']['status']
        has_price     = product_info['advert']['hasPrice']
        if has_price:
            self.price = product_info['advert']['price']

        if self.price != 'null':
            try:
                self.price = float(self.price)
            except Exception:
                return False
        return True


class Parsers():
    def __init__(self, url: str = None) -> None:
        if url:
            self.url = url
            host = urlparse(url).hostname
            self.parser = self.get_parser(host=host)
            pass

    def get_price(self):
        info = self.parser(url=self.url).get_info()
        return info.price

    def find_host_in_subclasses(self, klass, host):
        if getattr(klass, 'host', '') == host:
            return klass
        for sub in klass.__subclasses__():
            subsub = self.find_host_in_subclasses(sub, host)
            if subsub:
                return subsub
        return None

    def get_parser(self, host: str) -> BaseParser | None:
        return self.find_host_in_subclasses(BaseParser, host)


if __name__ == '__main__':
    pass
