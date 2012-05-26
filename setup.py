from setuptools import setup, find_packages

setup(
    name='jmbo-registration',
    version='0.0.2',
    description='Registration for Jmbo.',
    long_description = open('README.md', 'r').read() + open('AUTHORS.rst', 'r').read() + open('CHANGELOG.rst', 'r').read(),
    author='Unomena',
    author_email='dev@unomena.com',
    license='BSD',
    url='http://github.com/unomena/jmbo-registration',
    packages = find_packages(),
    install_requires = [
        'jmbo-foundry',
    ],
    include_package_data=True,
    tests_require=[
        'django-setuptest',
        'panomena-mobile==0.0.7',
    ],
    test_suite="setuptest.SetupTestSuite",
    classifiers=[
        "Programming Language :: Python",
        "License :: OSI Approved :: BSD License",
        "Development Status :: 4 - Beta",
        "Operating System :: OS Independent",
        "Framework :: Django",
        "Intended Audience :: Developers",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
    ],
    zip_safe=False,
)