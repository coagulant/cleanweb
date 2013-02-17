# coding: utf-8
from __future__ import unicode_literals
import sure
from unittest import TestCase
from httpretty import httprettified, HTTPretty
from cleanweb import Cleanweb, CleanwebError


class Api(TestCase):

    def test_raises_exception_when_instantiated_with_no_key(self):
        Cleanweb.when.called_with().should.throw(CleanwebError,
            "Cleanweb needs API key to operate. Get it here: http://api.yandex.ru/cleanweb/form.xml")

    @httprettified
    def test_xml_error_is_handled(self):
        error_repsonse = """
        <!DOCTYPE get-captcha-result PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
        <error key="key-not-registered"><message>Provided API key not registered</message></error>"""
        HTTPretty.register_uri(HTTPretty.GET, "http://cleanweb-api.yandex.ru/1.0/get-captcha", body=error_repsonse,
                               status=403)
        Cleanweb(key='xxx').get_captcha.when.called_with().should.throw(CleanwebError,
            'Provided API key not registered (key-not-registered)')


class CheckSpam(TestCase):

    def setUp(self):
        self.ham_response = """
        <!DOCTYPE check-spam-result PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
        <check-spam-result>
            <id>123456789abcd</id>
            <text spam-flag="no" />
            <links></links>
        </check-spam-result>"""
        self.spam_response = """
        <!DOCTYPE check-spam-result PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
        <check-spam-result>
            <id>123456789efgh</id>
            <text spam-flag="yes" />
            <links>
                <link href="http://cnn.com" spam-flag="yes" />
                <link href="http://yandex.ru" spam-flag="no" />
            </links>
        </check-spam-result>"""

    @httprettified
    def test_is_not_spam(self):
        HTTPretty.register_uri(HTTPretty.POST, "http://cleanweb-api.yandex.ru/1.0/check-spam",
                               body=self.ham_response)
        Cleanweb(key='yyy').check_spam(body='Питон').should.be.equal({
            'id': '123456789abcd',
            'spam_flag': False,
            'links': []
        })
        HTTPretty.last_request.method.should.be.equal("POST")
        HTTPretty.last_request.body.should.be.equal('body-plain=%D0%9F%D0%B8%D1%82%D0%BE%D0%BD')
        HTTPretty.last_request.should.have.property('querystring').being.equal({
            'key': ['yyy'],
        })

    @httprettified
    def test_is_spam(self):
        HTTPretty.register_uri(HTTPretty.POST, "http://cleanweb-api.yandex.ru/1.0/check-spam",
                               body=self.spam_response)
        spam_text = 'ШОК! Видео скачать без СМС! http://cnn.com http://yandex.ru'
        Cleanweb(key='yyy').check_spam(subject=spam_text, body='123',
                                       ip='10.178.33.2', name='Vasia', body_type='html').should.be.equal({
            'id': '123456789efgh',
            'spam_flag': True,
            'links': [('http://cnn.com', True), ('http://yandex.ru', False)]
        })
        HTTPretty.last_request.method.should.be.equal("POST")
        HTTPretty.last_request.body.should.be.equal('ip=10.178.33.2&body-html=123&subject-plain=%D0%A8%D0%9E%D0%9A%21+%D0%92%D0%B8%D0%B4%D0%B5%D0%BE+%D1%81%D0%BA%D0%B0%D1%87%D0%B0%D1%82%D1%8C+%D0%B1%D0%B5%D0%B7+%D0%A1%D0%9C%D0%A1%21+http%3A%2F%2Fcnn.com+http%3A%2F%2Fyandex.ru&name=Vasia')
        HTTPretty.last_request.should.have.property('querystring').being.equal({
            'key': ['yyy'],
        })


