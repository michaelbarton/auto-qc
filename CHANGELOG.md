# Change Log

All notable changes to this project will be documented in this file.
This project adheres to [Semantic Versioning](http://semver.org/).

## 3.0.0 - Unreleased

* Update code from python 2.7 => 3.7.
* Add a flag `--manual / -m` which when given displays the `MANUAL.md` file.
  This replaces trying to install a man page on the user's system, which is
  hard to do reliably.

## 2.0.0 - 2018-02-21

### Added

* Added the `--json-output` flag. This generates a JSON formatted document
  describing the QC results.

* Each threshold file entry should include pass/fail messages. This is used
  to generate human readable output with more relevant information because
  the analyst can write the QC pass/fail messages themselves rather than the
  less readable machine-generated output. These pass/fail messages are
  available via the `message` key in the JSON output.

* Each threshold file entry should include an `fail_code`. The failure codes
  are returned for the failing QC thresholds. These can then be used to make
  downstream QC decisions.

* Each threshold file entry has an optional `tags` field. This can be used
  for adding analyst metadata to each entry, such as labelling the threshold
  types.

### Changed

* The threshold file tests must now must all evaluate to TRUE for a pass.
  This contrasts with the 1.x version where all thresholds must evaluate to
  FALSE for a pass. This means the threshold file is now written as a series
  of statements describing how the sequence data should be to considered as
  passing QC.

* Removed namespacing of analyses in the analysis file. The analysis file is
  now a dictionary with the fields `data` and `metadata`. The field `data` is
  a dictionary containing a the required metrics to do QC.

### Removed

* The `--yaml-output` and `--text-output` flags are now no longer supported.
  Detailed information instead retrieved using the `--json-output` flag.
  Tools such as `jq` can then be used to formatted this into whatever
  human-readable format is desired.
