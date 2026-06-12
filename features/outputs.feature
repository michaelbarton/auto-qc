Feature: Printing different output formats
  In order to visualise the QC results
  The auto-qc tool can generate different output formats

Scenario Outline: Generating JSON formatted output
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
     fail_code: ERR00001
     tags: ["contamination"]
     rule:
       - 'greater_than'
       - :value
       - <literal>
   """
  When I run the command "auto-qc" with the arguments:
     | key              | value         |
     | --data           | analysis.yml  |
     | --thresholds     | threshold.yml |
     | --json-output    |               |
  Then the standard error should be empty
  And the exit code should be <exit>
  And the JSON-format standard out should equal:
    """
    {
        "auto_qc_version": "3.0.0",
        "fail_codes": <code>,
        "pass": <pass>,
        "qc": [
            {
                "explain": {
                    "operator": "greater_than",
                    "result": <pass>,
                    "args": [
                        {"variable": ":value", "value": 2},
                        {"literal": <literal>}
                    ]
                },
                "fail_code": "ERR00001",
                "message": "<msg>",
                "name": "example test",
                "pass": <pass>,
                "tags": ["contamination"]
            }
        ]
    }

    """

Examples: Outputs
  | literal | pass   | msg    | code         | exit |
  | 0       | true   | passes | []           | 0    |
  | 2       | false  | fails  | ["ERR00001"] | 1    |

Scenario: Explaining how a rule was evaluated
  Given I create the file "analysis.yml" with the contents:
   """
   coverage:
     mean_depth: 18.6
   """
  And I create the file "threshold.yml" with the contents:
   """
   version: 3.0.0
   thresholds:
   - name: Coverage too low
     fail_code: LOW_COVERAGE
     rule:
       - greater_than
       - :coverage/mean_depth
       - 30
   """
  When I run the command "auto-qc" with the arguments:
     | key              | value         |
     | --data           | analysis.yml  |
     | --thresholds     | threshold.yml |
     | --explain        |               |
  Then the exit code should be 1
  And the standard out should contain:
    """
    Coverage too low
    """
  And the standard out should contain:
    """
    LOW_COVERAGE
    """
  And the standard out should contain:
    """
    18.6
    """

Scenario: Reporting how close a rule is to flipping
  Given I create the file "analysis.yml" with the contents:
   """
   coverage:
     mean_depth: 30.1
   """
  And I create the file "threshold.yml" with the contents:
   """
   version: 3.0.0
   thresholds:
   - name: Coverage too low
     fail_code: LOW_COVERAGE
     rule:
       - greater_than
       - :coverage/mean_depth
       - 30
   """
  When I run the command "auto-qc" with the arguments:
     | key              | value         |
     | --data           | analysis.yml  |
     | --thresholds     | threshold.yml |
     | --margin         |               |
  Then the exit code should be 0
  And the standard out should contain:
    """
    slack 0.1
    """
