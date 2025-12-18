*** Settings ***
Resource          ../../resources/visualisation.resource
Library           robotmbt    processor=echo

*** Test Cases ***
Load json file into robotmbt 
    Given test suite s with flag from_json=atest_resource
    When test suite s is processed
    Then test suite s has trace info t
    Then trace info t has current trace c 
    Then current trace c has a tuple of scenario a, state p: v=1
    Then current trace c has a tuple of scenario b, state p: v=2
    Then trace info t has all traces a
    Then all traces a has a list with a tuple with scenario a and state p: v=2