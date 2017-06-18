#!/usr/bin/python
# vim: noet sw=4 ts=4 filetype=python

try:
    from setuptools     import setup
    print 'Found setuptools, eggs may be hatched.'
except:
    from distutils.core import setup
    print 'Revered to distutils, only usual suspects possible.'

version = '2.0.2'

with open( 'asl/version.py', 'wt' ) as f:
    print >>f, "Version = '{0}'".format( version )

setup(
    name                 = 'asl',
    version              = version,
    description          = "Prettyprinter for OVM AdminServer.log files",
    long_description     = open('README.md').read(),
    keywords             = 'oracle vm adminserver.log prettyprinter',
    author               = 'Tommy Reynolds',
    author_email         = 'Oldest.Software.Guy@gmail.com',
    url                  = 'http://www.megacoder.com',
    license              = 'MIT',
    include_package_data = True,
    zip_safe             = False,
    install_requires     = [],
    packages             = [ 'asl' ],
    entry_points         = {
        'console_scripts' : [
            'asl=asl:main'
        ],
    },
    scripts              = [ 'bin/asl' ]
)
