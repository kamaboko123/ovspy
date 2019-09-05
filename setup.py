from setuptools import setup, find_packages

requires = []

setup(
    name='ovspy',
    version='0.1.0b1',
    description='Open vSwitch Mnipulation Library',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/kamaboko123/ovspy',
    author='kamaboko123',
    author_email='6112062+kamaboko123@users.noreply.github.com',
    license='MIT',
    packages=['ovspy'],
    install_requires=requires,
    classifiers=[
        'Programming Language :: Python :: 3.5',
    ]
)

