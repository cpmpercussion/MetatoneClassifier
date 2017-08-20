# Metatone Classifier

Python software for tracking musical performances on iPads with Charles Martin's Metatone apps. 

[![DOI](https://zenodo.org/badge/20166/cpmpercussion/MetatoneClassifier.svg)](https://zenodo.org/badge/latestdoi/20166/cpmpercussion/MetatoneClassifier)

## Installing

You probably already have python on your system, but on OS X, I use homebrew to get a better version. After [installing Homebrew](), I run:

    brew install python

Then I would install some Python packages:
    
    pip install pandas scikit-learn scipy matplotlib tornado
    pip install -e git+https://github.com/Eichhoernchen/pybonjour.git#egg=pybonjour
    pip install -U https://storage.googleapis.com/tensorflow/mac/cpu/tensorflow-1.1.0-py2-none-any.whl

## Building

For performing:

    cd web-classifier
    python metatone-server.py

For debug:

    cd MetatoneClassifier/classifier
    python setup.app py2app -A
    dist/MetatoneClassifier.app/Contents/MacOS/MetatoneClassifier

For packaging:

    cd MetatoneClassifier/classifier
    python setup.app py2app
    open dist/MetatoneClassifier.app

After the performance, you can check the logs in the "classifier/logs" directory.

## Important Folders:

- *classifier-creator*: given an input of gesture frames matched with target gestures, this script trains a Random Forest Classifier and saves it as a pickled Python object for the classifier software to run.
- *classifier*: Performance server software for real-time classification of Metatone app performances.
- *converters*: scripts to convert logs from one style to another and generate CSV files from general logs.
- *generative-classifier*: A "fake" version of the MetatoneClassifier using a generative model for gestures instead of the performer's actions. This is used as a control in performance studies.
- *modules*: Python modules for the project. Including an updated version of OSC.py.
- *visualisation*: Processing scripts for creating videos of the touch logs
- *web-classifier*: A web-based version of the classifier software using websockets.
