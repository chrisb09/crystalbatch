import setuptools
import versioneer

with open("README.rst", "r") as fh:
    long_description = fh.read()
with open("requirements.txt", "r") as fh:
    requirements = [line.strip() for line in fh]

setuptools.setup(
    name="crystalbatch",
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    author="Christian F. Brinkmann",
    author_email="mail@christian-f-brinkmann.de",
    description="A GUI for renaming file batches manually",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.5',
    install_requires=requirements,
)
