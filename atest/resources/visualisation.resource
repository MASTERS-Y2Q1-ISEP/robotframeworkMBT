*** Settings ***
Documentation     Resource file for testing the visualisation of RobotMBT
Library           atest.resources.helpers.scenariogenerator.ScenarioGenerator
Library           Collections


*** Keywords ***
Test Suite ${suite} exists
    [Documentation]    Makes a test suite
    ...    :IN: suite = ${suite}
    ...    :OUT: None
    Set Suite Variable    ${suite}

Test Suite ${suite} has ${count} scenarios
    [Documentation]    Makes a test suite
    ...    :IN: scenario_count = ${count}, suite = ${suite}
    ...    :OUT: None
    # use customer ScenarioGenerator.py to generate some scenarios
    
    ${scenarios} =    Generate Scenarios    ${count}
    Set Suite Variable    ${scenarios}    # Store scenarios as a suite variable
    Log    Generated scenarios: ${scenarios}

Graph ${graph} is generated based on Test Suite ${suite}
     [Documentation]    Generates the graph 
    ...    :IN: graph = ${graph}, suite = ${suite}
    ...    :OUT: None
    # the actual function Visualiser
    # Call Method    Visualiser    visualise    ${graph}
    ${emptylist} =        Create List
    Set Suite Variable    ${graph.vertices}    ${emptylist}    

Graph ${graph} contains ${number} vertices
    [Documentation]    Verifies that the graph contains the specified number of vertices.
    ...    :IN: graph = ${graph}, number = ${number}
    ...    :OUT: None
    ${vertex_count} =    Get Length   ${graph.vertices}
    Should Be Equal As Integers       ${vertex_count}    ${number}


