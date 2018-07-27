import sys

# Make sure we are running python3.5+
if 10 * sys.version_info[0]  + sys.version_info[1] < 35:
    sys.exit("Sorry, only Python 3.5+ is supported.")

from setuptools import setup

def readme():
    with open('README.rst') as f:
        return f.read()

setup(
      name             =   'pfdicom_tagExtract',
      version          =   '2.0.2',
      description      =   'Extract DICOM header info -- part of the pf* family.',
      long_description =   readme(),
      author           =   'FNNDSC',
      author_email     =   'dev@babymri.org',
      url              =   'https://github.com/FNNDSC/pfdicom_tagExtract',
      packages         =   ['pfdicom_tagExtract'],
      install_requires =   ['pfdicom', 'matplotlib'],
      #test_suite       =   'nose.collector',
      #tests_require    =   ['nose'],
      scripts          =   ['bin/pfdicom_tagExtract'],
      license          =   'MIT',
      zip_safe         =   False
)
