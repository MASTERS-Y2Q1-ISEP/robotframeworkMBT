*** Settings ***   
Library           robotmbt    processor=flatten

*** Test Cases ***
Feature Setup
    Given test suite s
    When the algorithm inserts 'A1' with state "attr: states = ['a1'], special='!'"
    And the algorithm inserts 'A2' with state "attr: states = ['a1', 'a2'], special='!'"
    Then test suite s has a trace with 2 steps