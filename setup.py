"""ImportLite setup module.
Based on the example at https://github.com/pypa/sampleproject.
"""

from setuptools import setup
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

    setup(
        name='importlite',
        version='0.1.0',
        description='Import CSV files into SQLite databases',
        url='https://github.com/KatrinaE/importlite',
        author='Katrina Ellison Geltman',
        author_email='katrina.m.ellison@gmail.com',
        license='MIT',
        classifiers=[
            'Development Status :: 3 - Alpha',
            'Intended Audience :: Developers',
            'Topic :: Database',
            'License :: OSI Approved :: MIT License',
            'Programming Language :: Python :: 2.7',
            'Programming Language :: Python :: 3.2',
            'Programming Language :: Python :: 3.3',
            'Programming Language :: Python :: 3.4',
            'Programming Language :: Python :: 3.5'
        ],
        keywords='csv sqlite',
        packages=['importlite'],
        entry_points={
            'console_scripts': [
                'importlite=importlite.__main__:main',
            ]
        }
)
