import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

with open("requirements.txt", "r") as fh:
    requirements_raw = fh.read()
    requirements_list = requirements_raw.split('\n')
    requirements = []
    for req in requirements_list:
        # Skip comments and optional requirements
        if not req.strip().startswith('#') and len(req.strip()) > 0 and not req.strip().startswith(
                'mysqlclient') and not req.strip().startswith('psycopg2'):
            requirements.append(req)

setuptools.setup(
    version=0.0,
    name="tesla-ce",
    author="Xavier Baro",
    author_email="xbaro@uoc.edu",
    description="TeSLA CE",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/tesla-ce/core",
    packages=setuptools.find_packages('src', exclude='__pycache__'),
    package_dir={'': 'src'},  # tell distutils packages are under src
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)",
        "Operating System :: POSIX :: Linux",
    ],
    python_requires='>=3.6',
    install_requires=requirements,
    extras_require={
        'mysql': ["mysqlclient"],
        'psql': ["psycopg2"]
    }
)
