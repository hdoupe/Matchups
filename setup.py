import setuptools
import os

with open("README.md", "r") as f:
    long_description = f.read()

setuptools.setup(
    name="matchups",
    version=os.environ.get("TAG"),
    author="Hank Doupe",
    author_email="henrymdoupe@gmail.com",
    description="Provides pitch data on pitcher and batter matchups.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/hdoupe/Matchups",
    packages=setuptools.find_packages(),
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
