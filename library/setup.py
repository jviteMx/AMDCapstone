from setuptools import find_packages, setup
setup(
    name='pargo',
    packages=find_packages(include=['pargo', 'annotate']),
    description='Parse, process rocm math library test outs files and write to mongo db',
    version='1.0.0',
    author='Victor Tuah Kumi, Javier Vite Ahmed Iqbal, Aidan Forester',
    license='MIT',
    install_requires=['pymongo==3.11.3']
)