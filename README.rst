Cleanweb
========

.. image:: https://travis-ci.org/coagulant/cleanweb.png?branch=master
    :target: https://travis-ci.org/coagulant/cleanweb

.. image:: https://coveralls.io/repos/coagulant/cleanweb/badge.png?branch=master
    :target: https://coveralls.io/r/coagulant/cleanweb

Python wrapper for cleanweb API of Yandex to fight spam.

`Yandex.Clean Web`_ helps against spam in text message in comments, on forums, etc.
It detects spam messages based on their content and offers API for graphic CAPTCHA.
Technlogies that power Yandex.Mail spam defence are behind Yandex.Clean Web.

.. _Yandex.Clean Web: http://api.yandex.ru/cleanweb/

Install
-------
* Install via pip::

    pip install cleanweb

* If you understand and accept `licence agreement`_ you need to `Obtain mandatory API key`_ (yandex login is required)

API is provided as is

.. _licence agreement: http://legal.yandex.ru/cleanweb_api/
.. _Obtain mandatory API key: http://api.yandex.ru/cleanweb/form.xml

Usage
-----
Examples show basic usage of cleanweb api, for details check sources and `docs`_::

    >> from cleanweb import Cleanweb
    >> client = Cleanweb(key='cw.1.1.fc4c0c5c3be05adb04c9400214T193305Z')

* check if message contains spam::

    >> client.check_spam(body='This might be some spam message')
    {'id': '036151771200000F', 'links': [], 'spam_flag': False}

* get captcha to show bots::

    >> client.get_captcha()
    {'captcha': '20_iC0ZHRYtEllRhgEAngpsenpKGCIyi',
     'url': 'http://i.captcha.yandex.net/image?key=20_iC0ZHRYtEllRhgEAngpsenpKGCIyi'}

.. image:: http://habrastorage.org/storage2/1a3/fda/5f4/1a3fda5f431fe7be4ed116220d383d40.png

* check captcha::

    >> client.check_captcha(captcha='20_iC0ZHRYtEllRhgEAngpsenpKGCIyi', value='48151632')
    True

* complain on spam detector::

    >> client.complain(id='036151771200000F', is_spam=False)
    True

.. _docs: http://api.yandex.ru/cleanweb/doc/dg/concepts/resources.xml

