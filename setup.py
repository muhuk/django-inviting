from distutils.core import setup
from invitation import __version__, __maintainer__, __email__


setup(
    name = 'django-inviting',
    version = __version__,
    url = 'http://github.com/muhuk/django-inviting',
    author = __maintainer__.encode('utf8'),
    author_email = __email__,
    license = open('LICENSE.txt').read(),
    packages = ['invitation',
                'invitation.templatetags'],
    package_data= {'invitation': ['templates/*',
                                  'locale/*/LC_MESSAGES/django.po']},
    data_files=[('', ['LICENSE.txt',
                      'README.rst'])],
    description = 'Registration through invitations',
    long_description=open('README.rst').read(),
    classifiers = ['Development Status :: 5 - Production/Stable',
                   'Environment :: Web Environment',
                   'Framework :: Django',
                   'Intended Audience :: Developers',
                   'License :: OSI Approved :: BSD License',
                   'Topic :: Internet :: WWW/HTTP :: Dynamic Content']
)
