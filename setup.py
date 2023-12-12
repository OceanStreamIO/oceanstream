from setuptools import find_packages, setup

# Reading requirements from 'requirements.txt'
with open("requirements.txt", "r") as f:
    requirements = [line.strip() for line in f.readlines()]

setup(
    name="oceanstream",
    version="0.1",
    packages=find_packages(),
    install_requires=requirements,
    package_data={"oceanstream": ["settings/*.json", "data/*.json"]},
    include_package_data=True,  # Include package data
    # Optional metadata
    author="Pine View Software AS",
    author_email="hello@pineview.io",
    description="",
    license="MIT",
    keywords="oceanstream echosounder",
    url="https://github.com/OceanStreamIO/oceanstream",
)
