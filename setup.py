import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="dryflower",
    version="1.0",
    author="shmn7iii",
    author_email="shmn7iii@gmail.com",
    description="dryflower is a package of DryFlowerBOT.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://www.shmn7iii.net/dryflower",
    classifiers=[
        "Programming Language :: Python :: 3.9.4",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    packages=setuptools.find_packages()
)