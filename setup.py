# -*- coding: utf-8 -*-

"""setup.py"""

from setuptools import setup, find_packages

from pytractions.pkgutils import traction_entry_points

import signtractions.tractors.t_sign_containers
import signtractions.tractors.t_sign_snapshot

classifiers = [
    "Development Status :: 3 - Alpha",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)",
    "Programming Language :: Python",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.7",
    "Programming Language :: Python :: Implementation :: CPython",
    "Programming Language :: Python :: Implementation :: PyPy",
]


def get_requirements():
    """
    Transform a list of requirements so that they are usable by older pip (9.0.0), and newer pip

    Regex extracts name and url from a tox-compatible format, and replaces it with only a name
    (which will be combined with dependency_links) or with PEP-508 compatible dependency.
    """
    with open("requirements.txt") as f:
        reqs = f.read().splitlines()
        return reqs


setup(
    name="signtractions",
    version="0.0.5",
    description="quay-tractions",
    long_description="pubtools-sign pytractions wrapper for signing containers and release snapshots in tractions.",
    long_description_content_type="text/x-rst",
    author="Jindrich Luza",
    author_email="jluza@redhat.com",
    url="https://github.com/midnightercz/signtractions",
    classifiers=classifiers,
    python_requires=">=3.6",
    packages=find_packages(exclude=["tests"]),
    data_files=[],
    install_requires=[
        "koji",
        "requests",
        "requests_kerberos",
        "pytractions @ git+https://github.com/midnightercz/pytractions.git@main",
        "gssapi"],
    entry_points={
        "tractions": list(set([
            x for x in traction_entry_points(signtractions.tractors.t_sign_containers)
        ]) & set([
            x for x in traction_entry_points(signtractions.tractors.t_sign_snapshot)
        ])),
    },
    dependency_links=[
    ],
    include_package_data=True,
)
