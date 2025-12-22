'''
Author: Devi Granec-Boydstun
    Role: Scrum Master 2
Purpose: Test if the filter buttons in the FAA abbreviations/common items tool are working correcting 
         in a End 2 End style testing, which requires the page to be loaded in the localhost and 
         tests like how a user would interact with the page. This needs Selenium to do so.
Tests Implemented:
        1. All Buttons are active by default
        2. Clicking a Button makes the category go away, random category
        3. After clicking, clicking again makes the category re-appear, random category
Improvements: Make tests 2/3 test all categories, but you will need a fixture for this to parameterize
'''

# ---- Imports ----
import sys
import os
import pytest
from selenium.webdriver.common.by import By
import json
import glob
import random

# ---- PATHING ----
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
UTILS_DIR = os.path.join(ROOT_DIR, "tests", "utils")
DATA_DIR = os.path.join(ROOT_DIR, "backdrop-demo-clean", "public", "data")

# ---- Import Test helpers ----
sys.path.append(UTILS_DIR)

from e2e_helpers import (
    checkPageReady,            # Function to check the page is ready for tests
    waitAndClickByRole,        # Function to click on a element using ARIA
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
FILTER_BUTTON_ROLE = "button"
FILTER_BUTTON_LABEL = "Filter by category"

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

def get_term_categories():
    """
    Reads all *_term.json files from root/public/data and extracts the category field
    of the first element in each file.

    rtype: List of category values
    """
    categories = []

    # glob in is python to search files simialr to regex, but requires less set up
    for file_path in glob.glob(os.path.join(DATA_DIR, "*_terms.json")):
        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)

            if not data:
                continue  # this skips empty files

            first_element = data[0]

            # Get the value of the category field
            category = first_element["category"]
            categories.append(category)

    return categories

def get_category_present(driver, category):
    '''
    This function will check if the category is on the page
    param: webdriver that allows the page to run
    param: category to look for
    rtype: true if the category is there, false if not
    '''
    # Get all categories currently on the page
    categories = get_all_categories(driver)

    # check if the category is in that list
    return category in categories


def helper_all_categories_present(driver):
    '''
    This function checks that all the categories are on the page
    param: webdriver that allows the page to run
    rtype: if the lists are identical, that all categories are on the page
    '''
    # Get a list of categories that should be present
    term_categories = get_term_categories()

    # Check the page exists
    checkPageReady(driver, LOCAL_HOST)

    # Get all categories found on the page
    page_categories = get_all_categories(driver)

    # Check that all categories in page_categories matches with term_categories
    identical = sorted(term_categories) == sorted(page_categories)

    return identical, term_categories, page_categories

# ---- Default State Test ----
@pytest.mark.parametrize(
    "browser_types_fixture",
    BROWSER_SUPERLIST,
    indirect=True) # Indirect allows parameterizing fixtures, browser_types_fixture
def test_default_categories(browser_types_fixture):
    '''
    This function checks the number of categories that have a JSON, then sees if 
    they are all on the page 
    param: browser_types_fixture handles the browser tests for all passed browsers
    '''
    driver = browser_types_fixture
    driver.get(LOCAL_HOST)

    # Use the helper function to check all categories are on the page
    identical, term_categories, page_categories = helper_all_categories_present(driver)

    assert identical, f"ERROR: Categories did not match, Categories from file {term_categories}, Categories from page {page_categories}"

# ---- 1-Click Test ----
@pytest.mark.parametrize(
    "browser_types_fixture",
    BROWSER_SUPERLIST,
    indirect=True) # Indirect allows parameterizing fixtures, browser_types_fixture
def test_one_click_category(browser_types_fixture):
    '''
    This function picks one category to select the given filter button to check if the category dissapears
    param: browser_types_fixture handles the browser tests for all passed browsers
    '''
    driver = browser_types_fixture
    driver.get(LOCAL_HOST)

    # Use the helper function to check all categories are on the page
    identical, term_categories, page_categories = helper_all_categories_present(driver)

    if (identical):
        category = random.choice(term_categories)

        waitAndClickByRole(driver, FILTER_BUTTON_ROLE, FILTER_BUTTON_LABEL+f" {category}", DEFAULT_TIMEOUT)

        # Use helper function to check if the category is in the list, we WANT False
        is_present = get_category_present(driver, category)
    
        assert (not is_present), f"ERROR: the category ({category}) is still active after being clicked"
    else:
        assert identical, f"ERROR: Categories did not match, Categories from file {term_categories}, Categories from page {page_categories}"

# ---- 2-Click Test ----
@pytest.mark.parametrize(
    "browser_types_fixture",
    BROWSER_SUPERLIST,
    indirect=True) # Indirect allows parameterizing fixtures, browser_types_fixture
def test_two_click_category(browser_types_fixture):
    '''
    This function picks one category to select the given filter button to check if the category dissapears
    and then clicks again to see if it reappears
    param: browser_types_fixture handles the browser tests for all passed browsers
    '''
    driver = browser_types_fixture
    driver.get(LOCAL_HOST)

    # Use the helper function to check all categories are on the page
    identical, term_categories, page_categories = helper_all_categories_present(driver)

    if (identical):
        category = random.choice(term_categories)

        waitAndClickByRole(driver, FILTER_BUTTON_ROLE, FILTER_BUTTON_LABEL+f" {category}", DEFAULT_TIMEOUT)

        # Use helper function to check if the category is in the list, we WANT False
        is_present = get_category_present(driver, category)
    else:
        assert identical, f"ERROR: Categories did not match, Categories from file {term_categories}, Categories from page {page_categories}"

    if (not is_present):
        waitAndClickByRole(driver, FILTER_BUTTON_ROLE, FILTER_BUTTON_LABEL+f" {category}")

        # Use helper function to check if the category is in the list, we WANT True here
        is_present = get_category_present(driver, category)

        assert is_present, f"ERROR: the category ({category}) is not active after being clicked twice"
    else: 
        assert (not is_present), f"ERROR: the category ({category}) is still active after being clicked once"