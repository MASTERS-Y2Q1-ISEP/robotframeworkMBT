*** Settings ***
Documentation     Export and import a test suite from and to JSON
...               and check that the imported suite equals the 
...               exported suite.
Suite Setup       Treat this test suite Model-based     graph=scenario
Resource          ../../resources/visualisation.resource
Library           robotmbt

*** Test Cases ***
Scenario graph
    Given test suite s has trace info t
    When the algorithm inserts a
    and the algorithm inserts b
    and the algorithm inserts c
    and the algorithm inserts d
    and the algorithm inserts e
    and the graph of type scenario is generated
    Then the scenario graph contains vertices start, a, b, c, d, e
