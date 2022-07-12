from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='contek-tusk',
    version='1.5',
    description='Tusk for Clickhouse metric writing',
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    py_modules=["contek_tusk"],
    url='https://github.com/contek-io/contek-tusk',
    author='contek_bjy',
    author_email='bjy@contek.io',
    license='MIT',
    install_requires=[
        'clickhouse-driver',
        'pandas',
        'pyyaml',
    ],
    zip_safe=True,
)
