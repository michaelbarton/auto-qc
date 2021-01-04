from setuptools import setup, find_packages
from auto_qc.version import __version__

setup(
    name                 = 'auto_qc',
    version              = __version__,
    description          = 'Run high-throughput automated quality control using configuration files.',
    author               = 'Michael Barton',
    author_email         = 'mail@michaelbarton.me.uk',
    scripts              = ['bin/auto-qc'],
    install_requires     = open('requirements/default.txt').read().splitlines(),
    packages             = find_packages(),
    package_data         = {'': ['assets/*']},
    include_package_data = True,

    classifiers = [
        'Natural Language :: English',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Operating System :: POSIX'
    ],
)
