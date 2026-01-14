*** Settings ***
Documentation     Resource file for testing the visualisation of RobotMBT
Library           atest.resources.helpers.modelgenerator.ModelGenerator
Library           Collections


*** Keywords ***
test suite ${suite}
    [Documentation]     *model info*
    ...     :IN: new trace_info | trace_info.current_trace=0 | trace_info.all_traces=0
    ...     :OUT: None
    ${trace_info} =     Generate Trace Information
    Set Suite Variable  ${trace_info}

test suite ${suite} has trace info ${trace}
    [Documentation]     *model info*
    ...     :IN: new trace_info | trace_info.current_trace=0 | trace_info.all_traces=0
    ...     :OUT: None
    ${trace_info} =     Generate Trace Information
    Set Suite Variable  ${trace_info}

the algorithm inserts '${scenario_name}' with state "${state_str}"
    [Documentation]    *model info*
    ...    :IN: trace_info
    ...    :OUT: trace_info.current_trace+=1
    Variable Should Exist    ${trace_info}
    ${trace_info} =    The Algorithm Inserts    ${trace_info}    ${scenario_name}    ${state_str}

test suite ${suite} has a trace with ${n} steps
    [Documentation]    *model info*
    ...    :IN: trace_info.current_trace==${n}
    ...    :OUT: trace_info.current_trace==${n}
    No operation

test suite ${suite} has ${n} steps in its current trace 
    [Documentation]    *model info*
    ...    :IN: trace_info.current_trace==${n}
    ...    :OUT: trace_info.current_trace==${n}
    No operation

test suite ${suite} has ${n} total traces
    [Documentation]    *model info*
    ...    :IN: trace_info.current_trace | trace_info.all_traces==${n}-1
    ...    :OUT: trace_info.current_trace | trace_info.all_traces==${n}-1
    No operation

${graph_type} graph ${name} is generated
    [Documentation]    *model info*
    ...    :IN: trace_info
    ...    :OUT: graph.name=${name}, graph.type=${graph_type}
    Variable Should Exist    ${trace_info}

    ${graph} =  Get Graph   ${trace_info}   ${graph_type}
    Set Suite Variable  ${graph}

graph ${name} contains vertex '${scenario}'
    [Documentation]    *model info*
    ...    :IN: graph.name=${name}
    ...    :OUT: graph.name=${name}
    Variable Should Exist    ${graph}

    ${result} =     Graph Contains No Text        ${graph}      ${scenario}
    Should be Equal     ${result}       Graph contains ${scenario}

graph ${name} contains vertex '${scenario}' with text "${text}"
    [Documentation]    *model info*
    ...    :IN: graph.name=${name}
    ...    :OUT: graph.name=${name}
    Variable Should Exist    ${graph}

    ${result} =     Graph Contains Vertex With Text        ${graph}      ${scenario}       ${text}
    Run Keyword If      "${result}" == "None"
    ...    Fail     Fail: Graph does not contain '${scenario}' with "${text}"

graph ${name} does not contain vertex '${scenario}' with text "${text}"
    [Documentation]    *model info*
    ...    :IN: graph.name=${name}
    ...    :OUT: graph.name=${name}
    Variable Should Exist    ${graph}

    ${result} =     Graph Contains Vertex With Text        ${graph}      ${scenario}       ${text}
    Run Keyword If      "${result}" != "None"
    ...    Fail     Fail: Graph contains '${scenario}' with "${text}"
    
graph ${name} has an edge from vertex '${start_title}' to ${vertex}'${end_title}'
    [Documentation]    *model_info*
    ...    :IN: graph.name=${name}
    ...    :OUT: graph.name=${name}
    Variable Should Exist    ${graph}
    ${start_node} =    Graph Contains Vertex With Text    ${graph}    ${start_title}
    ${end_node} =    Graph Contains Vertex With Text    ${graph}    ${end_title}
    
    Should Not Be Equal    ${start_node}    ${None}    Start node with title '${start_title}' not found
    Should Not Be Equal    ${end_node}    ${None}    End node with title '${end_title}' not found
    
    ${result} =    Vertices Are Connected    ${graph}    ${start_node}    ${end_node}
    Run Keyword If    ${result} != True
    ...     Fail    Fail: Edges '${start_title}' and '${end_title}' exist in graph but are not connected!

graph ${name} does not have an edge from ${vertex}'${start_title}' to ${vertex}'${end_title}'
    [Documentation]    *model_info*
    ...    :IN: graph.name=${name}
    ...    :OUT: graph.name=${name}
    Variable Should Exist    ${graph}
    ${start_node} =    Graph Contains Vertex With Text    ${graph}    ${start_title}
    ${end_node} =    Graph Contains Vertex With Text    ${graph}    ${end_title}
    
    ${result} =    Vertices Are Connected    ${graph}    ${start_node}    ${end_node}
    Run Keyword If    ${result} == True
    ...     Fail    Fail: Edges '${start_title}' and '${end_title}' exist in graph and are connected, but shouldn't be!
    
