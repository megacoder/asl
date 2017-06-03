from setuptools import setup, find_packages
import sys, os

version = '1.1.3'

setup(name='asl',
      version=version,
      description="Prettyprinter for Oracle VM AdminServer.log files",
      long_description="""\
good""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='oracle vm adminserver.log prettyprinter',
      author='Tommy Reynolds',
      author_email='Oldest.Software.Guy@gmail.com',
      url='http://www.megacoder.com',
      license='MIT',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
