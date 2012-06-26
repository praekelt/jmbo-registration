from setuptools import setup, find_packages

setup(
    name='jmbo-registration',
    version='0.0.11',
    description='Registration for Jmbo.',
    long_description = open('README.md', 'r').read() + open('AUTHORS.rst', 'r').read() + open('CHANGELOG.rst', 'r').read(),
    author='Unomena',
    author_email='dev@unomena.com',
    license='BSD',
    url='http://github.com/unomena/jmbo-registration',
    packages = find_packages(),
    install_requires = [
        'jmbo-foundry',
        'jmbo-friends',
    ],
    include_package_data=True,
    tests_require=[
        'django-setuptest',
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
