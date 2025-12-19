*** Settings ***
Resource          ../../resources/visualisation.resource
Library           robotmbt    processor=echo

*** Test Cases ***
Create test suite
    Given test suite s
    Then test suite s has trace info t
    and trace info t has current trace c 
    and current trace c has a tuple 'scenario i, state p: v=1'
    and current trace c has a tuple 'scenario j, state p: v=2'
    and trace info t has all traces a
    and all traces a has list l
    and list l has a tuple 'scenario i, state p: v=2'

Load json file into robotmbt 
    Given test suite s with flag from_json=atest_resource