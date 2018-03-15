# -*- coding: utf-8 -*-

import sys
from setuptools import setup, find_packages
from codecs import open

setup(
	name='commonmarkextensions',
	version='0.0.1',

	description='Tables and plain text rendering for CommonMark-py.',
	long_description=open("README.md", encoding='utf-8').read(),
	url='https://github.com/GovReady/CommonMark-py-Extensions',

	author=u'GovReady PBC',
	author_email=u'',
	license='BSD 3',

	# See https://pypi.python.org/pypi?%3Aaction=list_classifiers
	classifiers=[
		'Intended Audience :: Developers',
		'Topic :: Software Development :: Libraries :: Python Modules',

		'Programming Language :: Python :: 2',
		'Programming Language :: Python :: 2.7',
		'Programming Language :: Python :: 3',
		'Programming Language :: Python :: 3.4',
		'Programming Language :: Python :: 3.5',
		'Programming Language :: Python :: 3.6',
	],

	keywords="markdown commonmark tables plaintext",

	packages=find_packages(),
	install_requires=[
		"CommonMark>=0.7.4,<=0.7.5",
		],

	entry_points={
		'console_scripts': [
		],
	},
)
