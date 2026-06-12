# Change Log

All notable changes to this project will be documented in this file. This
project adheres to [Semantic Versioning](http://semver.org/).

## Unreleased

### Added

- A `--margin` / `-M` flag that reports, for every ordered numeric comparison in
  a rule, how far the metric could move before the comparison flips — the slack
  on a passing check or the shortfall on a failing one — and marks the tightest
  comparison in each rule. This surfaces _how robustly_ a sample passed, which a
  bare `PASS`/`FAIL` hides. Equality, string and membership tests are discrete
  and have no margin, so they are skipped.
- The same margin is included on every ordered comparison node in the
  `--json-output` `explain` tree (a `margin` key alongside `operator`, `result`
  and `args`), so the margins of a whole cohort of samples can be aggregated —
  per rule — into a threshold-sensitivity dataset.

## 3.0.0 - 2026-06-01

This is a major release that ports auto-qc to Python 3, modernises the packaging
and command-line interface, and simplifies the input file formats. It is **not
backwards compatible** with 2.x threshold or data files.

### Changed

- Ported the codebase from Python 2.7 to Python 3 (now requires Python 3.10+).
- Rewrote the command-line interface using
  [click](https://click.palletsprojects.com/):
  - Renamed flag `--analysis-file` / `-a` => `--data` / `-d`.
  - Renamed flag `--threshold-file` / `-t` => `--thresholds` / `-t`.
  - Kept `--json-output` / `-j`.
- Simplified the **data** file format: it is now a plain JSON / YAML dictionary
  with no required metadata wrapper.
- Simplified the **thresholds** file format: a top-level `version` and
  `thresholds` list, where each entry is a dictionary with `name`, `fail_code`
  and `rule` (and optional `pass_msg`, `fail_msg` and `tags`). The version field
  moved from `metadata.auto_qc.version` => `version`.
- Human-readable output now prints `PASS`, or `FAIL: <fail_code>, ...` listing
  the codes of every rule that failed.
- Threshold and data files are now validated up front with
  [pydantic](https://docs.pydantic.dev/); invalid files report a clear error and
  exit non-zero.

### Added

- A non-zero exit code is returned when any QC rule fails, so auto-qc can be
  used directly in pipelines and CI.
- Support for list-valued data references (used by the `is_in` / `is_not_in`
  operators). The membership list can now be written inline, without the
  explicit `list` keyword.
- New operators that make rules more expressive without leaving the s-expression
  syntax: `between` (inclusive range); `add`, `subtract`, `multiply` and
  `divide` (arithmetic over derived values such as ratios); `matches`,
  `starts_with`, `ends_with` and `contains` (string and collection predicates);
  and `length`.
- Friendly, single `AutoQCError` for rules that can't be evaluated. Type
  mismatches (e.g. comparing a number to text or to a missing metric) and
  operators given the wrong number of arguments now report a clear message
  naming the rule, instead of raising an uncaught Python traceback. Argument
  counts are validated up front.
- `--data` and `--thresholds` accept `-` to read a document from standard input,
  so auto-qc fits a shell pipeline without a temp file.
- A `--version` / `-V` flag.
- The `--json-output` report now includes a machine-readable `explain` tree for
  each rule (every operator with its result, every pointer resolved to its
  value), so downstream tooling can show why a rule failed.
- An `examples/` directory with runnable examples.
- An `--explain` / `-e` flag that prints a tree showing how every rule was
  evaluated, with each metric pointer resolved to its value and the passing and
  failing branches marked.
- A `--test` / `-T` flag that runs a suite of test cases against a thresholds
  file, pairing sample data with the outcome you expect (`pass`/`fail`, with
  optional exact `codes`) and reporting which cases disagree with the rules.
- "Did you mean ...?" suggestions when a rule references an unknown metric path
  or operator.
- A small, documented public Python API: `from auto_qc import run`. Invalid
  input now raises `auto_qc.AutoQCError` rather than leaking pydantic's
  `ValidationError` to callers.
- A `py.typed` marker (PEP 561) so downstream type checkers use auto-qc's
  annotations.

### Removed

- Removed the unmaintained `fn`, `funcy` and `python-termstyle` dependencies.
  Runtime dependencies are now `click`, `pydantic`, `rich` and `PyYAML`.

### Packaging & tooling

- Replaced `setup.py` / `tox` with a PEP 621 `pyproject.toml` built by
  [hatchling](https://hatch.pypa.io/), managed with
  [uv](https://docs.astral.sh/uv/).
- The version number is single-sourced from `auto_qc/version.py`.
- Linting and formatting moved to [ruff](https://docs.astral.sh/ruff/); Markdown
  is formatted with [prettier](https://prettier.io/).
- Added a GitHub Actions workflow that runs the unit and feature tests, lints,
  and builds the package on every push and pull request. Tests run across a
  Python 3.10–3.13 matrix, and the package is type checked with
  [mypy](https://mypy-lang.org/).

## 2.0.0 - 2018-02-21

### Added

- Added the `--json-output` flag. This generates a JSON formatted document
  describing the QC results.

- Each threshold file entry should include pass/fail messages. This is used to
  generate human readable output with more relevant information because the
  analyst can write the QC pass/fail messages themselves rather than the less
  readable machine-generated output. These pass/fail messages are available via
  the `message` key in the JSON output.

- Each threshold file entry should include an `fail_code`. The failure codes are
  returned for the failing QC thresholds. These can then be used to make
  downstream QC decisions.

- Each threshold file entry has an optional `tags` field. This can be used for
  adding analyst metadata to each entry, such as labelling the threshold types.

### Changed

- The threshold file tests must now must all evaluate to TRUE for a pass. This
  contrasts with the 1.x version where all thresholds must evaluate to FALSE for
  a pass. This means the threshold file is now written as a series of statements
  describing how the sequence data should be to considered as passing QC.

- Removed namespacing of analyses in the analysis file. The analysis file is now
  a dictionary with the fields `data` and `metadata`. The field `data` is a
  dictionary containing a the required metrics to do QC.

### Removed

- The `--yaml-output` and `--text-output` flags are now no longer supported.
  Detailed information instead retrieved using the `--json-output` flag. Tools
  such as `jq` can then be used to formatted this into whatever human-readable
  format is desired.
