try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


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
    install_requires=[
        "ws4py==0.4.2",
        "requests[security]",
        "future",
    ],
    setup_requires=[
        'pytest-runner',
    ],
    tests_require=[
        'pytest',
    ],
)
