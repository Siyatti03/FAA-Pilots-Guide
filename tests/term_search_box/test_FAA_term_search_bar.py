'''
Author: Devi Granec-Boydstun
    Role: Scrum Master 2
Purpose: Test if the Search Bar in the FAA abbreviations/common items tool is working correcting 
         in a End 2 End style testing, which requires the page to be loaded in the localhost and 
         tests like how a user would interact with the page. This needs Selenium to do so.
Tests Implemented:
        1. Check an empty input
            NOT USED RIGHT NOW. Check the Usually unsafe inputs
        2. Check for an input that is NOT in the end results
        3. Check for an input that IS in the end results
        4. Check for how numbers/special characters work in the search bar
'''

# ---- Imports ----
import sys
import os
import pytest
from selenium.webdriver.common.by import By

# ---- PATHING ----
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
UTILS_DIR = os.path.join(ROOT_DIR, "tests", "utils")

# ---- Import Test helpers ----
sys.path.append(UTILS_DIR)
print(sys.path)

from e2e_helpers import (
    checkPageReady,            # Function to check the page is ready for tests
    findElementByRoleExisting, # Function to support using ARIA to wait on components to appear
    DEFAULT_TIMEOUT,           # Import variable to support timeouts
)

# ---- Variables ----
LOCAL_HOST = "http://localhost:5173"
from driver_variables import BROWSER_SUPERLIST

# ---- Page ARIA Information----
SEARCH_BOX_ROLE = "searchbox"
SEARCH_BOX_LABEL = "Search Term Input"
CATEGORIES_CONTAINER_ROLE = "region"
CATEGORIES_CONTAINER_LABEL = "Search Terms Categories"

# ---- Expected Output Class ----
# This is used to make calling output information easier
class ExpectedOutput:
    def __init__(self, role, label, text):
        self.role = role
        self.label = label
        self.text = text

# ---- Tests Helper functions ----
def get_all_categories(driver):
    """
    Returns a list of category names as strings for use in other helpers
    param:driver is the webdriver being passed for functions
    rtype: Returns a list of category names as strings.
    """

    #Selenium looks for: <div role="region" aria-label="{category}-outer-container">
    elements = driver.find_elements(
        By.XPATH, 
        '//div[@role="region" and substring(@aria-label, string-length(@aria-label)-15)="-outer-container"]'
    )

    categories = []
    for el in elements:
        label = el.get_attribute("aria-label")
        category = label.replace("-outer-container", "") # Remove extra characters
        categories.append(category)

    return categories

def expand_categories(driver, categories):
    """
    Extends the categories given for searching
    param: driver is the webdriver being passed for functions
    """
    for category in categories:
        button = findElementByRoleExisting(driver, "button", f"control-visibility-{category}", DEFAULT_TIMEOUT)
        button.click()

def check_all_no_results(driver):
    """
    Searches all categories have "No Matching items"
    param: driver is the webdriver being passed for functions
    """
    categories = get_all_categories(driver)

    expand_categories(driver, categories)

    expected_text = "No matching items."

    for category in categories:
        region = findElementByRoleExisting(driver, "list", f"list-{category}-terms", DEFAULT_TIMEOUT)
        return region.text == expected_text, category
    
def helper_func_tests_one(driver, input, output):
    '''
    This function has the formatting needed to test for 1 ouput given by the test
    param: driver is the webdriver being passed for functions
    param: The input which needs to be passed into the search box
    param: the output that is being found to get the where the output should be
    '''
    # Check the page exists
    checkPageReady(driver, LOCAL_HOST)

    # Expand All Categories for searching ease
    categories = get_all_categories(driver)
    expand_categories(driver, categories)

    # Get the search box element, using default timeout
    search_box = findElementByRoleExisting(driver, SEARCH_BOX_ROLE, SEARCH_BOX_LABEL, DEFAULT_TIMEOUT)

    # Input the given input
    search_box.clear()
    search_box.send_keys(input)

    # Wait for the results
    results = findElementByRoleExisting(driver, output.role, output.label, DEFAULT_TIMEOUT)
    return results.text

