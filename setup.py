from setuptools import setup, find_packages
import sys
from setuptools.command.test import test as TestCommand

#https://pytest.org/latest/goodpractises.html
class PyTest(TestCommand):
    user_options = [('pytest-args=', 'a', "Arguments to pass to py.test")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = []

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        #import here, cause outside the eggs aren't loaded
        import pytest
        errno = pytest.main(self.pytest_args)
        sys.exit(errno)

setup(
    name='cellsplit',
    version='0.0.1',
    description='Split fastq from cellranger',
    url='http://github.com/sherrillmix/cellsplit', #doesn't exist
    author='Scott Sherrill-Mix',
    author_email='shescott@upenn.edu',
    license='GPL 3',
    packages=find_packages(),
    zip_safe=True,
    install_requires=[],
    tests_require=['pytest >=2.8'],
    cmdclass = {'test': PyTest},
    entry_points={ 'console_scripts': [
        'cellsplit = cellsplit.cellsplit:main',
        ] },
    classifiers=[
        "Topic :: Scientific/Engineering :: Bio-Informatics",
        'Intended Audience :: Science/Research',
    ],
    package_data={'cellsplit':['barcodes/*.txt*']}, #TODOD is this right?
    #,long_description=open('README.rst').read()
)
