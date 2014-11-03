"""
This is a setup.py script generated by py2applet

Usage:
    python setup.py py2app
"""

from setuptools import setup

APP = ['metatoneLiveLoggingProcessor.py']
DATA_FILES = ['2013-07-01-TrainingData-classifier.p']
OPTIONS = {'argv_emulation': True,
 'iconfile': 'metatone.icns',
 'includes':'sklearn.utils.lgamma',
 'plist': {'CFBundleName': 'MetatoneClassifier',
 	'CFBundleShortVersionString':'0.1.0',
 	'CFBundleVersion': '0.1.0',
 	'CFBundleIdentifier':'au.com.charlesmartin.MetatoneClassifier',
 	'NSHumanReadableCopyright': 'Copyright 2014 Charles Martin',
 	'CFBundleDevelopmentRegion': 'English',
 	}
 }

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
