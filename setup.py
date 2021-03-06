import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="ytdl-nfo",
    version="0.0.1",
    author="owdevel",
    author_email="owdevel@gmail.com",
    description="Utility to convert youtube-dl json metadata to .nfo",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/owdevel/ytdl-nfo",
    packages=['ytdl_nfo'],
    package_dir={'ytdl_nfo': 'ytdl_nfo'},
    package_data={'ytdl_nfo': ['configs/*.yaml']},
    license="Unlicense",
    install_requires=[
        'pyyaml',
    ],
    classifiers= [
        "Programming Language :: Python :: 3",
        "License :: Public Domain",
        "Operating System :: OS Independent",

    ],
    entry_points = {
        'console_scripts': ['ytdl-nfo=ytdl_nfo:main']
    },
    python_requires='>=3.6'
)