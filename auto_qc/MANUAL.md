# auto-qc(1) -- A command line tool for automated quality control

## SYNOPSIS

`auto-qc` --data <ANALYSIS_FILE> --thesholds <THRESHOLD_FILE>

## OPTIONS

* `-d`, `--data` <DATA_FILE>: The path to the file containing input data to be
  checked.

* `-t`, `--thresholds` <THRESHOLD_FILE>: The path to the file containing the
  pass/fail thresholds.

* `-j`, `--json-output`: Generate JSON output describing each of the threshold
  checks.

## SYNTAX

### ANALYSIS FILE

The data file is a YAML dictionary with the keys `metadata` and `data`. Both
these `metadata` and `data` fields are freeform dictionaries that can contain
any subdictionary with any fields.

The `metadata` field contains an additional data that is required to be stored
about the QC data. The one mandatory field is required under `metadata` is
`version/auto-qc`. The version number should match the version number of
auto-qc being used. This version number is checked by auto-qc to prevent
incompatible versions being used. [Semantic versioning][semver] is followed
when defining version numbers for auto-qc.

[semver]: http://semver.org

The `data` field is used to store all the metrics values used to make the QC
decision. There is no restriction on the dictionary structure or keys. Arrays
are however not permitted.

An example data file is given below.

``` YAML
---
bases:
	contaminants: 1392000
	initial: 1500000000
	non_contaminants: 1498608000
metrics:
	percent_contamination: 0.1
reads:
	contaminants: 9280
	initial: 10000000
	non_contaminants: 9990720
```

### THRESHOLD FILE

The threshold file specifies the QC criteria for pass or fail. This is a YAML
format dictionary contains two fields `metadata` and `thresholds`. These fields
are defined as:

* **metadata** - This contains any metadata that you wish to associate with
  your threshold file. The field `metadata/version/auto-qc` is mandatory and
  is checked by auto-qc to determine if the QC threshold syntax matches that
  of the version of auto-qc according to [semantic versioning][semver].

* **thresholds** - This field should contain an array of
  [s-expressions][sexp]. Each s-expression is a list defining a single QC
  threshold. The format of each threshold is:

  * **metadata dictionary** - A dictionary with metadata fields for the QC
    threshold. The required fields are: `name`, `fail_msg` and `pass_msg`,
    with an optional `tags' field. The description of each of these fields
    are:

    * **name**: A unique name describing the QC entry.

    * **fail_msg**: The message to return when this entry QC entry fails.
      Python string interpolation can be used to customise this message with
      values from the analysis file.

    * **pass_msg**: The message to return when this entry QC entry pass.
      Python string interpolation may also be used to customise this message
      with values from the analysis file.

    * **fail_code**: An ID for the kind of failure identified if this entry
      does not pass QC. The list of failure codes is returned in the JSON
      output with the `--json-output` flag.

    * **tags**: A optional list of tags for the QC entry. These tags are
      returned in the JSON output and can be used to organise the QC entries.

  * **operator** - An operator to test the QC value. This may be mathematical
    comparison operators such as 'greater_than' or Boolean operators such as 'AND'. The
    list of allowed operators is described in the section below.

  * **analysis value** - The value from the analysis file that should be
    tested. The colon ':' indicates that this a reference to a value in the
    analysis file. The remainder of this string shows the path to the value
    to be tested.

  * **literal value** - A literal value that to compare with the reference
    value.

[sexp]: https://en.wikipedia.org/wiki/S-expression

An example of a simple threshold file with two QC tests is given below. In this
example if both QC evaluations return TRUE then this will pass. If either
return FALSE then this will fail QC.

``` YAML
version: 3.0.0
thresholds:
- - name: example test
    pass_msg: No obvious contamination detected.
    fail_msg: Contamination detected at {metrics/percent_contamination}%
    fail_code: ERR00001
    tags: ["contamination"]
  - greater_than
  - :metrics/percent_contamination
  - 2
```

A more complex example uses `NOT` and `AND` to create a QC threshold that
fails only when both of the nested thresholds fail. Boolean operators can be
use arbitrarily to create more complex QC tests.

``` YAML
version: 3.0.0
thresholds:
- - name: example test
    pass_msg: No obvious contamination detected.
    fail_msg: Contamination detected at {metrics/percent_contamination}% with {reads/contaminants} reads.
    fail_code: ERR00001
    tags: ["contamination"]
  - AND
  - - [less_than :metrics/percent_contamination, 2]
    - [less_than, :reads/contaminants, 1e6]
```

### AVAILABLE OPERATORS

**equals** / **not_equals** - Test whether two values are equal or not.

``` YAML
- equals
- :run_metadata/protocol
- Low Input DNA
```

**greater_than** / **less_than** / **greater_equal_than** / **less_equal_than** - Test whether one
numeric value is greater/smaller than another.

``` YAML
- greater_than
- :human_contamination/metrics/percent_contamination
- 5
```

**and** - Test whether two values are both true. The example here illustrates
that metrics can be nested. For instance here, the two arguments to the **and**
operator are themselves thresholds.

``` YAML
- and
-
  - greater_than
  - :cat_contamination/metrics/percent_contamination
  - 5
-
  - greater_than
  - :dog_contamination/metrics/percent_contamination
  - 5
```

**or** - Test whether any values are true.

``` YAML
- or
-
  - greater_than
  - :cat_contamination/metrics/percent_contamination
  - 5
-
  - greater_than
  - :dog_contamination/metrics/percent_contamination
  - 5
```

**not** - Flips the Boolean value

``` YAML
- not
- :cat_contamination/is_contaminated
```

**is_in** / **is_not_in** - Test whether a value is in a list of values. Note
that the list of values must begin with the **list** operator.

``` YAML
- is_in
- :cat_contamination/name_of_cat
-
  - list
  - "Chase No Face"
  - "Colonel Meow"
  - "Felicette"
  - "Mrs. Chippy"
  - "Peter, the Lord's Cat"
  - "Tiddles"
  - "Wilberforce"
```

## AUTHOR

Michael Barton <mail@michaelbarton.me.uk>

## HISTORY

* 3.0.0 - Mon 11 Jan 2021
* 2.0.0 - Mon 20 Jun 2016
* 1.1.0 - Mon 27 Apr 2015
* 1.0.0 - Fri 15 Aug 2014
* 0.2.1 - Tue 20 May 2014
* 0.2.0 - Mon 19 May 2014
* 0.1.0 - Thu 15 May 2014
