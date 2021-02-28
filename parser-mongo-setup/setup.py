from setuptools import find_packages, setup
setup(
    name='parsermongo',
    packages=find_packages(include=['parsermongo']),
    version='1.0.0',
    description='Read, parse files, write to mongodb',
    author='Victor Tuah Kumi, Javier Vite, Aidan Forester, Ahmed Iqbal',
    license='MIT',
    install_requires=['pymongo==3.11.3','Send2Trash==1.5.0'],
)