def helper_func_tests_all(driver, input):
    '''
    This function has the formatting need to check all categories for No Matching Items
    param: driver is the webdriver being passed for functions
    param: The input which needs to be passed into the search box
    '''
    # Check the page exists
    checkPageReady(driver, LOCAL_HOST)

    # Get the search box element, using default timeout
    search_box = findElementByRoleExisting(driver, SEARCH_BOX_ROLE, SEARCH_BOX_LABEL, DEFAULT_TIMEOUT)

    # Input the given input
    search_box.clear()
    search_box.send_keys(input)

    # Wait for the results
    driver.implicitly_wait(10) 

    return check_all_no_results(driver) 

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
    checkPageReady(driver, LOCAL_HOST)

    # Get the search box element, using default timeout
    search_box = findElementByRoleExisting(driver, SEARCH_BOX_ROLE, SEARCH_BOX_LABEL, DEFAULT_TIMEOUT)
    
    # Empty the search box
    search_box.clear()

    # Get current state of Categories container
    results_container = findElementByRoleExisting(driver, CATEGORIES_CONTAINER_ROLE, CATEGORIES_CONTAINER_LABEL, DEFAULT_TIMEOUT)
    prev_results = results_container.text

    search_box.send_keys("")

    # Wait for a few seconds, then pull the container
    driver.implicitly_wait(10)
    current_results = findElementByRoleExisting(driver, CATEGORIES_CONTAINER_ROLE, CATEGORIES_CONTAINER_LABEL, DEFAULT_TIMEOUT).text 

    assert current_results == prev_results, f"Empty Input Test Failed: Previous Container = {prev_results}, Current Container = {current_results}"

'''
With the current set up there are no known Unsafe Inputs:
SQL Injection- No backend to inject into
JavaScript- Data sent is NOT displayed on screen
    CrossSite Scripting- No javaScript enabled

# ---- Unsafe Inputs Map + Function ----
The dictionary below contains the Input:Output expectations for each test of the different possible
unsafe inputs

PLACE HOLDERS FOR NOW, needs inputs for testing

Unsafe_Map = {
    "unsafeInput1":"unsafeOutput2",
    "unsafeInput2":"unsafeOutput2",
}

@pytest.mark.parametrize("browser_types_fixture", BROWSER_SUPERLIST, indirect=True)
@pytest.mark.parametrize("input, output", Unsafe_Map.items())
def test_Unsafe_Inputs(browser_types_fixture, input, output):
    Tests unsafe inputs that should be sanitized by the page
    param: browser_types_fixture handles the browser tests for all passed browsers
    param: input from Unsafe_Map
    param: output from Unsafe_Map
    driver = browser_types_fixture
    driver.get(LOCAL_HOST)

    results = helper_func_tests_one(driver, input)

    assert results in output, f"Unsafe Input Test Failed: input = {input}, output = {results}, expected = {output}"
'''
    
# ---- Unknown input test ----
@pytest.mark.parametrize("browser_types_fixture", BROWSER_SUPERLIST, indirect=True)
def test_Unknown_Input(browser_types_fixture):
    '''
    Tests an unknown input which should show no results in all categories
    param: browser_types_fixture handles the browser tests for all passed browsers
    '''
    input = "UnknownInput" #Placeholder

    driver = browser_types_fixture
    driver.get(LOCAL_HOST)

    results, category = helper_func_tests_all(driver, input)
    assert results, f"Unknown Input Test Failed: input = {input}, category = {category}"

# ---- Known input test ----
Known_Map = {
    "1":ExpectedOutput(role = "listitem", label = "term-Certification Types-1st Class", text = "1st Class"),
    "pilot":ExpectedOutput(role = "listitem", label = "term-Certifications-CPL", text = "CPL"),
}

@pytest.mark.parametrize("browser_types_fixture", BROWSER_SUPERLIST, indirect=True)
@pytest.mark.parametrize("input, output", Known_Map.items())
def test_Known_Input(input, output, browser_types_fixture):
    '''
    Tests an known input which should show correct result
    param: browser_types_fixture handles the browser tests for all passed browsers
    '''
    driver = browser_types_fixture
    driver.get(LOCAL_HOST)

    results = helper_func_tests_one(driver, input, output)

    assert output.text in results, f"Known Input Test Failed: input = {input}, output = {results}, expected = {output.text}"

# ---- Unusual Inputs Map + Function ----
'''
The dictionary below contains the Input:Output expectations for each test of the different possible
unusual inputs
'''
Unusual_Input_List = ["123456789", "@", "EMOJI"]

@pytest.mark.parametrize("browser_types_fixture", BROWSER_SUPERLIST, indirect=True)
@pytest.mark.parametrize("input", Unusual_Input_List)
def test_Unusual_Inputs(browser_types_fixture, input):
    '''
    Tests unusual inputs that should return no results
    param: browser_types_fixture handles the browser tests for all passed browsers
    param: input from Unusual_Input_List
    '''
    driver = browser_types_fixture
    driver.get(LOCAL_HOST)

    results, category = helper_func_tests_all(driver, input)
    assert results, f"Unusual Input Test Failed: input = {input}, category = {category}"