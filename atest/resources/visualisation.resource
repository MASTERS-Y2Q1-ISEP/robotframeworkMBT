*** Settings ***
Documentation     Resource file for testing the visualisation of RobotMBT
Library           atest.resources.helpers.modelgenerator.ModelGenerator
Library           Collections


*** Keywords ***
test suite ${suite} with flag from_json=${file}
    [Documentation]     Makes a test suite with the flag from_json=file
    ...     :IN: None
    ...     :OUT: new suite, new file
    Set Suite Variable  ${suite}
    Set Suite Variable  ${file}

test suite ${suite} is processed
    [Documentation]     Processes test suite with flag from_json
    ...     :In: suite, file
    ...     :Out:  new trace_info
    Variable Should Exist    ${file}
    
    ${trace_info} =    Test Suite From JSON    ${file}
    Set Suite Variable  ${trace_info}

test suite ${suite} has trace info ${trace}
    [Documentation]     Check that trace_info has been generated
    ...     :In: trace_info
    ...     :Out: trace_info
    Variable Should Exist    ${trace_info}

trace info ${trace} has current trace ${current}
    [Documentation]     Get current trace from trace info
    ...     :In: trace_info
    ...     :Out: new current_trace
    Variable Should Exist    ${trace_info}

    ${current_trace} =      Get Current Trace From TraceInfo    ${trace_info}
    Set Suite Variable  ${current_trace}

current trace ${c} has a tuple of scenario ${scenario}, state ${state}
    Variable Should Exist   ${current_trace}
    
    


