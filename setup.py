# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup(
    name='commonmark_to_text',
    version='0.0.2',
    author=u'Joshua Tauberer',
    author_email=u'jt@occams.info',
    packages = find_packages(),
    py_modules = ['CommonMarkPlainText'],
    url='https://github.com/JoshData/commonmark-py-plaintext',
    license='CC0 (copyright waived)',
    description='A CommonMark renderer that outputs pretty plain text or compliant CommonMark.',
    long_description=open("README.rst").read(),
    keywords = "commonmark plain text",
    install_requires=["CommonMark==0.7.4"],
)
