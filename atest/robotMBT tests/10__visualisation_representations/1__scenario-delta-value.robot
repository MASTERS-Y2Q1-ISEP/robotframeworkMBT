*** Settings ***   
Library           robotmbt    processor=flatten

*** Test Cases ***
Vertex Scenario-Delta-Value graph
    Given test suite s has a trace with 2 steps
    When scenario-delta-value graph g is generated
    Then graph g contains vertex 'start'
    And graph g contains vertex 'A1' with text "attr: states = ['a1'], special='!'"
    And graph g contains vertex 'A2' with text "attr: states = ['a1', 'a2']"
    And graph g does not contain vertex 'A2' with text "attr: states = ['a1', 'a2'], special='!'"