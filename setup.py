from setuptools import find_packages
from setuptools import setup

setup(
    name='pydantic-mypy-strict',
    version='1.0.0',
    description='',
    url='',
    author='Yonatan Greenfeld',
    author_email='yonathan@jit.io',
    packages=find_packages(exclude=['tests/*']),
    install_requires=[
        'mypy>=0.900',
    ],
    python_requires='>=3',
)
