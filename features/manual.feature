Feature: Showing the auto-qc manual
  In order to see how to use auto-qc
  The auto-qc tool should support a manual `--manual / -m` flag

Scenario: Generating JSON formatted output
  When I run the command "../bin/auto-qc --manual"
  Then the standard out should not be empty
  And the standard error should be empty
  And the exit code should be 0
