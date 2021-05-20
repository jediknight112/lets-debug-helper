from setuptools import setup
import requirements
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

setup(name="lets-debug-helper",
      version="1.0.4",
      author="Jeffrey Crane",
      author_email="jediknight11206@gmail.com",
      description="This is a cli tool that interacts with the Let's Debug API",
      url="https://github.com/jediknight112/lets-debug-helper",
      install_requires=install_requires,
      long_description=long_description,
      long_description_content_type='text/markdown',
      classifiers=[
          "Programming Language :: Python :: 3",
          "License :: OSI Approved :: MIT License",
          "Operating System :: OS Independent",
      ],
      python_requires='>=3.8',
      )
