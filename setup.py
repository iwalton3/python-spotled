from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='spotled',
    version='1.0.1',
    author="Ian Walton",
    author_email="ian@iwalton.com",
    description="Allows control of SPOTLED bluetooth led displays via Python. (Unofficial)",
    license='MIT',
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    url="https://github.com/iwalton3/python-spotled",
    packages=['spotled'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
    install_requires=['gattlib'],
    include_package_data=True,
    package_data={
        "spotled": ["fonts/*.yaff"],
    },
)
