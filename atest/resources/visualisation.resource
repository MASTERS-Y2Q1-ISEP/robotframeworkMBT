*** Settings ***
Documentation     Resource file for testing the visualisation of RobotMBT
Library           atest.resources.helpers.modelgenerator.ModelGenerator
Library           Collections


*** Keywords ***
test suite ${suite}
    [Documentation]     Makes a new test suite
    ...     :IN: None
    ...     :OUT: new suite
    Set Suite Variable  ${suite}

test suite ${suite} has trace info ${trace}
    [Documentation]     Adds trace info to test suite
    ...     :In: suite
    ...     :Out: new trace_info
    Variable Should Exist    ${suite}

    ${trace_info} =         Generate Trace Information
    Set Suite Variable  ${trace_info}
    
trace info ${trace} has current trace ${current}
    [Documentation]     Step for readability
    ...     :In: trace_info
    ...     :Out: None
    Variable Should Exist    ${trace_info}

current trace ${current_trace} has a tuple 'scenario ${scenario}, state ${state}'
    [Documentation]    Add (scenario, state) to current trace
    ...     :In: trace_info
    ...     :Out: trace_info
    Variable Should Exist   ${trace_info}

    ${trace_info} =         Current Trace Contains  ${trace_info}   ${scenario}     ${state}
    Set Suite Variable  ${trace_info}

trace info ${trace} has all traces ${all}
    [Documentation]     Step for readability
    ...     :In: trace_info
    ...     :Out: None
    Variable Should Exist    ${trace_info}

all traces ${all} has list ${list}
    [Documentation]    Add empty list to all traces
    ...     :In: trace_info
    ...     :Out: trace_info
    Variable Should Exist   ${trace_info}

    ${trace_info} =         All Traces Contains List  ${trace_info}
    Set Suite Variable  ${trace_info}

list ${list} has a tuple 'scenario ${scenario}, state ${state}'
    [Documentation]    Add (scenario, state) to the first trace of all traces
    ...     :In: trace_info
    ...     :Out: trace_info
    Variable Should Exist   ${trace_info}

    ${trace_info} =         All Traces Contains  ${trace_info}   ${scenario}     ${state}
    Set Suite Variable  ${trace_info}










test suite ${suite} with flag from_json=${file}
    [Documentation]     Makes a test suite with the flag from_json=file
    ...     :IN: None
    ...     :OUT: new suite, new file
    Set Suite Variable  ${suite}
    Set Suite Variable  ${file}

