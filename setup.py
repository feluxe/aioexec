from setuptools import setup, find_packages
from codecs import open
import ruamel.yaml as yaml


def load_yaml(file: str, keep_order: bool = False) -> dict:
    with open(file, 'r') as stream:
        if keep_order:
            return yaml.load(stream.read(), Loader=yaml.RoundTripLoader)
        else:
            return yaml.safe_load(stream.read())


with open('README.md') as f:
    long_description = f.read()

print(long_description)

config = load_yaml('Project')

setup(
    name=config['public_name'],
    version=config['version'],
    author=config['author'],
    author_email=config['author_email'],
    maintainer=config['maintainer'],
    maintainer_email=config['maintainer_email'],
    url=config['url'],
    description=config['description'],
    long_description=long_description,
    long_description_content_type="text/markdown",
    download_url=config['url'] + '/tarball/' + config['version'],
    license=config['license'],
    keywords=config['keywords'],
    include_package_data=True,
    platforms=[],
    classifiers=[],
    install_requires=[],
    packages=find_packages(where='.', exclude=('tests', 'tests.*')),
    package_dir={"aioexec": "aioexec"},
    package_data={},
    data_files=[],
    entry_points={"console_scripts": [], "gui_scripts": []},
    tests_require=[],
)
