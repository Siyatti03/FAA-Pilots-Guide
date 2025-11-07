'''
Author: Devi Granec-Boydstun
    Role: Scrum Master 2
Purpose: Test if the Search Bar in the FAA abbreviations/common items tool is working correcting 
         in a End 2 End style testing, which requires the page to be loaded in the localhost and 
         tests like how a user would interact with the page. This needs Selenium to do so.
Tests Implemented:
        1. Check an empty input
        2. Check the sanitization of the inputs
        3. Check for an input that is NOT in the end results
        4. Check for an input that IS in the end results
        5. Check for how numbers/special characters work in the search bar
'''

# ---- Imports ----
import sys
import os
from selenium.webdriver.common.keys import Keys
import pytest

# ---- PATHING ----
ROOT_DIR = os.path.dir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
UTILS_DIR = os.path.join(ROOT_DIR, "tests", "utils")

# ---- Import Test helpers ----
sys.path.append(UTILS_DIR)
print(sys.path)

import e2e_helpers as e2ehelp

# ---- Variables ----
LOCAL_HOST = "http://localhost:3000"
# This is the superset of all browsers, to be filtered by the fixture
BROWSER_SUPERLIST = [{"browser": "chrome", "headless": True},
                    {"browser": "firefox", "headless": True},
                    {"browser": "safari", "headless": True},
                    {"browser": "edge", "headless": True},]

# ---- ARIA XPATHs ----
SEARCH_BOX_ROLE = "searchbox"
SEARCH_BOX_LABEL = "Term_Search_Input"
SEARCH_BOX_XPATH = f"//*[@role={SEARCH_BOX_ROLE} and @aria-label={SEARCH_BOX_LABEL}]"
SEARCH_BOX_RESULTS_CONTAINER_ROLE = "group" #TODO- Would this have an ARIA???? its just a DIV??
SEARCH_BOX_RESULTS_CONTAINER_LABEL = "Term_Search_Results_Container"
SEARCH_BOX_RESULTS_LIST_XPATH = f"//*[@role={SEARCH_BOX_RESULTS_CONTAINER_ROLE} and @aria-label={SEARCH_BOX_RESULTS_CONTAINER_LABEL}]"
SEARCH_BOX_RESULTS_LIST_ROLE = "list"
SEARCH_BOX_RESULTS_LIST_LABEL= "Term_Search_Results_List"
SEARCH_BOX_RESULTS_LIST_XPATH = f"//*[@role={SEARCH_BOX_RESULTS_LIST_ROLE} and @aria-label={SEARCH_BOX_RESULTS_LIST_LABEL}]"
    
# ---- Empty Input Test ----
@pytest.mark.parametrize(
    "browser_types_fixture",
    BROWSER_SUPERLIST,
    indirect=True) # Indirect allows parameterizing fixtures, browser_types_fixture
def test_Empty_Input(browser_types_fixture):
    '''
    This function tests the empty input for all browsers
    param: browser_types_fixture handles the browser tests for all passed browsers
    '''
    driver = browser_types_fixture
    driver.get(LOCAL_HOST)

    # Check the page exists
    e2ehelp.checkPageReady(driver, LOCAL_HOST)

    # Get the search box element, using default timeout
    search_box = e2ehelp.findElementByRoleExisting(driver, SEARCH_BOX_ROLE, SEARCH_BOX_LABEL, None)
    
    # Empty the search box
    search_box.clear()

    # Get current state of results container
    results_container = e2ehelp.findElementByRoleExisting(driver, SEARCH_BOX_RESULTS_CONTAINER_ROLE, SEARCH_BOX_RESULTS_CONTAINER_LABEL, None)
    prev_results = results_container.text

    search_box.send_keys(Keys.RETURN)

    # Wait for a few seconds, then pull the container
    driver.implict_wait(10)
    current_results = e2ehelp.findElementByRoleExisting(driver, SEARCH_BOX_RESULTS_CONTAINER_ROLE, SEARCH_BOX_RESULTS_CONTAINER_LABEL, None).text 

    assert current_results == prev_results, f"Empty Input Test Failed: Previous Container = {prev_results}, Current Container = {current_results}"

