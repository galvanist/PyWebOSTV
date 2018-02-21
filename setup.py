try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


with open('requirements.txt') as f:
    requirements = f.read().split()

with open('dev-requirements.txt') as f:
    requirements_dev = f.read().split()

setup(
    name='pywebostv',
    version='0.8.1',
    author='Srivatsan Iyer',
    author_email='supersaiyanmode.rox@gmail.com',
    packages=[
        'pywebostv',
    ],
    license='MIT',
    description='Library to remote control LG Web OS TV',
    long_description=open('README.md').read(),
    install_requires=requirements,
    tests_require=requirements_dev,
    setup_requires=[
        'pytest-runner',
    ],
)
