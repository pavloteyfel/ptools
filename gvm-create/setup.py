from setuptools import setup

setup(
    name='gvm-create',
    version='1.0',
    py_modules=['gvm_create'],
    install_requires=[],
    entry_points={
        'console_scripts': [
            'gvm-create = gvm_create:main',
        ],
    },
)
