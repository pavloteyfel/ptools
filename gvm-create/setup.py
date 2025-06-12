from setuptools import setup

setup(
    name='gvm-create',
    version='1.0',
    py_modules=['gvm-create'],
    install_requires=[],
    entry_points={
        'console_scripts': [
            'gvm-cteate = gvm-create:main',
        ],
    },
)
