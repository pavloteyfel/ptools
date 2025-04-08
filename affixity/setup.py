from setuptools import setup

setup(
    name='affixity',
    version='1.0',
    py_modules=['affixity'],
    install_requires=[],
    entry_points={
        'console_scripts': [
            'affixity = affixity:main',
        ],
    },
)
