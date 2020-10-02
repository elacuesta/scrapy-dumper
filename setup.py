from setuptools import setup


setup(
    name='scrapy_dumper',
    version='0.1.0',
    description='Simple Scrapy extension to dump requests and responses',
    author='Eugenio Lacuesta',
    author_email='eugenio.lacuesta@gmail.com',
    license='BSD',
    packages=['scrapy_dumper'],
    install_requires=[
        'scrapy>=1.0',
    ],
)
