Feature: Testing thresholds with a suite of cases
  In order to trust QC rules the way I trust code
  The auto-qc tool can run a suite of test cases
  And report which cases disagree with the rules

  Background:
    Given I create the file "thresholds.yml" with the contents:
     """
     version: 3.0.0
     thresholds:
     - name: Coverage too low
       fail_code: LOW_COVERAGE
       rule: ["greater_than", ":coverage/mean_depth", 30]
     """

  Scenario: A suite where every case agrees with the rules
    Given I create the file "qc_tests.yml" with the contents:
     """
     thresholds: thresholds.yml
     cases:
       - name: healthy sample
         data:
           coverage: { mean_depth: 40 }
         expect: pass
       - name: low coverage is flagged
         data:
           coverage: { mean_depth: 5 }
         expect: fail
         codes: [LOW_COVERAGE]
     """
    When I run the command "auto-qc" with the arguments:
       | key      | value         |
       | --test   | qc_tests.yml  |
    Then the exit code should be 0
    And the standard out should contain:
      """
      2 passed
      """

  Scenario: A suite with a case the rules disagree with
    Given I create the file "qc_tests.yml" with the contents:
     """
     thresholds: thresholds.yml
     cases:
       - name: this sample should pass
         data:
           coverage: { mean_depth: 5 }
         expect: pass
     """
    When I run the command "auto-qc" with the arguments:
       | key      | value         |
       | --test   | qc_tests.yml  |
    Then the exit code should be 1
    And the standard out should contain:
      """
      expected PASS, got FAIL (LOW_COVERAGE)
      """
