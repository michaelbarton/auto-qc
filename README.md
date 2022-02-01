# auto-qc - quality control as config file

TODO: Logo

TODO: GIF. Perhaps: https://github.com/johnkerl/miller

TODO: python Code example, with generated output dictionary

## Quick Start

Create a JSON file with data:

```json
{
  "height": 14.2,
  "width": 9.3
}
```

Write a list of quality rules in a YAML file:

```yaml
quality_control:
  - id: "MINIMUM_HEIGHT"
    require: ["greater_than", ":height", 10]
  - id: "MINIMUM_WIDTH"
    require: ["greater_than", ":width", 10]
version: 3
```

Run `auto-qc` to see if the product passes quality control.

```console
$ auto-qc --data=data.json --thresholds=qc_rules.yml

FAIL: MINIMUM_WIDTH
```

### Installation

```console
pip3 install auto-qc
```

## What's the point?

Before processing data you often need to check the quality of the input data.
If the data is bad you want the code to exit or flag a failure the data before
trying to proceed, or before passing data onto downstream users. The most
common way of doing this in applications is using `if` and `case` statements
and then raising an exception or skipping bad data.

Auto QC is an alternative to `if` statments, intead creating quality checks as
lists in YAML. This reduces complexity because the QC checks can be maintained
outside the application in configuration files. New QC thresholds can be tested
without having to create a pull request or build a new a Docker image. Instead
quality control rules are updated by changing lists in a configuration file
outside the application.

The first version of auto-qc was prototyped at the Joint Genome Institute. It
has been used in production since 2014 to quality check and flag issues in the
thousands of sequenced microbial genomes every year.

## How to create a QC rules file

The `auto-qc` tool accepts two input files: a JSON file containing your data,
and a YAML file containing the quality control requirements. The reference JSON
data can be in any format. A small example for the QC rules YAML looks like:

```yaml
quality_control:
  - id: "MINIMUM_LENGTH"
    require: ["greater_equal_than", ":length", 10]
version: 3
```

This specifies that the length variable should be greater or equal to 10. There
should be a corresponding "length" key in the JSON value. The tool will look up
this value and check if it meets the threashold. If not the id
`MINIMUM_LENGTH` is reported as the failure cause.

### Creating more complex QC rules

More complex examples can be built by combining multiple requirements using
Boolean expressions such as `AND` or `OR`. The below example assumes the
thresholds depend on the type of board being manufactured. Cheaper boards
have more lax quality thresholds. This can be handled by encoding the board
type in the data file.

```json
{
  "id": "GSV-00478-9",
  "lot": 10742,
  "board_type": "cheap",
  "specs": {
    "density": 14.2,
    "defects_per_metre": 0.02
  }
}
```

The thresholds file uses a mixture of `OR` and `AND` expressions to test the
value of `:bar` based on the value of the `:widget_type` field.

```yaml qc_threshold_example
thresholds:

  - comment: "The number of defects allowed per sq.m. depends on board type."
    id: "BAR_FAILURE"
    require:
      - OR
      - - AND
        - [equals, ":board_type", "cheap"]
        - ["less_than", ":specs/defects_per_metre", 0.1]
      - - AND
        - [equals, ":board_type", "expensive"]
        - ["less_than", ":specs/defects_per_metre", 0.01]

  - comment: "Fail if an unknow board type is given."
  - id: "UNKNOWN_TYPE_FAILURE"
    require: [is_in, ":board_type" [list, "cheap", "expensive"]]

version: 3
```

The last check here catches data validation errors: if the board type is
neither cheap or expensive. Though it is possible this tool is not designed for
data format validation and enforcement at the database level or in the
application with tools like [JSON Schema][], [cue][], and [pydantic][] are
better suited.

[JSON Schema]: https://json-schema.org/
[cue]: https://cuelang.org/
[pydantic]: https://pydantic-docs.helpmanual.io/

## Reporting

The tool works especially well when generating detailed reporting of QC
failures. String interpolation allows showing the cause of the QC failure. In
this example the corresponding message depending on pass or failure of the
threshold rule. These are enabled using either the `--std[err|out]-fmt` flag
value of either `json` or `msg`.

```yaml qc_threshold_example
thresholds:

  - comment: "Density of all boards should be > 10kg / sq.m."
    id: "DENSITY_FAILURE"
    require: ["greater_equal_than", ":specs/density", 10]
    msg:
      pass_msg: "✅ Board {id} density passes QC."
      fail_msg: '❌ Board {id} density fails QC: {spec/density}."'

version: 3
```

This more complex example generates [logfmt][] data. This uses many more data
fields in the interpolation to provide more information about the evaluation.
This could be streamed into an analytics dashboard such as grafana to visualise
QC failures over time. The special field `qc/ts` is the current timestamp of
evaluating the rule.

```yaml
thresholds:

  - comment: "Density of all boards should be > 10kg / sq.m."
    id: "DENSITY_FAILURE"
    require: ["greater_equal_than", ":specs/density", 10]
    msg:
      prefix: "ts={qc/ts} id={id} lot={lot} density={specs/density}"
      pass: 'level=DEBUG qc=pass msg="Board {id} density passes QC."'
      fail: 'level=CRITICAL qc=fail msg="Board {id} density fails QC: {specs/density}."'

version: 3
```

[logfmt]: https://brandur.org/logfmt

## Command Line Options

- `-d`, `--data` <DATA_FILE>: The path to the file containing input data to be
  checked.

