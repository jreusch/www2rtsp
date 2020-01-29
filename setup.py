setuptools.setup(
    name="websources-to-rtsp-streamer",
    version="0.0.1",
    author="Jan Reusch",
    author_email="jan@jreusch.de",
    description="A small script to open URLs in the bacground and stream the output via rtsp h264",
    long_description=long_description,
    long_description_content_type="text/markdown",
    #url="https://github.com/pypa/sampleproject",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
