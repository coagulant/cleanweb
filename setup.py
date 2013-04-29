from os import path
import codecs
from setuptools import setup


read = lambda filepath: codecs.open(filepath, 'r', 'utf-8').read()


setup(
    name='cleanweb',
    version='2.0',
    author='Ilya Baryshev',
    author_email='baryshev@gmail.com',
    py_modules=['cleanweb'],
    url='https://github.com/coagulant/cleanweb',
    license='MIT',
    description="Python wrapper for cleanweb API of Yandex to fight spam.",
    long_description=read(path.join(path.dirname(__file__), 'README.rst')),
    install_requires=["requests>=1.0.0",],
    tests_require=['nose', 'httpretty>=0.5.9', 'sure'],
    test_suite = "nose.collector",
    classifiers = [
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
    ],
)