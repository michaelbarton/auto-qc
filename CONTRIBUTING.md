# Contributing to auto-qc

Thanks for your interest in improving auto-qc. This document covers how to set
up a development environment, run the checks, and cut a release.

## Development environment

auto-qc uses [uv](https://docs.astral.sh/uv/) for dependency management and
[ruff](https://docs.astral.sh/ruff/) for linting and formatting. Markdown is
formatted with [prettier](https://prettier.io/) via `npx`, so a recent Node.js
is needed for the formatting checks.

Install the Python dependencies into a local virtual environment with:

```console
make bootstrap
```

## Running the checks

The same checks that run in CI are available as `make` targets:

```console
make test        # run the unit tests with pytest
make feature     # run the feature tests with behave
make fmt         # auto-format the code (ruff) and Markdown (prettier)
make fmt_check   # check formatting without changing files
make build       # build the wheel and sdist into dist/
```

`make all` runs the formatting check, both test suites, and the build, which is
the quickest way to confirm a change is ready to push.

## Pull requests

- Keep changes focused and add tests for new behaviour. Unit tests live in
  `test/` and end-to-end feature tests live in `features/`.
- Run `make fmt` before committing so the diff only contains meaningful changes.
- Update `CHANGELOG.md` under the unreleased heading when your change is
  user-facing.

## Cutting a release

1. Update the version string in `auto_qc/version.py`. This is the single source
   of truth for the package version, the `--json-output` payload, and the
   threshold-file `version` compatibility check.
2. Move the relevant `CHANGELOG.md` entries under a new dated heading.
3. Open a pull request and merge once CI is green.
4. Tag the merge commit (`git tag vX.Y.Z && git push origin vX.Y.Z`) and publish
   a GitHub release for that tag. The
   [`release` workflow](.github/workflows/release.yml) builds the package and
   publishes it to [PyPI](https://pypi.org/project/auto-qc/) automatically.

Publishing uses PyPI
[trusted publishing](https://docs.pypi.org/trusted-publishers/), so no API token
is stored in the repository. The PyPI project must be configured to trust this
repository's `release` workflow before the first automated publish.
