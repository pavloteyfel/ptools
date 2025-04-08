from setuptools import setup

setup(
    name='nmap_parse',
    version='1.0',
    py_modules=['nmap_parse'],
    install_requires=[],
    entry_points={
        'console_scripts': [
            'nmap_parse = nmap_parse:main',
        ],
    },
)
