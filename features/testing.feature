Feature: Using the auto-qc tool
  In order to determine whether a sample passes QC
  The auto-qc tool can be used to
  Test quality thresholds

Scenario Outline: Using different comparison operators
  Given I create the file "analysis.yml" with the contents:
   """
   object_1:
     metric_1:
       value: <variable>
   """
  And I create the file "threshold.yml" with the contents:
   """
   version: 3.0.0
   thresholds:
   - name: example test
     fail_msg: fails
     pass_msg: passes
     fail_code: ERR
     rule:
       - <operator>
       - :object_1/metric_1/value
       - <literal>
   """
  When I run the command "../bin/auto-qc" with the arguments:
     | key              | value         |
     | --data           | analysis.yml  |
     | --thresholds     | threshold.yml |
  Then the standard error should be empty
  And the exit code should be <exit>
  And the standard out should contain:
    """
    <result>

    """

Examples: Operators
  | variable | operator           | literal      | result | exit |
  | 1        | greater_than       | 0            | PASS   | 0    |
  | 1        | greater_than       | 2            | FAIL   | 1    |
  | 1        | less_than          | 2            | PASS   | 0    |
  | 1        | less_than          | 0            | FAIL   | 1    |
  | 1        | greater_equal_than | 0            | PASS   | 0    |
  | 1        | greater_equal_than | 2            | FAIL   | 1    |
  | 1        | less_equal_than    | 2            | PASS   | 0    |
  | 1        | less_equal_than    | 0            | FAIL   | 1    |
  | 1        | greater_equal_than | 1            | PASS   | 0    |
  | 1        | less_equal_than    | 1            | PASS   | 0    |
  | True     | and                | True         | PASS   | 0    |
  | False    | and                | True         | FAIL   | 1    |
  | True     | and                | False        | FAIL   | 1    |
  | False    | and                | False        | FAIL   | 1    |
  | True     | or                 | True         | PASS   | 0    |
  | False    | or                 | True         | PASS   | 0    |
  | True     | or                 | False        | PASS   | 0    |
  | False    | or                 | False        | FAIL   | 1    |
  | 1        | not_equals         | 1            | FAIL   | 1    |
  | 2        | not_equals         | 1            | PASS   | 0    |
  | 1        | equals             | 1            | PASS   | 0    |
  | 2        | equals             | 1            | FAIL   | 1    |
  | A        | is_in              | [list, A, B] | PASS   | 0    |
  | C        | is_in              | [list, A, B] | FAIL   | 1    |
  | A        | is_not_in          | [list, A, B] | FAIL   | 1    |
  | C        | is_not_in          | [list, A, B] | PASS   | 0    |

Scenario: Using the unary not operator
  Given I create the file "analysis.yml" with the contents:
   """
   object_1:
     metric_1:
       value: true
   """
  And I create the file "threshold.yml" with the contents:
   """
   version: 3.0.0
   thresholds:
   - name: example test
     fail_msg: fails
     pass_msg: passes
     fail_code: ERR
     rule:
       - not
       - :object_1/metric_1/value
   """
  When I run the command "../bin/auto-qc" with the arguments:
     | key              | value         |
     | --data           | analysis.yml  |
     | --thresholds     | threshold.yml |
  Then the standard error should be empty
  And the exit code should be 1
  And the standard out should contain:
    """
    FAIL

    """

Scenario Outline: Testing multiple different thresholds
  Given I create the file "analysis.yml" with the contents:
   """
   object_1:
     metric_1:
       value: <var_1>
   object_2:
     metric_2:
       value: <var_2>
   """
  And I create the file "threshold.yml" with the contents:
   """
   version: 3.0.0
   thresholds:
   - name: example test 1
     fail_msg: fails
     pass_msg: passes
     fail_code: ERR
     rule:
       - 'greater_than'
       - ':object_1/metric_1/value'
       - <lit_1>
   - name: example test 2
     fail_msg: fails
     pass_msg: passes
     fail_code: ERR
     rule:
       - 'greater_than'
       - ':object_2/metric_2/value'
       - <lit_2>
   """
  When I run the command "../bin/auto-qc" with the arguments:
    | key              | value         |
    | --data           | analysis.yml  |
    | --thresholds     | threshold.yml |
  Then the standard error should be empty
  And the exit code should be <exit>
  And the standard out should contain:
    """
    <result>

    """

Examples: Operators
  | var_1 | lit_1 | var_2 | lit_2 | result | exit |
  | 1     | 0     | 1     | 0     | PASS   | 0    |
  | 1     | 0     | 0     | 1     | FAIL   | 1    |
  | 0     | 1     | 1     | 0     | FAIL   | 1    |
  | 0     | 1     | 0     | 1     | FAIL   | 1    |

Scenario Outline: Using nested thresholds
  Given I create the file "analysis.yml" with the contents:
   """
   object_1:
     metric_1:
       value: <var_1>
   """
  And I create the file "threshold.yml" with the contents:
   """
   version: 3.0.0
   thresholds:
   - name: example test 1
     fail_msg: fails
     pass_msg: passes
     fail_code: ERR
     rule:
       - and
       - - 'greater_than'
         - :object_1/metric_1/value
         - <lit_1>
       - - 'greater_than'
         - :object_1/metric_1/value
         - <lit_2>
   """
  When I run the command "../bin/auto-qc" with the arguments:
    | key              | value         |
    | --data           | analysis.yml  |
    | --thresholds     | threshold.yml |
  Then the standard error should be empty
  And the exit code should be <exit>
  And the standard out should contain:
    """
    <result>

    """

Examples: Operators
  | var_1 | lit_1 | lit_2 | result | exit |
  | 1     | 0     | 0     | PASS   | 0    |
  | 1     | 0     | 1     | FAIL   | 1    |
  | 1     | 1     | 0     | FAIL   | 1    |
  | 1     | 1     | 1     | FAIL   | 1    |
