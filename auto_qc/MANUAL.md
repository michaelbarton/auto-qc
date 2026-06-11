# auto-qc

Evaluate a file of metrics against a file of pass/fail rules, and report whether
the metrics pass quality control.

## Synopsis

```
auto-qc --data <DATA_FILE> --thresholds <THRESHOLD_FILE> [--json-output]
```

## Description

`auto-qc` reads two files:

- a **data** file of metrics (plain YAML/JSON), and
- a **thresholds** file of pass/fail rules.

It evaluates every rule against the data. If all rules pass it prints `PASS` and
exits `0`. If any rule fails it prints `FAIL:` followed by the `fail_code` of
each failing rule, and exits `1`. Keeping the rules in a data file lets the
people who own the thresholds change them without changing the code that runs
the check.

## Options

- `-d`, `--data` <DATA_FILE> — Path to the YAML/JSON file of metrics, or `-` for
  standard input.
- `-t`, `--thresholds` <FILE> — Path to the YAML/JSON file of rules, or `-` for
  standard input. Only one of `--data` / `--thresholds` may use stdin at once.
- `-j`, `--json-output` — Print a detailed JSON report instead of PASS/FAIL.
  Each rule includes an `explain` tree describing how it was evaluated.
- `-e`, `--explain` — Print a tree explaining how every rule was evaluated.
- `-T`, `--test` <SUITE_FILE> — Run a suite of test cases against its thresholds
  file.
- `-m`, `--manual` — Print this manual and exit.
- `-V`, `--version` — Print the version and exit.

## Data file

A dictionary of nested metrics. There are no required fields:

```yaml
sample:
  protocol: Low Input DNA
contamination:
  percent_human: 0.4
coverage:
  mean_depth: 18.6
```

## Threshold file

A dictionary with two fields, `version` and `thresholds`:

```yaml
version: 3.0.0
thresholds:
  - name: Coverage too low
    fail_code: LOW_COVERAGE
    rule: ["greater_than", ":coverage/mean_depth", 30]
```

- **version** must match the major version of `auto-qc` being run, or the tool
  exits with an error.
- **thresholds** is a list of rules. Each rule is a dictionary with:
  - **name** (required) — a unique name for the rule.
  - **fail_code** (required) — the code reported when the rule fails.
  - **rule** (required) — the expression to evaluate (see below).
  - **fail_msg** / **pass_msg** (optional) — messages with `{path/to/value}`
    interpolation from the data file.
  - **tags** (optional) — labels returned in the JSON output.

## Rules

A rule is a list beginning with an operator. A string beginning with `:` is a
pointer into the data file; its `/`-separated path locates the value. Rules nest
arbitrarily using the Boolean operators.

A sample passes only when every rule evaluates to `True`.

## Operators

- **equals**, **not_equals** — compare two values for equality.
- **greater_than**, **less_than**, **greater_equal_than**, **less_equal_than** —
  compare two numbers.
- **between** — test that a value is within an inclusive range (`low`, `high`).
- **add**, **subtract**, **multiply**, **divide** — arithmetic on numbers, for
  rules over derived values such as ratios.
- **and**, **or** — combine nested rules.
- **not** — flip a Boolean value.
- **is_in**, **is_not_in** — test membership in a list (written inline).
- **contains** — test that a string or list contains a value.
- **matches**, **starts_with**, **ends_with** — test a string against a regular
  expression, prefix, or suffix.
- **length** — the length of a string or list.

A rule that uses an operator on incompatible types — comparing a number to text,
or to a missing metric — reports a clear error naming the rule, rather than
crashing.

```yaml
- or
- ["greater_than", ":coverage/mean_depth", 30]
- ["greater_than", ":quality/percent_q30", 90]
```

## Exit codes

- `0` — all rules passed.
- `1` — one or more rules failed, or the input files were invalid.

## See also

Full documentation: https://github.com/michaelbarton/auto-qc
