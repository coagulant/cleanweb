import sys
from os import path
import codecs
from setuptools import setup
from setuptools.command.test import test as TestCommand


read = lambda filepath: codecs.open(filepath, 'r', 'utf-8').read()


class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        #import here, cause outside the eggs aren't loaded
        import pytest
        errno = pytest.main(self.test_args)
        sys.exit(errno)


setup(
    name='cleanweb',
    version='2.1',
    author='Ilya Baryshev',
    author_email='baryshev@gmail.com',
    py_modules=['cleanweb'],
    url='https://github.com/coagulant/cleanweb',
    license='MIT',
    description="Python wrapper for cleanweb API of Yandex to fight spam.",
    long_description=read(path.join(path.dirname(__file__), 'README.rst')),
    install_requires=["requests>=1.0.0"],
    tests_require=['pytest', 'httpretty==0.5.9'],
    cmdclass={'test': PyTest},
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
    ],
)
