# -*- coding:utf-8 -*-
# create_time: 2019/8/6 15:30
# __author__ = 'brad'


from setuptools import setup, find_packages

setup(
    name='django-customflow',
    version='0.1.1',
    description='A custom workflow with Django',
    url='https://github.com/Brad19940809/django-customflow',
    author='Brad',
    author_email='xiaoleluo2@gmail.com',
    maintainer="Brad",
    maintainer_email='xiaoleluo2@gmail.com',
    license="MIT",
    keywords='workflow, django, flow',
    classifiler=[
        'Development Status :: 1 - Planning',
        'Environment :: Web Environment',
        'Framework :: Django',
        'License :: OSI Approved :: MIT License',
        "Intended Audience :: Developers",
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ],
    packages=find_packages(exclude=['example']),
    install_requires=[
        'django'
    ],
)
