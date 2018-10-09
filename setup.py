from setuptools import setup

setup (
    name = 'crossword-app',
    version = '1.0.0',
    entry_points = {
        'console_scripts': [
            'crossword = app.__main__:main'
        ]
    }
)