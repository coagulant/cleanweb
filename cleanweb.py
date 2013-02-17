# coding: utf-8
import requests
import xml.etree.ElementTree as ET


class CleanwebError(Exception):
    pass


class Cleanweb(object):
    """ Python wrapper for Clean Web project by Yandex

        http://api.yandex.ru/cleanweb
    """

    def __init__(self, key=None):
        if not key:
            raise CleanwebError('Cleanweb needs API key to operate. Get it here: http://api.yandex.ru/cleanweb/form.xml')
        self.session = requests.Session()
        self.session.params['key'] = key

    def request(self, *args, **kwargs):
        """ Error handling in requests
            http://api.yandex.ru/cleanweb/doc/dg/concepts/error-codes.xml
        """
        r = self.session.request(*args, **kwargs)
        if r.status_code != requests.codes.ok:
            error = ET.fromstring(r.content)
            message = error.findtext('message')
            code = error.attrib['key']
            raise CleanwebError('%s (%s)' % (message, code))
        return r

    def check_spam(self, ip=None, email=None, name=None, login=None, realname=None,
                   subject=None, body=None, subject_type='plain', body_type='plain'):
        """ http://api.yandex.ru/cleanweb/doc/dg/concepts/check-spam.xml
            subject_type = plain|html|bbcode
            body_type = plain|html|bbcode
        """
        data = {'ip': ip, 'email': email, 'name': name, 'login': login, 'realname': realname,
                'body-%s' % body_type: body, 'subject-%s' % subject_type: subject}
        r = self.request('post', 'http://cleanweb-api.yandex.ru/1.0/check-spam', data=data)
        root = ET.fromstring(r.content)
        return {
            'id': root.findtext('id'),
            'spam_flag': yesnobool(root.find('text').attrib['spam-flag']),
            'links': [(link.attrib['href'], yesnobool(link.attrib['spam-flag'])) for link in root.findall('./links/link')]
        }

    def get_captcha(self, id=None):
        """ http://api.yandex.ru/cleanweb/doc/dg/concepts/get-captcha.xml"""
        payload = {'id': id}
        r = self.request('get', 'http://cleanweb-api.yandex.ru/1.0/get-captcha', params=payload)
        return dict((item.tag, item.text) for item in ET.fromstring(r.content))

    def check_captcha(self, captcha, value, id=None):
        """ http://api.yandex.ru/cleanweb/doc/dg/concepts/check-captcha.xml"""
        payload = {'captcha': captcha,
                   'value': value,
                   'id': id}
        r = self.request('get', 'http://cleanweb-api.yandex.ru/1.0/check-captcha', params=payload)
        root = ET.fromstring(r.content)
        if root.findall('ok'):
            return True
        if root.findall('failed'):
            return False

    def complain(self, id, is_spam):
        """ http://api.yandex.ru/cleanweb/doc/dg/concepts/complain.xml"""
        r = self.request('post', 'http://cleanweb-api.yandex.ru/1.0/complain',
                         data={'id': id, 'spamtype': 'spam' if is_spam else 'ham'})
        return True


def yesnobool(string):
    if string == 'yes':
        return True
    if string == 'no':
        return False