from setuptools import setup
from os import path

here = path.abspath(path.dirname(__file__))
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(  name='iitb-login',
        version='0.2.1',
        description='iitb login script with ssh key based credentials encryption',
        long_description=long_description,
        long_description_content_type='text/markdown',
        url='https://github.com/dumbPy/iitb-login',
        author='Sufiyan Adhikari',
        author_email='dumbpyx@gmail.com',
        python_requires='>=3.3.*',
        install_requires=['paramiko', 'scrapy', 'click',
                            'argparse','cryptography' ],
        scripts=['scripts/iitb'],
        # There are no packages, just a login script
        packages=[]
        )
