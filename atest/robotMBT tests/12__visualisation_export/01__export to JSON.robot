*** Settings ***
Documentation     Export and import a test suite from and to JSON
...               and check that the imported suite equals the 
...               exported suite.
Suite Setup       Treat this test suite Model-based     graph=scenario-state
Resource          ../../resources/visualisation.resource
Library           robotmbt

*** Test Cases ***
Setup
    Given test suite s has trace info t
    When the algorithm inserts 'A1' with state "attr: states = ['a1'], special='!'"
    And the algorithm inserts 'A2' with state "attr: states = ['a1', 'a2'], special='!'"
    Then test suite s has a trace with 2 steps

Backtrack and Insert
  Given test suite s has 2 steps in its current trace  
  When the algorithm backtracks by 1 step
  And the algorithm inserts 'B1' with state 'attr: states=['a1', 'b1'], special='!''
  Then test suite s has 2 total traces