from setuptools import setup, find_packages

setup(
    name='mlb_strikezone_app',
    version='1.0.0',
    description='App that polls the MLB API and creates a visual strike zone with descriptions of each pitch and its outcome.',
    author='Vincent Crescente',
    packages=find_packages(where='.'),  # Search from the root
    package_dir={'mlb_strikezone_app': 'mlb_strikezone_app'},
    install_requires=[
        'pillow==11.2.1',
        'requests==2.32.3',
        'python-dotenv==1.0.0'
    ],
    entry_points={
        'console_scripts': [
            'strikezone=mlb_strikezone_app.main:main'
        ],
    },
    python_requires='>=3.11',
)