class GetCaptcha(TestCase):

    def setUp(self):
        self.valid_response = """
        <!DOCTYPE get-captcha-result PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
        <get-captcha-result>
            <captcha>abcd12345</captcha>
            <url>http://i.captcha.yandex.net/image?key=abcd12345</url>
        </get-captcha-result>
        """

    @httprettified
    def test_can_be_obtained_without_msg_id(self):
        HTTPretty.register_uri(HTTPretty.GET, "http://cleanweb-api.yandex.ru/1.0/get-captcha",
                               body=self.valid_response)
        Cleanweb(key='xxx').get_captcha().should.be.equal(
            {'captcha': 'abcd12345',
             'url': 'http://i.captcha.yandex.net/image?key=abcd12345'})
        HTTPretty.last_request.should.have.property("querystring").being.equal({
            "key": ["xxx"],
        })

    @httprettified
    def test_can_be_obtained_with_msg_id(self):
        HTTPretty.register_uri(HTTPretty.GET, "http://cleanweb-api.yandex.ru/1.0/get-captcha",
                               body=self.valid_response)
        Cleanweb(key='xxx').get_captcha(id='somekindofmsgid').should.be.equal(
            {'captcha': 'abcd12345',
             'url': 'http://i.captcha.yandex.net/image?key=abcd12345'})
        HTTPretty.last_request.should.have.property("querystring").being.equal({
            "key": ["xxx"],
            "id": ["somekindofmsgid"]
        })


class CheckCaptcha(TestCase):

    def setUp(self):
        self.valid_response = """
        <!DOCTYPE check-captcha-result PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
        <check-captcha-result>
            <ok />
        </check-captcha-result>
        """
        self.invalid_response = """
        <!DOCTYPE check-captcha-result PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
        <check-captcha-result xmlns:x="http://www.yandex.ru/xscript">
            <failed></failed>
        </check-captcha-result>
        """

    @httprettified
    def test_valid_captcha_no_msg_is_ok(self):
        HTTPretty.register_uri(HTTPretty.GET,
                               "http://cleanweb-api.yandex.ru/1.0/check-captcha",
                               body=self.valid_response)
        Cleanweb(key='xxx').check_captcha(captcha='abcd12345', value='48151632').should.be.true
        HTTPretty.last_request.should.have.property("querystring").being.equal({
            "key": ["xxx"],
            "captcha": ["abcd12345"],
            "value": ["48151632"],
        })

    @httprettified
    def test_valid_captcha_msg_is_ok(self):
        HTTPretty.register_uri(HTTPretty.GET,
                               "http://cleanweb-api.yandex.ru/1.0/check-captcha",
                               body=self.valid_response)
        Cleanweb(key='xxx').check_captcha(id='somekindofmsgid', captcha='abcd12345', value='48151632').should.be.true
        HTTPretty.last_request.should.have.property("querystring").being.equal({
            "key": ["xxx"],
            "captcha": ["abcd12345"],
            "value": ["48151632"],
            "id": ["somekindofmsgid"]
        })

    @httprettified
    def test_invalid_captcha(self):
        HTTPretty.register_uri(HTTPretty.GET,
                               "http://cleanweb-api.yandex.ru/1.0/check-captcha",
                               body=self.invalid_response)
        Cleanweb(key='xxx').check_captcha(id='somekindofmsgid', captcha='abcd12345', value='000').should.be.false
        HTTPretty.last_request.should.have.property("querystring").being.equal({
            "key": ["xxx"],
            "captcha": ["abcd12345"],
            "value": ["000"],
            "id": ["somekindofmsgid"]
        })


class Complain(TestCase):

    def setUp(self):
        self.valid_response = """
        <complain-result>
        <ok/>
        </complain-result>"""

    @httprettified
    def test_spam_is_ham(self):
        HTTPretty.register_uri(HTTPretty.POST,
                               "http://cleanweb-api.yandex.ru/1.0/complain",
                               body=self.valid_response)
        Cleanweb(key='zzz').complain(id='somekindofmsgid', is_spam=True)
        HTTPretty.last_request.body.should.be.equal('spamtype=spam&id=somekindofmsgid')

    @httprettified
    def test_spam_is_spam(self):
        HTTPretty.register_uri(HTTPretty.POST,
                               "http://cleanweb-api.yandex.ru/1.0/complain",
                               body=self.valid_response)
        Cleanweb(key='zzz').complain(id='somekindofmsgid', is_spam=False)
        HTTPretty.last_request.body.should.be.equal('spamtype=ham&id=somekindofmsgid')