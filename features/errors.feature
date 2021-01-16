Feature: Error messages for incorrect use of auto-qc
  In order to correctly use the auto-qc tool
  The auto-qc provides useful errors
  So that the user use the modify their usage

Scenario: The given analysis file does not exist
  Given I create the file "thresholds.yml"
  When I run the command "../bin/auto-qc" with the arguments:
     | key              | value          |
     | --data           | none           |
     | --thresholds     | thresholds.yml |
  Then the standard error should contain:
    """
    Invalid value for '--data' / '-d': Path 'none' does not exist
    """
  And the exit code should be non-zero

Scenario: The given thresholds file does not exist
  Given I create the file "analysis.yml"
  When I run the command "../bin/auto-qc" with the arguments:
     | key              | value         |
     | --data           | analysis.yml  |
     | --thresholds     | none          |
  Then the standard error should contain:
    """
    Invalid value for '--thresholds' / '-t': Path 'none' does not exist

    """
  And the exit code should be non-zero

Scenario Outline: Incompatible threshold file version number
  Given I create the file "analysis.yml" with the contents:
   """
   metric_1:
     val: 1
   """
  And I create the file "threshold.yml" with the contents:
   """
   version: <version>
   thresholds: []
   """
  When I run the command "../bin/auto-qc" with the arguments:
     | key              | value         |
     | --data           | analysis.yml  |
     | --thresholds     | threshold.yml |
  Then the standard out should be empty
  And the exit code should be 1
  And the standard error should contain:
    """
    Incompatible threshold file syntax: <version>.
    Please update the syntax to version >= 3.0.0.

    """

Examples: Versions
  | version |
  | 0       |
  | 0.1     |
  | 0.1.2   |
  | 1.0.0   |

Scenario Outline: The given value does not exist
  Given I create the file "analysis.yml" with the contents:
   """
   metric_1:
     val: 1
   """
  And I create the file "threshold.yml" with the contents:
   """
   version: 3.0.0
   thresholds:
   - name: example
     fail_code: ERR_1
     rule:
     - <operator>
     - <variable>
     - 1
   """
  When I run the command "../bin/auto-qc" with the arguments:
     | key              | value         |
     | --data           | analysis.yml  |
     | --thresholds     | threshold.yml |
  Then the standard out should be empty
  And the standard error should equal:
    """
    Errors:
    <error>

    """
  And the exit code should be 1

Examples: Errors
  | operator     | variable            | error                                                        |
  | greater_than | :metric_1/non_value | No matching metric path ':metric_1/non_value' found in data. |
  | unknown      | :metric_1/val       | Unknown operator 'unknown.'                                  |

Scenario: A QC entry is missing a failure code
  Given I create the file "analysis.yml" with the contents:
   """
   value: 2
   """
  And I create the file "threshold.yml" with the contents:
   """
   version: 3.0.0
   thresholds:
   - name: example test
     fail_msg: fails
     pass_msg: passes
     rule:
     - 'greater_than'
     - :value
     - 2
   """
  When I run the command "../bin/auto-qc" with the arguments:
    | key              | value         |
    | --data           | analysis.yml  |
    | --thresholds     | threshold.yml |
  Then the standard out should be empty
  And the standard error should equal:
    """
    Errors:
    The QC entry 'example test' is missing a failure code

    """
  And the exit code should be 1
