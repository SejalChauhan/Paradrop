from setuptools import setup, find_packages
 
setup(
    name="paradrop",
    version="0.1",
    author="Damouse",
    description="Paradrop wireless virtualization",
    install_requires=['flask'],
    packages=find_packages(),

    entry_points={
        'console_scripts': [
            'paradrop=paradrop.paradrop:main',
        ],
    },
)