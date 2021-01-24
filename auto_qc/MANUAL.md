# auto-qc(1) -- A tool for storing business logic as data.

## Synopsis

`auto-qc` --data <DATA_FILE> --thresholds <THRESHOLD_FILE>

## Command Line Options

- `-d`, `--data` <DATA_FILE>: The path to the file containing input data to be
  checked.

- `-t`, `--thresholds` <THRESHOLD_FILE>: The path to the file containing the
  pass/fail thresholds.

- `-j`, `--json-output`: Generate JSON output describing each of the threshold
  checks.

## Syntax

### Source Data File

A data file is a YAML/JSON file containing all the data used to make decisions.
This file should contain nested dictionaries. An example data file might look like:

```YAML
---
manufacturing:
	defective_parts_per_million_per_month: 7
	mean_throughput_per_machine_per_month: 1462.8
customer:
	percent_on_time_delivery: 97.3
	returns_per_month: 31
```

### Source Threshold File

A threshold file specifies the QC criteria or business logic to make a pass or
fail based on the fields and metrics in the data above file. The threshold file
is a YAML/JSON dictionary contains two fields `version` and `thresholds`. These
fields are defined as:

- **version** - This field is checked by auto-qc to determine if the QC
  threshold syntax matches that of the version of auto-qc being run. For the
  current version of auto-qc this should be `3.0.0`. If the `version` field is
  out of date, e.g. `2.x`, then auto-qc will immediately fail.

- **thresholds** - This field should contain a list of dictionaries, where each
  entry defines a rule that should be evaluated against the metrics in the data
  file. The threshold dictionaries are defined as follows in the next section.

### Evaluated Rules

Use the example data above, a simple threshold file with two business rules
might look like:

```
version: 3.0.0
thresholds:

- name: Dropping throughput rate
  fail_code: ERR_001
  rule:
	- LESS_THAN
  - :manufacturing/mean_throughput_per_machine_per_month
  - 10000

- name: Increasing defects
  fail_code: ERR_002
  rule:
	- OR
  - [GREATER_THAN, :manufacturing/defective_parts_per_million_per_month, 100]
  - [GREATER_THAN, :customer/returns_per_month, 10]
```

The first rule 'Dropping throughput rate' checks the value in the data file for
the path `:manufacturing/mean_throughput_per_machine_per_month` ensures it's
greater than `10000`.

The second rule 'Increasing defects' is a compound rule joined by an `OR`
operator, and checks two metrics in the data file to see if either are above a
given threshold file. This second rule illustates that all business rules are
lists beginning with an operator, and can be arbrarily nested. The full list of
available operators is given below.

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

### AVAILABLE OPERATORS

**equals** / **not_equals** - Test whether two values are equal or not.

```YAML
- equals
- :run_metadata/protocol
- Low Input DNA
```

**greater_than** / **less_than** / **greater_equal_than** / **less_equal_than** -
Test whether one numeric value is greater/smaller than another.

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
