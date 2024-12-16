import unittest

from .parsers import (
    Sulpak,
    Technodom,
    ShopKz,
    WildberriesKz,
    WildberriesKzAspx,
    GlobalWildberriesRu,
    OlxKz,
    Parsers,
    Info,
    AlserKz,
    ObyavleniyaKaspiKz,
    KaspiKz,
    KolesaKz,
    KrishaKz,
)


class Test_TestParsers(unittest.TestCase):
    def setUp(self):
        pass

    def test_get_parser(self):
        host = 'www.sulpak.kz'
        parser = Parsers().get_parser(host=host)
        self.assertIs(parser, Sulpak)


class Test_TestSulpak(unittest.TestCase):

    def test_get_info(self):
        url = 'https://www.sulpak.kz/g/strujniyj_mfu_epson_l3101'
        info = Sulpak(url=url).get_info()

        self.assertIsInstance(info, Info)


class Test_TestTechnodom(unittest.TestCase):

    def test_get_info(self):
        url = 'https://www.technodom.kz/uralsk/p/smartfon-gsm-samsung-galaxy-a13-64gb-black-258737?recommended_by=dynamic&recommended_code=z9wxnh4hkr'
        url = 'https://www.technodom.kz/p/noutbuk-156-neo-55257u-8-256-w-wh15u-i5-v1-226869?recommended_by=dynamic&recommended_code=z9wxnh4hkr'
        url = 'https://www.technodom.kz/p/televizor-samsung-50-ue50au7100uxce-led-uhd-smart-titan-gray-242364?recommended_by=dynamic&recommended_code=z9wxnh4hkr'

        info = Technodom(url=url).get_info()

        self.assertIsInstance(info, Info)


class Test_TestShopKz(unittest.TestCase):

    def test_get_info(self):
        url = 'https://shop.kz/offer/vneshniy-zhestkiy-disk-1000gb-2-5-apacer-ac233-black/'
        info = ShopKz(url=url).get_info()

        self.assertIsInstance(info, Info)


class Test_TestWildberriesKz(unittest.TestCase):

    def test_get_info(self):
        url = 'https://kz.wildberries.ru/product?card=10330269&category=303'
        url = 'https://kz.wildberries.ru/product?card=17094328'
        url = 'https://kz.wildberries.ru/product?card=114629100'

        info = WildberriesKz(url=url).get_info()

        self.assertIsInstance(info, Info)


class Test_TestWildberriesKzAspx(unittest.TestCase):

    def test_get_info(self):
        url = 'https://kz.wildberries.ru/catalog/55919141/detail.aspx'

        info = WildberriesKzAspx(url=url).get_info()

        self.assertIsInstance(info, Info)


class Test_TestGlobalWildberriesRu(unittest.TestCase):

    def test_get_info(self):
        url = 'https://global.wildberries.ru/product/noutbuk-igrovoj-thin-a15-b7uc-405xru-9s7-16rk11-405-283118104?option=433985712'

        info = GlobalWildberriesRu(url=url).get_info()

        self.assertIsInstance(info, Info)



class Test_TestOlxKz(unittest.TestCase):

    def test_get_info(self):
        url = 'https://www.olx.kz/d/obyavlenie/zotac-rtx-3060-12gb-obmen-IDndt4w.html'
        # url = 'https://www.olx.kz/d/obyavlenie/prodam-iphone-11-black-64gb-IDndjPM.html'  # archive
        url = 'https://www.olx.kz/d/obyavlenie/videokarty-3060-rtx-na-garantii-IDn7bhE.html'
        # url = 'https://www.olx.kz/d/obyavlenie/zotac-rtx-3060-12gb-obmen-IDndt4w.html'  # archive
        url = 'https://www.olx.kz/d/obyavlenie/k162-planshet-samsung-tab-s7-128gb-89944-IDn7oDY.html?reason=seller_listing%7Colx_shop_basic'
        info = OlxKz(url=url).get_info()

        self.assertIsInstance(info, Info)


class Test_TestAlserKz(unittest.TestCase):

    def test_get_info(self):
        url = 'https://alser.kz/p/rb33a32n0elwtholodilnik-samsung'
        info = AlserKz(url=url).get_info()

        self.assertIsInstance(info, Info)


class Test_ObyavleniyaKaspiKz(unittest.TestCase):

    def test_get_info(self):
        url = 'https://market.kz/a/prodam-sistemnyiy-blok-109093743/'
        info = ObyavleniyaKaspiKz(url=url).get_info()

        self.assertIsInstance(info, Info)


class Test_KaspiKz(unittest.TestCase):

    def test_get_info(self):
        url = 'https://kaspi.kz/shop/p/giant-xtc-jr-20-2022-seryi-103688219/?c=750000000#!/item'
        url = 'https://kaspi.kz/shop/p/kingston-dtx-64-gb-100759959/?c=750000000&ref=shared_link'
        info = KaspiKz(url=url).get_info()

        self.assertIsInstance(info, Info)


class Test_TestKolesaKz(unittest.TestCase):

    def test_get_info(self):
        # url = 'https://kolesa.kz/a/show/138930595'
        url = 'https://kolesa.kz/a/show/145558514'
        info = KolesaKz(url=url).get_info()

        self.assertIsInstance(info, Info)


class Test_TestKrishaKz(unittest.TestCase):

    def test_get_info(self):
        url = 'https://krisha.kz/a/show/680055827'
        info = KrishaKz(url=url).get_info()

        self.assertIsInstance(info, Info)


if __name__ == '__main__':
    unittest.main()
