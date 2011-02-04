import os
import sys
from distutils.core import setup
from invitation import __version__, __maintainer__, __email__


def compile_translations():
    try:
        from django.core.management.commands.compilemessages \
                                                       import compile_messages
    except ImportError:
        return None
    curdir = os.getcwdu()
    os.chdir(os.path.join(os.path.dirname(__file__), 'invitation'))
    try:
        compile_messages(stderr=sys.stderr)
    except TypeError:
        # compile_messages doesn't accept stderr parameter prior to 1.2.4
        compile_messages()
    os.chdir(curdir)
compile_translations()


license_text = open('LICENSE.txt').read()
long_description = open('README.rst').read()


setup(
    name = 'django-inviting',
    version = __version__,
    url = 'http://github.com/muhuk/django-inviting',
    author = __maintainer__,
    author_email = __email__,
    license = license_text,
    packages = ['invitation',
                'invitation.tests',
                'invitation.templatetags'],
    package_data= {
        'invitation': ['templates/admin/invitation/invitationstats/*',
                       'tests/templates/invitations/*',
                       'tests/templates/registration/*',
                       'locale/*/LC_MESSAGES/django.*']
    },
    data_files=[('', ['LICENSE.txt',
                      'README.rst'])],
    description = 'Registration through invitations',
    long_description=long_description,
    classifiers = ['Development Status :: 5 - Production/Stable',
                   'Environment :: Web Environment',
                   'Framework :: Django',
                   'Intended Audience :: Developers',
                   'License :: OSI Approved :: BSD License',
                   'Topic :: Internet :: WWW/HTTP :: Dynamic Content']
)
