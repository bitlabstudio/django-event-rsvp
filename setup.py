import os
from setuptools import setup, find_packages
import event_rsvp


def read(fname):
    try:
        return open(os.path.join(os.path.dirname(__file__), fname)).read()
    except IOError:
        return ''


setup(
    name="django-event-rsvp",
    version=event_rsvp.__version__,
    description=read('DESCRIPTION'),
    long_description=read('README.rst'),
    license='The MIT License',
    platforms=['OS Independent'],
    keywords='django, events, app, rsvp',
    author='Daniel Kaufhold',
    author_email='daniel.kaufhold@bitmazk.com',
    url="https://github.com/bitmazk/django-event-rsvp",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'django>=1.4.3',
        'django-cms>=2.3',
        'django-filer',
        'python-dateutil',
        'South',
    ],
    tests_require=[
        'fabric',
        'factory_boy',
        'django-nose',
        'coverage',
        'django-coverage',
        'mock',
    ],
    test_suite='event_rsvp.tests.runtests.runtests',
)
