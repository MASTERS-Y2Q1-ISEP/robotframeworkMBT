*** Settings ***
Documentation     Test correctness all graph representations
Suite Setup       do test setup
Resource          ../../resources/visualisation.resource
Library           robotmbt    processor=flatten


*** Keywords ***
do test setup
    check requirements
    Treat this test suite Model-based