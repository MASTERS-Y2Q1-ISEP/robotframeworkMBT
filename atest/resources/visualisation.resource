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

test suite ${suite} contains trace info ${ti}
    [Documentation]     Check that test suite and trace_info exist
    ...     :IN: suite, trace_info
    ...     :OUT: None
    Variable Should Exist   ${suite}
    Variable Should Exist   ${trace_info}

test suite ${suite} is exported to json
    [Documentation]     Check that test suite and trace_info exist
    ...     :IN: suite, trace_info
    ...     :OUT: json file 
    Variable Should Exist   ${suite}
    Variable Should Exist   ${trace_info}
    
    ${filepath} =   Export to JSON      ${suite}    ${trace_info}
    Set Suite Variable  ${filepath}

the file ${filename} exists
    [Documentation]     Check that a file with ${filename} exists
    ...     :IN: filepath
    ...     :OUT: None 
    Variable Should Exist   ${filepath}

    ${result} =     Check File Exists   ${filepath}
    Should Be Equal     ${result}   file exists

${filename} is imported
    [Documentation]     import trace info from json file
    ...     :IN: filepath
    ...     :OUT: new_trace_info
    Variable Should Exist   ${filepath}
    
    ${new_trace_info} =     Import JSON File    ${filepath}
    Set Suite Variable      ${new_trace_info}

trace info from ${filename} is the same as trace info ${trace}
    [Documentation]     Check that trace_info and new_trace_info contain the same information
    ...     :IN: new_trace_info, trace_info
    ...     :OUT: flag_cleanup
    Variable Should Exist   ${trace_info}
    Variable Should Exist   ${new_trace_info}

    ${result} =     Compare Trace Info   ${trace_info}      ${new_trace_info}
    Should Be Equal     ${result}   imported model equals exported model
    Set Suite Variable      ${flag_cleanup}     True

${filename} is deleted
    [Documentation]     delete file with ${filename}
    ...     :IN: filepath, flag_cleanup
    ...     :OUT: json file does not exist
    Variable Should Exist   ${filepath}
    Variable Should Exist   ${flag_cleanup}
    
    Delete JSON File    ${filepath}

${filename} does not exist
    [Documentation]     check that file is deleted
    ...     :IN: filepath
    ...     :OUT: None
    Variable Should Exist   ${filepath}

    ${result} =     Check File Exists   ${filepath}
    Should Be Equal     ${result}   file does not exist

