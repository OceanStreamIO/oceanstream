from setuptools import find_packages, setup

# Reading requirements from 'requirements.txt'
with open("requirements.txt", "r") as f:
    requirements = [line.strip() for line in f.readlines()]

setup(
    name="oceanstream",
    version="0.1",  # You can adjust the version number as needed
    packages=find_packages(),
    install_requires=requirements,
    # Optional metadata
    author="PineView AS",
    author_email="hello@pineview.io",
    description="A brief description of the oceanstream package",
    license="MIT",
    keywords="ocean stream processing",
    url="https://github.com/OceanStreamIO/oceanstream",
)
