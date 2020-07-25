import setuptools

with open("README.md", "r") as fh:
  long_description = fh.read()

setuptools.setup(
  name="pychroma",
  version="0.0.1",
  author="Patryk Janiak",
  author_email="xmorswinx@gmail.com",
  description="Python library for accessing the Razer Chroma SDK",
  long_description=long_description,
  long_description_content_type="text/markdown",
  url="https://github.com/morswin22/pychroma",
  packages=setuptools.find_packages(),
  license="MIT",
  classifiers=[
    "Programming Language :: Python :: 3",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
  ],
  python_requires='>=3.6',
  install_requires=[
    "requests>=2.23.0",
    "pynput>=1.6.8"
  ]
)