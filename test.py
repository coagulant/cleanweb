# coding: utf-8
from __future__ import unicode_literals
from unittest import TestCase
import sure
from httpretty import HTTPretty, PY3, parse_qs
from cleanweb import Cleanweb, CleanwebError


class HttprettyCase(TestCase):

    def setUp(self):
        HTTPretty.reset()
        HTTPretty.enable()

    def tearDown(self):
        HTTPretty.disable()

    def assertBodyQueryString(self, **kwargs):
        """ Hakish, but works %("""
        if PY3:
            qs = parse_qs(HTTPretty.last_request.body.decode('utf-8'))
        else:
            qs = dict((key, [values[0].decode('utf-8')]) for key, values in parse_qs(HTTPretty.last_request.body).items())
        kwargs.should.be.equal(qs)


class Api(HttprettyCase):

    def test_raises_exception_when_instantiated_with_no_key(self):
        Cleanweb.when.called_with().should.throw(CleanwebError,
            "Cleanweb needs API key to operate. Get it here: http://api.yandex.ru/cleanweb/form.xml")

    def test_xml_error_is_handled(self):
        error_repsonse = """
        <!DOCTYPE get-captcha-result PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
        <error key="key-not-registered"><message>Provided API key not registered</message></error>"""
        HTTPretty.register_uri(HTTPretty.GET, "http://cleanweb-api.yandex.ru/1.0/get-captcha", body=error_repsonse,
                               status=403)
        Cleanweb(key='xxx').get_captcha.when.called_with().should.throw(CleanwebError,
            'Provided API key not registered (key-not-registered)')


class CheckSpam(HttprettyCase):

    def setUp(self):
        super(CheckSpam, self).setUp()
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

    def test_is_not_spam(self):
        HTTPretty.register_uri(HTTPretty.POST, "http://cleanweb-api.yandex.ru/1.0/check-spam",
                               body=self.ham_response)
        Cleanweb(key='yyy').check_spam(body='Питон').should.be.equal({
            'id': '123456789abcd',
            'spam_flag': False,
            'links': []
        })
        HTTPretty.last_request.method.should.be.equal("POST")
        self.assertBodyQueryString(**{'body-plain': ['Питон']})
        HTTPretty.last_request.should.have.property('querystring').being.equal({
            'key': ['yyy'],
        })

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
        self.assertBodyQueryString(**{'ip': ['10.178.33.2'], 'body-html': ['123'],
                                      'subject-plain': [spam_text], 'name': ['Vasia']})
        HTTPretty.last_request.should.have.property('querystring').being.equal({
            'key': ['yyy'],
        })


class GetCaptcha(HttprettyCase):

    def setUp(self):
        super(GetCaptcha, self).setUp()
        self.valid_response = """
        <!DOCTYPE get-captcha-result PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
        <get-captcha-result>
            <captcha>abcd12345</captcha>
            <url>http://i.captcha.yandex.net/image?key=abcd12345</url>
        </get-captcha-result>
        """

    def test_can_be_obtained_without_msg_id(self):
        HTTPretty.register_uri(HTTPretty.GET, "http://cleanweb-api.yandex.ru/1.0/get-captcha",
                               body=self.valid_response)
        Cleanweb(key='xxx').get_captcha().should.be.equal(
            {'captcha': 'abcd12345',
             'url': 'http://i.captcha.yandex.net/image?key=abcd12345'})
        HTTPretty.last_request.should.have.property("querystring").being.equal({
            "key": ["xxx"],
        })

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


class CheckCaptcha(HttprettyCase):

    def setUp(self):
        super(CheckCaptcha, self).setUp()
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


class Complain(HttprettyCase):

    def setUp(self):
        super(Complain, self).setUp()
        self.valid_response = """
        <complain-result>
        <ok/>
        </complain-result>"""

    def test_spam_is_ham(self):
        HTTPretty.register_uri(HTTPretty.POST,
                               "http://cleanweb-api.yandex.ru/1.0/complain",
                               body=self.valid_response)
        Cleanweb(key='zzz').complain(id='somekindofmsgid', is_spam=True)
        self.assertBodyQueryString(spamtype=['spam'], id=['somekindofmsgid'])

    def test_spam_is_spam(self):
        HTTPretty.register_uri(HTTPretty.POST,
                               "http://cleanweb-api.yandex.ru/1.0/complain",
                               body=self.valid_response)
        Cleanweb(key='zzz').complain(id='somekindofmsgid', is_spam=False)
        self.assertBodyQueryString(spamtype=['ham'], id=['somekindofmsgid'])