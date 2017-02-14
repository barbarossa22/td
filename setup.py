import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'requirements.txt')) as requirements:
    requires = [i.strip() for i in requirements.readlines()]
with open(os.path.join(here, 'test_requirements.txt')) as test_requirements:
    tests_require = [i.strip() for i in test_requirements.readlines()]

setup(name='td',
      version='0.0',
      description='td',
      classifiers=[
          "Programming Language :: Python",
          "Framework :: Pyramid",
          "Topic :: Internet :: WWW/HTTP",
          "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
      ],
      author='',
      author_email='',
      url='',
      keywords='web pyramid pylons',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      install_requires=requires,
      extras_require={
          'testing': tests_require,
      },
      entry_points="""\
      [paste.app_factory]
      main = td:main
      """,
      )