the algorithm backtracks by ${n} step
    [Documentation]    *model info*
    ...    :IN: trace_info.current_trace
    ...    :OUT: trace_info.current_trace | trace_info.all_traces+=1
    Variable Should Exist    ${trace_info}

    ${a} =      Get Length Current Trace        ${trace_info}
    ${b} =      Get Length All Traces        ${trace_info}

    ${trace_info} =     Backtrack       ${trace_info}       ${n}

    ${i} =      Get Length Current Trace        ${trace_info}
    ${j} =      Get Length All Traces        ${trace_info}

    Run Keyword If      ${a} - ${n} != ${i}
    ...    Fail     Fail: Backtracking did not shorten current trace correctly

    Run Keyword If      ${b} + 1 != ${j}
    ...    Fail     Fail: Backtracking did not add new trace to all traces
































the algorithm inserts ${scenario_name}
    [Documentation]    *model info*
    ...    :IN: trace_info
    ...    :OUT: trace_info
    Variable Should Exist    ${trace_info}
    ${trace_info} =    The Algorithm Inserts    ${trace_info}    ${scenario_name}



the graph of type ${type} is generated
    [Documentation]    *model info*
    ...    :IN: trace_info
    ...    :OUT: trace_info
    Variable Should Exist    ${trace_info}
    ${graph} =    Generate Graph    ${trace_info}    ${type}
    Set Suite Variable    ${graph}
    Set Suite Variable    ${graph_type}

the scenario graph contains vertices ${vertices}
    [Documentation]    *model info*
    ...    :IN: None
    ...    :OUT: None
    Variable Should Exist    ${graph}
    Variable Should Exist    ${graph_type}

    Should Be Equal    ${graph_type}    scenario
    Log    TODO!
        

trace info ${trace} has current trace ${current}
    [Documentation]     *model info*
    ...     :IN: trace_info
    ...     :OUT: trace_info.current_trace=[]
    Variable Should Exist    ${trace_info}

current trace ${current_trace} has a tuple 'scenario ${scenario}, state ${state}'
    [Documentation]    *model info*
    ...     :IN: trace_info.current_trace
    ...     :OUT: trace_info.current_trace.append((${scenario}, ${state}))
    Variable Should Exist   ${trace_info}

    ${trace_info} =         The Algorithm Inserts  ${trace_info}   ${scenario}     ${state}
    Set Suite Variable  ${trace_info}

trace info ${trace} has all traces ${all}
    [Documentation]     *model info*
    ...     :IN: trace_info
    ...     :OUT: trace_info.all_traces=[]
    Variable Should Exist    ${trace_info}

all traces ${all} has list ${list}
    [Documentation]    *model info*
    ...     :IN: trace_info
    ...     :OUT: trace_info.all_traces.append([])
    Variable Should Exist   ${trace_info}

    ${trace_info} =         All Traces Contains List  ${trace_info}
    Set Suite Variable  ${trace_info}

list ${list} has a tuple 'scenario ${scenario}, state ${state}'
    [Documentation]    *model info*
    ...     :IN: trace_info.all_traces
    ...     :OUT: trace_info.all_traces.append((${scenario}, ${state}))
    Variable Should Exist   ${trace_info}

    ${trace_info} =         All Traces Contains  ${trace_info}   ${scenario}     ${state}
    Set Suite Variable  ${trace_info}

test suite ${suite} contains trace info ${ti}
    [Documentation]     *model info*
    ...     :IN: suite, trace_info
    ...     :OUT: suite, trace_info
    Variable Should Exist   ${suite}
    Variable Should Exist   ${trace_info}

test suite ${suite} is exported to json
    [Documentation]     *model info*
    ...     :IN: suite, trace_info
    ...     :OUT: new filepath
    Variable Should Exist   ${suite}
    Variable Should Exist   ${trace_info}
    
    ${filepath} =   Export Graph      ${suite}    ${trace_info}
    Set Suite Variable  ${filepath}

the file ${filename} exists
    [Documentation]     *model info*
    ...     :IN: suite, filepath
    ...     :OUT: suite, filepath 
    Variable Should Exist   ${filepath}

    ${result} =     Check File Exists   ${filepath}
    Should Be Equal     ${result}   file exists

${filename} is imported
    [Documentation]     *model info*
    ...     :IN: suite, filepath
    ...     :OUT: new new_trace_info
    Variable Should Exist   ${filepath}
    
    ${new_trace_info} =     Import Graph   ${filepath}
    Set Suite Variable      ${new_trace_info}

trace info from ${filename} is the same as trace info ${trace}
    [Documentation]     *model info*
    ...     :IN: new_trace_info, trace_info
    ...     :OUT: new flag_cleanup
    Variable Should Exist   ${trace_info}
    Variable Should Exist   ${new_trace_info}

    ${result} =     Compare Trace Info   ${trace_info}      ${new_trace_info}
    Should Be Equal     ${result}   imported model equals exported model

${filename} is deleted
    [Documentation]     *model info*
    ...     :IN: filepath
    ...     :OUT: filepath
    Variable Should Exist   ${filepath}
    
    Delete File    ${filepath}

${filename} does not exist
    [Documentation]     *model info*
    ...     :IN: filepath
    ...     :OUT: filepath
    Variable Should Exist   ${filepath}

    ${result} =     Check File Exists   ${filepath}
    Should Be Equal     ${result}   file does not exist

flag cleanup is set
    [Documentation]     *model info*
    ...     :IN: suite
    ...     :OUT: suite
    Set Suite Variable      ${flag_cleanup}     True

flag cleanup has been set
    [Documentation]     *model info*
    ...     :IN: flag_cleanup
    ...     :OUT: flag_cleanup
    Variable Should Exist   ${flag_cleanup}
