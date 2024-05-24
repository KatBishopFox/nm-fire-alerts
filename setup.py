from setuptools import find_packages, setup

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setup(
    name="NM-fire-alerts",
    version="0.1.0",
    author="Katie Ritchie",
    author_email="ritchieke@gmail.com",
    description="Query the https://nifc.maps.arcgis.com/apps/dashboards/aa9ff369dd414b74b69b696b40a1d057 map to determine if New Mexico National Forests have fire prohibitions or bans.",
    url="https://github.com/KatBishopFox/nm-fire-alerts"
    packages=find_packages(exclude=("tests", "docs")),
    install_requires=requirements,
    classifiers=[
        "Programming Language :: Python :: 3.10",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.10",
    entry_points={"console_scripts": ["nm-fire-alerts=nm-fire-alerts.main:main"]},
)