- `-t`, `--thresholds` <THRESHOLD_FILE>: The path to the file containing the
  pass/fail thresholds.

- `-o`, `--stdout-fmt`: Can be `short`, `msg`, `json`, `none`, default is `none`.

- `-e`, `--stderr-fmt`: Can be `short`, `msg`, `json`, `none`, default
  is `short`.

## Python API

Auto QC can be used in python code as follows:

```python
from auto_qc import main
evaluation = main.run(thresholds, data)
```

## File Syntax

### Data File

A data file is a YAML/JSON file containing all the data used to make decisions.
This file should contain nested dictionaries. An example data file might look like:

```yaml
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
  current version of auto-qc this should be 3. If the `version` field is
  out of date, e.g. 2, then auto-qc will immediately fail.

- **thresholds** - This field should contain a list of dictionaries, where each
  entry defines a rule that should be evaluated against the metrics in the data
  file. The threshold dictionaries are defined as follows in the next section.

### Evaluated Rules

Use the example data above, a simple threshold file with two business rules
might look like:

```yaml
version: 3.0.0
thresholds:
  - name: Dropping throughput rate
    id: ERR_001
    rule:
      - LESS_THAN
      - ":manufacturing/mean_throughput_per_machine_per_month"
      - 10000

  - name: Increasing defects
    id: ERR_002
    rule:
      - OR
      - [
          GREATER_THAN,
          ":manufacturing/defective_parts_per_million_per_month",
          100,
        ]
      - [GREATER_THAN, :customer/returns_per_month , 10]
```

The first rule 'Dropping throughput rate' checks the value in the data file for
the path `:manufacturing/mean_throughput_per_machine_per_month` ensures it's
greater than `10000`.

The second rule 'Increasing defects' is a compound rule joined by an `OR`
operator, and checks two metrics in the data file to see if either are above a
given threshold file. This second rule illustrates that all business rules are
lists beginning with an operator, and can be arbitrarily nested. The full list of
available operators is given below.

Each evaluation rule dictionary contains:

- **name**: A unique name for this business rule.

- **fail_msg**: A message to generate if this entry QC entry fails. Python
  string interpolation can be used to customise this message with values from
  the data file.

- **pass_msg**: A message to generate if this entry passes. Python string
  interpolation may also be used to customise this message with values from the
  data file.

- **id**: An ID for the kind of failure identified if this entry
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
    tested. The ampersand ':' indicates that this a pointer to a value in the
    data file. The remainder of this string is the JSON path to the value
    to be evaluated against.

  - **literal value** - A literal value that to compare with the reference
    value.

### AVAILABLE OPERATORS

**equals** / **not_equals** - Test whether two values are equal or not.

```yaml
- equals
- ":run_metadata/protocol"
- Low Input DNA
```

**greater_than** / **less_than** / **greater_equal_than** / **less_equal_than** -
Test whether one numeric value is greater/smaller than another.

```yaml
- greater_than
- ":human_contamination/metrics/percent_contamination"
- 5
```

**and** - Test whether two values are both true. The example here illustrates
that metrics can be nested. For instance here, the two arguments to the **and**
operator are themselves thresholds.

```yaml
- and
- - greater_than
  - ":cat_contamination/metrics/percent_contamination"
  - 5
- - greater_than
  - ":dog_contamination/metrics/percent_contamination"
  - 5
```

**or** - Test whether any values are true.

```yaml
- or
- - greater_than
  - ":cat_contamination/metrics/percent_contamination"
  - 5
- - greater_than
  - ":dog_contamination/metrics/percent_contamination"
  - 5
```

**not** - Flips the Boolean value

```yaml
- not
- ":cat_contamination/is_contaminated"
```

**is_in** / **is_not_in** - Test whether a value is in a list of values. Note
that the list of values must begin with the **list** operator.

```yaml
- is_in
- ":cat_contamination/name_of_cat"
- - list
  - "Chase No Face"
  - "Colonel Meow"
  - "Felicette"
  - "Mrs. Chippy"
  - "Peter, the Lord's Cat"
  - "Tiddles"
  - "Wilberforce"
```

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

auto-qc Copyright (c) 2017-2022, The Regents of the University of California,
through Lawrence Berkeley National Laboratory (subject to receipt of any
required approvals from the U.S. Dept. of Energy). All rights reserved.

If you have questions about your rights to use or distribute this software,
please contact Berkeley Lab's Innovation and Partnerships Office at IPO@lbl.gov
referring to "auto-qc v2 (2017-031)."

NOTICE. This software was developed under funding from the U.S. Department of
Energy. As such, the U.S. Government has been granted for itself and others
acting on its behalf a paid-up, nonexclusive, irrevocable, worldwide license in
the Software to reproduce, prepare derivative works, and perform publicly and
display publicly. The U.S. Government is granted for itself and others acting
on its behalf a paid-up, nonexclusive, irrevocable, worldwide license in the
Software to reproduce, prepare derivative works, distribute copies to the
public, perform publicly and display publicly, and to permit others to do so.

## AUTHOR

Michael Barton <mail@michaelbarton.me.uk>

## HISTORY

- 3.0.0 - Mon 08 Feb 2022
- 2.0.0 - Mon 20 Jun 2016
- 1.1.0 - Mon 27 Apr 2015
- 1.0.0 - Fri 15 Aug 2014
- 0.2.1 - Tue 20 May 2014
- 0.2.0 - Mon 19 May 2014
- 0.1.0 - Thu 15 May 2014
