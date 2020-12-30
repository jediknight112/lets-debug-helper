from setuptools import setup
import requirements
import os

install_requires = []
with open('build/requirements.txt') as f:
    for req in requirements.parse(f):
        if req.name:
            name = req.name.replace('-', '_')
            full_line = name + ''.join([''.join(list(spec)) for spec in req.specs])
            install_requires.append(full_line)

setup(version=os.getenv('VERSION'),
      install_requires=install_requires)
