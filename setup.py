import setuptools
import os

with open("README.md", "r") as f:
    long_description = f.read()

setuptools.setup(
    name="compbaseball",
    version=os.environ.get("TAG"),
    author="Hank Doupe",
    author_email="henrymdoupe@gmail.com",
    description="Documents COMP via baseball data examples.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/hdoupe/compbaseball",
    packages=setuptools.find_packages(),
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
