# auto-qc


For the full user manual see [MANUAL.md](./auto_qc/MANUAL.md).

## Building and Testing

Type `make` to get a full list of available commands for building and testing.
The available commands are:

```console
make bootstrap   Installs python and ruby dependencies locally
make test        Runs all unit tests defined in the test/
make feature     Runs all feature tests defined in the features/
make fmt         Runs black and isort code formatting
make fmt_check   Checks code is correctly formatted
make build       Builds a python package of auto_qc in dist/
```

## Versioning

This project uses bump2version to manage the version numbers. This project aims
to adhere to [Semantic Versioning](http://semver.org/) as much as possible. The
project version history is described in the CHANGELOG. Version strings can be
updated with the shell as follows:

```console
poetry run bump2version patch  # 3.0.0 → 3.0.1
poetry run bump2version minor  # 3.0.1 → 3.1.0
poetry run bump2version major  # 3.1.0 → 4.0.0
```

## Licence

auto-qc Copyright (c) 2017, The Regents of the University of California,
through Lawrence Berkeley National Laboratory (subject to receipt of any
required approvals from the U.S. Dept. of Energy).  All rights reserved.

If you have questions about your rights to use or distribute this software,
please contact Berkeley Lab's Innovation and Partnerships Office at
IPO@lbl.gov referring to " auto-qc v2 (2017-031)."

NOTICE.  This software was developed under funding from the U.S. Department
of Energy.  As such, the U.S. Government has been granted for itself and
others acting on its behalf a paid-up, nonexclusive, irrevocable, worldwide
license in the Software to reproduce, prepare derivative works, and perform
publicly and display publicly. The U.S. Government is granted for itself
and others acting on its behalf a paid-up, nonexclusive, irrevocable,
worldwide license in the Software to reproduce, prepare derivative works,
distribute copies to the public, perform publicly and display publicly, and
to permit others to do so.
