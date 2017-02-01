from setuptools import setup, find_packages

setup(
    name="jungle",
    version="0.1.0",
    packages=find_packages(),
    package_data={},
    author="Nik Ogura",
    author_email="nik.ogura@gmail.com",
    description="Experiments in AWS",
    license="Apache 2.0",
    keywords="aws",
    url="https://github.com/nikogura/jungle-explorer",

    install_requires=[
        'boto3'
        'flask'
    ]

)
