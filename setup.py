from setuptools import setup
import requirements
import os

# read the contents of your README file
from os import path
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

install_requires = []
with open('build/requirements.txt') as f:
    for req in requirements.parse(f):
        if req.name:
            name = req.name.replace('-', '_')
            full_line = name + ''.join([''.join(list(spec)) for spec in req.specs])
            install_requires.append(full_line)

setup(name="Let's Debug Helper",
      version=os.getenv('VERSION'),
      install_requires=install_requires,
      long_description=long_description,
      long_description_content_type='text/markdown')
