# setup.py helps py.test find your tests in comp/tests/test_functions.py

import setuptools
import os

setuptools.setup(
    name="compconfig",
    version=os.environ.get("VERSION", "0.0.0"),
    author="Hank Doupe",
    author_email="henrymdoupe@gmail.com",
    description="COMP configuration files.",
    url="https://github.com/comp-org/COMP-Developer-Toolkit",
    packages=setuptools.find_packages(),
    include_package_data=True,
)
