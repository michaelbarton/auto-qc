Feature: Using the auto-qc tool
  In order to determine whether a sample passes QC
  The auto-qc tool can be used to
  Test quality thresholds

Scenario Outline: Using different comparison operators
  Given I create the file "analysis.yml" with the contents:
   """
   metadata:
   data:
     object_1:
       metric_1:
         value: <variable>
   """
  And I create the file "threshold.yml" with the contents:
   """
   metadata:
     version:
       auto-qc: 3.0.0
   thresholds:
   -
     - name: example test
       fail_msg: fails
       pass_msg: passes
       fail_code: ERR
     - <operator>
     - :object_1/metric_1/value
     - <literal>
   """
  When I run the command "../bin/auto-qc" with the arguments:
     | key              | value         |
     | --analysis-file  | analysis.yml  |
     | --threshold-file | threshold.yml |
  Then the standard error should be empty
  And the exit code should be 0
  And the standard out should contain:
    """
    <result>

    """

Examples: Operators
  | variable | operator           | literal      | result |
  | 1        | greater_than       | 0            | PASS   |
  | 1        | greater_than       | 2            | FAIL   |
  | 1        | less_than          | 2            | PASS   |
  | 1        | less_than          | 0            | FAIL   |
  | 1        | greater_equal_than | 0            | PASS   |
  | 1        | greater_equal_than | 2            | FAIL   |
  | 1        | less_equal_than    | 2            | PASS   |
  | 1        | less_equal_than    | 0            | FAIL   |
  | 1        | greater_equal_than | 1            | PASS   |
  | 1        | less_equal_than    | 1            | PASS   |
  | True     | and                | True         | PASS   |
  | False    | and                | True         | FAIL   |
  | True     | and                | False        | FAIL   |
  | False    | and                | False        | FAIL   |
  | True     | or                 | True         | PASS   |
  | False    | or                 | True         | PASS   |
  | True     | or                 | False        | PASS   |
  | False    | or                 | False        | FAIL   |
  | 1        | not_equals         | 1            | FAIL   |
  | 2        | not_equals         | 1            | PASS   |
  | 1        | equals             | 1            | PASS   |
  | 2        | equals             | 1            | FAIL   |
  | A        | is_in              | [list, A, B] | PASS   |
  | C        | is_in              | [list, A, B] | FAIL   |
  | A        | is_not_in          | [list, A, B] | FAIL   |
  | C        | is_not_in          | [list, A, B] | PASS   |

Scenario: Using the unary not operator
  Given I create the file "analysis.yml" with the contents:
   """
   metadata:
   data:
     object_1:
       metric_1:
         value: true
   """
  And I create the file "threshold.yml" with the contents:
   """
   metadata:
     version:
       auto-qc: 3.0.0
   thresholds:
   -
     - name: example test
       fail_msg: fails
       pass_msg: passes
       fail_code: ERR
     - not
     - :object_1/metric_1/value
   """
  When I run the command "../bin/auto-qc" with the arguments:
     | key              | value         |
     | --analysis-file  | analysis.yml  |
     | --threshold-file | threshold.yml |
  Then the standard error should be empty
  And the exit code should be 0
  And the standard out should contain:
    """
    FAIL

    """

Scenario Outline: Testing multiple different thresholds
  Given I create the file "analysis.yml" with the contents:
   """
   metadata:
   data:
     object_1:
       metric_1:
         value: <var_1>
     object_2:
       metric_2:
         value: <var_2>
   """
  And I create the file "threshold.yml" with the contents:
   """
   metadata:
     version:
       auto-qc: 3.0.0
   thresholds:
   - - name: example test 1
       fail_msg: fails
       pass_msg: passes
       fail_code: ERR
     - 'greater_than'
     - ':object_1/metric_1/value'
     - <lit_1>
   - - name: example test 2
       fail_msg: fails
       pass_msg: passes
       fail_code: ERR
     - 'greater_than'
     - ':object_2/metric_2/value'
     - <lit_2>
   """
  When I run the command "../bin/auto-qc" with the arguments:
     | key              | value         |
     | --analysis-file  | analysis.yml  |
     | --threshold-file | threshold.yml |
  Then the standard error should be empty
  And the exit code should be 0
  And the standard out should contain:
    """
    <result>

    """

Examples: Operators
  | var_1 | lit_1 | var_2 | lit_2 | result |
  | 1     | 0     | 1     | 0     | PASS   |
  | 1     | 0     | 0     | 1     | FAIL   |
  | 0     | 1     | 1     | 0     | FAIL   |
  | 0     | 1     | 0     | 1     | FAIL   |

Scenario Outline: Using nested thresholds
  Given I create the file "analysis.yml" with the contents:
   """
   metadata:
   data:
     object_1:
       metric_1:
         value: <var_1>
   """
  And I create the file "threshold.yml" with the contents:
   """
   metadata:
     version:
       auto-qc: 3.0.0
   thresholds:
   -
     - name: example test 1
       fail_msg: fails
       pass_msg: passes
       fail_code: ERR
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
     | --analysis-file  | analysis.yml  |
     | --threshold-file | threshold.yml |
  Then the standard error should be empty
  And the exit code should be 0
  And the standard out should contain:
    """
    <result>

    """

Examples: Operators
  | var_1 | lit_1 | lit_2 | result |
  | 1     | 0     | 0     | PASS   |
  | 1     | 0     | 1     | FAIL   |
  | 1     | 1     | 0     | FAIL   |
  | 1     | 1     | 1     | FAIL   |
