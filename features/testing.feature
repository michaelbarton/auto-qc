Feature: Using the auto-qc tool
  In order to determine whether a sample passes QC
  The auto-qc tool can be used to
  Test quality thresholds

  Scenario Outline: Threshold operators
   Given I create the file "analysis.yml" with the contents:
     """
     - analysis: object_1
       outputs:
         metric_1:
           value: <variable>
     """
     And I create the file "threshold.yml" with the contents:
     """
     metadata:
       version:
         auto-qc: 0.3.0
     thresholds:
     -
       - <operator>
       - :object_1/metric_1/value
       - <literal>
     """
    When I run the command "auto-qc" with the arguments:
       | key              | value         |
       | --analysis_file  | analysis.yml  |
       | --threshold_file | threshold.yml |
   Then the standard error should be empty
    And the exit code should be 0
    And the standard out should contain:
      """
      <result>

      """

  Examples: Operators
      | variable | operator     | literal | result |
      | 1        | greater_than | 0       | FAIL   |
      | 1        | greater_than | 2       | PASS   |
      | 1        | less_than    | 2       | FAIL   |
      | 1        | less_than    | 0       | PASS   |
      | True     | and          | True    | FAIL   |
      | False    | and          | True    | PASS   |
      | True     | and          | False   | PASS   |
      | False    | and          | False   | PASS   |
      | True     | or           | True    | FAIL   |
      | False    | or           | True    | FAIL   |
      | True     | or           | False   | FAIL   |
      | False    | or           | False   | PASS   |

  Scenario Outline: Multiple thresholds
   Given I create the file "analysis.yml" with the contents:
     """
     - analysis: object_1
       outputs:
         metric_1:
           value: <var_1>
     - analysis: object_2
       outputs:
         metric_2:
           value: <var_2>
     """
     And I create the file "threshold.yml" with the contents:
     """
     metadata:
       version:
         auto-qc: 0.3.0
     thresholds:
     - [greater_than, ':object_1/metric_1/value', <lit_1>]
     - [greater_than, ':object_2/metric_2/value', <lit_2>]
     """
    When I run the command "auto-qc" with the arguments:
       | key              | value         |
       | --analysis_file  | analysis.yml  |
       | --threshold_file | threshold.yml |
   Then the standard error should be empty
    And the exit code should be 0
    And the standard out should contain:
      """
      <result>

      """

  Examples: Operators
      | var_1 | lit_1 | var_2 | lit_2 | result |
      | 1     | 0     | 1     | 0     | FAIL   |
      | 1     | 0     | 0     | 1     | FAIL   |
      | 0     | 1     | 1     | 0     | FAIL   |
      | 0     | 1     | 0     | 1     | PASS   |
