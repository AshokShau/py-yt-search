import os

from setuptools import setup, find_packages

base_path = os.path.abspath(os.path.dirname(__file__))

about: dict = {}

with open(
        os.path.join(
            base_path,
            'py_yt',
            '__version__.py',
        ), encoding='utf-8',
) as f:
    exec(f.read(), about)

DESCRIPTION = 'A Python package for searching and retrieving YouTube data using py-yt-search.'
with open("README.md", encoding="utf8") as readme:
    long_description = readme.read()

setup(
    name="py-yt-search",
    version=about["__version__"],
    author="AshokShau",
    author_email="<abishnoi69@outlook.com>",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=long_description,
    packages=find_packages(),
    install_requires=[
        'httpx>=0.28.1',
    ],
    keywords="youtube youtube-api video-search playlist channel search py_yt py-yt-search py-yt",
    url="https://github.com/AshokShau/py-yt",
    download_url="https://github.com/AshokShau/py-yt-search/releases/latest",
    license="MIT",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "License :: OSI Approved :: MIT License",
        "Topic :: Internet",
        "Topic :: Multimedia :: Video",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    project_urls={
        "Tracker": "https://github.com/AshokShau/py-yt-search/issues",
        "Source": "https://github.com/AshokShau/py-yt-search",
    },
    python_requires=">=3.8",
)
