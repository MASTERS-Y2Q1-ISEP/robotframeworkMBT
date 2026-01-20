*** Settings ***
Documentation     Test correctness all graph representations
Suite Setup       Enter test suite
Resource          ../../resources/visualisation.resource
Library           robotmbt    processor=flatten


*** Keywords ***
Enter test suite
    check requirements
    Treat this test suite Model-based