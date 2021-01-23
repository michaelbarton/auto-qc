# auto-qc(1) -- A tool for using business logic as data.

## SYNOPSIS

`auto-qc` --data <DATA_FILE> --thresholds <THRESHOLD_FILE>

## OPTIONS

- `-d`, `--data` <DATA_FILE>: The path to the file containing input data to be
  checked.

- `-t`, `--thresholds` <THRESHOLD_FILE>: The path to the file containing the
  pass/fail thresholds.

- `-j`, `--json-output`: Generate JSON output describing each of the threshold
  checks.

## SYNTAX

### DATA FILE

The data file is a YAML/JSON file containing all the metrics you want to use to
make decisions. This file can be free form with any level of nesting, however
lists are not allowed, only dictioaries. An example data file looks like:

```YAML
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

The threshold file specifies the QC criteria or business logic to make a pass
or fail based on the fields and metrics in the data above file. The threshold
file is a YAML/JSON dictionary contains two fields `version` and `thresholds`.
These fields are defined as:

- **version** - This field is checked by auto-qc to determine if the QC
  threshold syntax matches that of the version of auto-qc being run according
  to [semantic versioning][semver]. For the current version of auto-qc this
  should be `3.0.0`. If the `version` field is out of date, e.g. `2.x`, then
  auto-qc will fail.

- **thresholds** - This field should contain a list of dictionaries, where each
  dictionary is a business logic rule that should be evaluated against the
  data. The threshold dictionaries are defined in the following section.

### EVALUATION RULES

Each evaluation rule dictionary contains:

- **name**: A unique name for this business rule.

- **fail_msg**: A message to generate f this entry QC entry fails. Python
  string interpolation can be used to customise this message with values from
  the data file.

- **pass_msg**: A message to generate if this entry passes. Python string
  interpolation may also be used to customise this message with values from the
  data file.

- **fail_code**: An ID for the kind of failure identified if this entry
  evaluates to fail. The list of failure codes is returned in the JSON output
  with the flag.

- **tags**: A optional list of tags for the QC entry. These tags are returned
  in the JSON output if `--json-output` is used. These have no effect on the
  evaluation of the tool, but can be useful for downstream processing of the
  generated JSON output. E.g. process the failures and group by tags.

- **rule**:

  - **operator** - An operator to test the QC value. This may be mathematical
    comparison operators such as 'greater_than' or Boolean operators such as
    'AND'. The list of allowed operators is described in the section below.

  - **analysis value** - The value from the data file that should be
    tested. The colon ':' indicates that this a reference to a value in the
    data file. The remainder of this string shows the path to the value
    to be tested.

  - **literal value** - A literal value that to compare with the reference
    value.

An example of a simple threshold file with two QC tests is given below. In this
example if both QC evaluations return TRUE then this will pass. If either
return FALSE then this will fail QC.

```YAML
version: 3.0.0
thresholds:
- name: example test
  pass_msg: No contamination detected.
  fail_msg: Contamination detected at {metrics/percent_contamination}%
  fail_code: ERR00001
  tags: ["contamination"]
  rule:
  - greater_than
  - :metrics/percent_contamination
  - 2
```

A more complex example uses `NOT` and `AND` to create a QC threshold that
fails only when both of the nested thresholds fail. Boolean operators can be
use arbitrarily to create more complex QC tests.

```YAML
version: 3.0.0
thresholds:
- name: example test
  pass_msg: No obvious contamination detected.
  fail_msg: Contamination detected at {metrics/percent_contamination}% with {reads/contaminants} reads.
  fail_code: ERR00001
  tags: ["contamination"]
  rule:
  - AND
  - - [less_than :metrics/percent_contamination, 2]
    - [less_than, :reads/contaminants, 1e6]
```

### AVAILABLE OPERATORS

**equals** / **not_equals** - Test whether two values are equal or not.

```YAML
- equals
- :run_metadata/protocol
- Low Input DNA
```

**greater_than** / **less_than** / **greater_equal_than** / **less_equal_than** - Test whether one
numeric value is greater/smaller than another.

```YAML
- greater_than
- :human_contamination/metrics/percent_contamination
- 5
```

**and** - Test whether two values are both true. The example here illustrates
that metrics can be nested. For instance here, the two arguments to the **and**
operator are themselves thresholds.

```YAML
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

```YAML
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

```YAML
- not
- :cat_contamination/is_contaminated
```

**is_in** / **is_not_in** - Test whether a value is in a list of values. Note
that the list of values must begin with the **list** operator.

```YAML
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

- 3.0.0 - Mon 11 Jan 2021
- 2.0.0 - Mon 20 Jun 2016
- 1.1.0 - Mon 27 Apr 2015
- 1.0.0 - Fri 15 Aug 2014
- 0.2.1 - Tue 20 May 2014
- 0.2.0 - Mon 19 May 2014
- 0.1.0 - Thu 15 May 2014