# ---- Tests Helper function ----
def helper_func_tests(driver, input):
    '''
    This function has the formatting needed for all tests, besides the empty test above
    param: driver is the webdriver being passed for functions
    param: The input which needs to be passed into the search box
    '''
    # Check the page exists
    e2ehelp.checkPageReady(driver, LOCAL_HOST)

    # Get the search box element, using default timeout
    search_box = e2ehelp.findElementByRoleExisting(driver, SEARCH_BOX_ROLE, SEARCH_BOX_LABEL, None)

    # Input the given input
    search_box.clear()
    search_box.send_keys(input)
    search_box.send_keys(Keys.RETURN)

    # Wait for the results
    results = e2ehelp.findElementByRoleExisting(driver, SEARCH_BOX_RESULTS_LIST_ROLE, SEARCH_BOX_RESULTS_LIST_LABEL, None)
    return results.text

# ---- Unsafe Inputs Map + Function ----
'''
The dictionary below contains the Input:Output expectations for each test of the different possible
unsafe inputs

PLACE HOLDERS FOR NOW
'''
Unsafe_Map = {
    "unsafeInput1":"unsafeOutput1",
    "unsafeInput2":"unsafeOutput2",
}

@pytest.mark.parametrize(
    "browser_types_fixture",
    BROWSER_SUPERLIST,
    indirect=True) # Indirect allows parameterizing fixtures, browser_types_fixture
@pytest.mark.parametrize("input, output", Unsafe_Map.items())
def test_Unsafe_Inputs(browser_types_fixture, input, output):
    '''
    Tests unsafe inputs that should be sanitized by the page
    param: browser_types_fixture handles the browser tests for all passed browsers
    param: input from Unsafe_Map
    param: output from Unsafe_Map
    '''
    driver = browser_types_fixture
    driver.get(LOCAL_HOST)

    results = helper_func_tests(driver, input)

    assert results in output, f"Unsafe Input Test Failed: input = {input}, output = {results}, expected = {output}"

# ---- Unknown input test ----
@pytest.mark.parametrize(
    "browser_types_fixture",
    BROWSER_SUPERLIST,
    indirect=True) # Indirect allows parameterizing fixtures, browser_types_fixture
def test_Unknown_Input(browser_types_fixture):
    '''
    Tests an unknown input which should show no results
    param: browser_types_fixture handles the browser tests for all passed browsers
    '''
    input = "UnknownInput"
    output = "NoResults"
    driver = browser_types_fixture
    driver.get(LOCAL_HOST)

    results = helper_func_tests(driver, input = input)

    assert results in output, f"Unknown Input Test Failed: input = {input}, output = {results}, expected = {output}"

# ---- Known input test ----
@pytest.mark.parametrize(
    "browser_types_fixture",
    BROWSER_SUPERLIST,
    indirect=True) # Indirect allows parameterizing fixtures, browser_types_fixture
def test_Known_Input(browser_types_fixture):
    '''
    Tests an known input which should show correct result
    param: browser_types_fixture handles the browser tests for all passed browsers
    '''
    input = "KnownInput"
    output = "Result"

    driver = browser_types_fixture
    driver.get(LOCAL_HOST)

    results = helper_func_tests(driver, input = input)

    assert results in output, f"Known Input Test Failed: input = {input}, output = {results}, expected = {output}"

# ---- Unusual Inputs Map + Function ----
'''
The dictionary below contains the Input:Output expectations for each test of the different possible
unusual inputs

PLACE HOLDERS FOR NOW
'''
Unusual_Map = {
    "123456789":"NoResults",
    "@":"NoResults",
}

@pytest.mark.parametrize(
    "browser_types_fixture",
    BROWSER_SUPERLIST,
    indirect=True) # Indirect allows parameterizing fixtures, browser_types_fixture
@pytest.mark.parametrize("input, output", Unusual_Map.items())
def test_Unusual_Inputs(browser_types_fixture, input, output):
    '''
    Tests unusual inputs that should return no results
    param: browser_types_fixture handles the browser tests for all passed browsers
    param: input from Unusual_Map
    param: output from Unusual_Map
    '''
    driver = browser_types_fixture
    driver.get(LOCAL_HOST)

    results = helper_func_tests(driver, input)

    assert results in output, f"Unusual Input Test Failed: input = {input}, output = {results}, expected = {output}"