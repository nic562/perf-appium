from setuptools import setup, find_packages


def parse_requirements(filename):
    """ load requirements from a pip requirements file. (replacing from pip.req import parse_requirements)"""
    content = (line.strip() for line in open(filename))
    return [line for line in content if line and not line.startswith("#")]


setup(
    name='perf-appium',
    packages=find_packages(),
    version='0.3',
    author='Nicholas Chen',
    author_email='nic562@gmail.com',
    license='Apache License 2.0',
    url='https://github.com/nic562/perf-appium',
    description='基于Appium和开源框架实现自动化UI操作和性能测试的框架',
    keywords=['android', 'ios', 'appium', 'performance'],
    data_files=['requirements.txt'],
    install_requires=parse_requirements('requirements.txt'),
    classifiers=[
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
)
