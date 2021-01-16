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
   - - name: example test
       fail_msg: fails
       pass_msg: passes
       fail_code: ERR00001
       tags: ["contamination"]
     - 'greater_than'
     - :value
     - <literal>
   """
  When I run the command "../bin/auto-qc" with the arguments:
     | key              | value         |
     | --data           | analysis.yml  |
     | --thresholds     | threshold.yml |
     | --json-output    |               |
  Then the standard error should be empty
  And the exit code should be 0
  And the JSON-format standard out should equal:
    """
    {
        "auto_qc_version": "3.0.0",
        "fail_codes": <code>,
        "pass": <pass>,
        "qc": [
            {
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
  | literal | pass   | msg    | code         |
  | 0       | true   | passes | []           |
  | 2       | false  | fails  | ["ERR00001"] |
