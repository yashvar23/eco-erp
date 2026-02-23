from setuptools import setup, find_packages

import os
install_requires = []
if os.path.exists("requirements.txt"):
    with open("requirements.txt") as f:
        install_requires = [r.strip() for r in f.read().splitlines() if r.strip()]

setup(
	name="eco_app",
	version="1.0.0",
	description="ECO App for European Concept Overseas on Frappe/ERPNext v17",
	author="ECO Dev Team",
	author_email="dev@europeanconceptoverseas.com",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
