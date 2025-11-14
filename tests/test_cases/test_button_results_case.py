'''
Author: Garrett Snow
    Role: Scrum Master 1
Purpose: End-to-end UI tests for condition selection flows and results, including
         Anxiety, Coronary Heart Disease (CHD), and Diabetes; restart behavior;
         and basic keyboard accessibility.
Tests Implemented:
    1. Anxiety: simple path → in-office issuance
    2. Anxiety: complex path → FAA review/deferral
    3. Anxiety: checkbox max-two behavior (no crash)
    4. CHD: waiting period info when < 3 months
    5. CHD: Class 1 initial requires radionuclide and catheterization
    6. Diabetes: three management paths → expected outcomes
    7. Restart: “Start Over” returns to the condition grid
    8. Keyboard: Enter on focused tile starts the guide
'''
import os
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# Helper imports
from e2e_helpers import (
    checkPageReady,            # open URL + wait for <body>  
    findElementByRoleExisting, # ARIA role + name lookup 
    waitAndClick,              # wait clickable + click (CSS)   
    findElementById,           # find by element id
    BASE_URL,                  # shared base URL         
    DEFAULT_TIMEOUT,           # default wait timeout 
)
from driver_variables import BROWSER_SUPERLIST

# function to click button by its text
# function to get result title element
# Choose a condition tile by mapping an app key → the tile’s accessible name.
# Keys ('anxiety', 'chd', 'diabetes') map to the icon's aria-label
# ('worried face', 'heart', 'drop of blood'). We then click the matching
# <img role="img" aria-label="..."> to start that guide.
def choose_condition(driver, key):  
    '''
    Map an app key ('anxiety','chd','diabetes') to the tile's aria-label and click it to start that guide.
    param: browser_types_fixture- per test web driver from conftest.py
    param: key- the condition key to choose
    '''


    aria = {"anxiety":"worried face","chd":"heart","diabetes":"drop of blood"}[key]
    findElementByRoleExisting(driver, "img", aria, DEFAULT_TIMEOUT).click()

# function to click continue button from checkbox page
# Restart flow: specifically clicks the exact “Start Over” button.
# Uses a text-based XPath to find the button by its visible label and
# return the user to the initial condition grid.
# actual unit tests begin here


# Tests the "Anxiety & Depression Guide" path with outcome
@pytest.mark.parametrize(
    "browser_types_fixture",
    BROWSER_SUPERLIST,
    indirect=True
)

def test_anxiety_simple_ame_can_issue(browser_types_fixture):
    '''
    Anxiety & depression flow that returns 'Likely Qualifies for In-Office Issuance'.
    param: browser_types_fixture- per test web driver from conftest.py
    '''
    driver = browser_types_fixture
    
    checkPageReady(driver, BASE_URL)
    choose_condition(driver, "anxiety")

    waitAndClick(driver, "Generalized Anxiety Disorder", DEFAULT_TIMEOUT)
    waitAndClick(driver, "PTSD", DEFAULT_TIMEOUT)
    waitAndClick(driver, "Continue", DEFAULT_TIMEOUT)

    for _ in range(4):
        waitAndClick(driver, "No", DEFAULT_TIMEOUT)

    title = findElementById(driver, "result-title", DEFAULT_TIMEOUT)
    assert "Likely Qualifies for In-Office Issuance" in title.text, \
        f"ERROR: Expected 'Likely Qualifies for In-Office Issuance' in result title, got {title.text!r}"


# Test for long anxiety path with outcome
@pytest.mark.parametrize(
    "browser_types_fixture",
    BROWSER_SUPERLIST,
    indirect=True
)

def test_anxiety_complex_deferral(browser_types_fixture):
    '''
    Anxiety flow with more questions that leads to 'FAA Review Required for Special Issuance'.
    param: browser_types_fixture- per test web driver from conftest.py
    '''
    driver = browser_types_fixture

    checkPageReady(driver, BASE_URL)
    choose_condition(driver, "anxiety")

    waitAndClick(driver, "OCD", DEFAULT_TIMEOUT)
    waitAndClick(driver, "Continue", DEFAULT_TIMEOUT)

    waitAndClick(driver, "Yes", DEFAULT_TIMEOUT)
    waitAndClick(driver, "No", DEFAULT_TIMEOUT)
    waitAndClick(driver, "No", DEFAULT_TIMEOUT)
    waitAndClick(driver, "No", DEFAULT_TIMEOUT)

    title = findElementById(driver, "result-title", DEFAULT_TIMEOUT)
    assert "FAA Review Required for Special Issuance" in title.text, \
        f"ERROR: Expected 'FAA Review Required for Special Issuance' in result title, got {title.text!r}"


# Test to make sure only two items are chosen
@pytest.mark.parametrize(
    "browser_types_fixture",
    BROWSER_SUPERLIST,
    indirect=True
)

def test_anxiety_checkbox_max_two_behaviour(browser_types_fixture):
    '''
    Selecting more than two anxiety options should not cause problems; continue to results safely.
    param: browser_types_fixture- per test web driver from conftest.py
    '''
    driver = browser_types_fixture
    
    checkPageReady(driver, BASE_URL)
    choose_condition(driver, "anxiety")

    waitAndClick(driver, "Generalized Anxiety Disorder", DEFAULT_TIMEOUT)
    waitAndClick(driver, "PTSD", DEFAULT_TIMEOUT)
    waitAndClick(driver, "OCD", DEFAULT_TIMEOUT)
    waitAndClick(driver, "Continue", DEFAULT_TIMEOUT)

    for _ in range(4):
        waitAndClick(driver, "No", DEFAULT_TIMEOUT)

    title = findElementById(driver, "result-title", DEFAULT_TIMEOUT)
    assert title is not None and title.is_displayed(), \
        f"ERROR: Result title not found or not displayed after selecting more than two options."
   
                         
# Test for stent + class 1 or 2, <3 months. 
@pytest.mark.parametrize(
    "browser_types_fixture",
    BROWSER_SUPERLIST,
    indirect=True
)

def test_chd_waiting_period_information(browser_types_fixture):
    '''
    CHD path (stent + first/second class, <3 months) shows 'Mandatory Recovery Period'.
    param: browser_types_fixture- per test web driver from conftest.py
    '''
    driver = browser_types_fixture
    
    checkPageReady(driver, BASE_URL)
    choose_condition(driver, "chd")

    waitAndClick(driver, "Stent Placement (Angioplasty)", DEFAULT_TIMEOUT)
    waitAndClick(driver, "Continue", DEFAULT_TIMEOUT)

    waitAndClick(driver, "First or Second Class", DEFAULT_TIMEOUT)
    waitAndClick(driver, "Less than 3 months", DEFAULT_TIMEOUT)
    waitAndClick(driver, "No", DEFAULT_TIMEOUT)

    title = findElementById(driver, "result-title", DEFAULT_TIMEOUT)
    assert "Mandatory Recovery Period" in title.text, \
        f"ERROR: Expected 'Mandatory Recovery Period' in result title, got {title.text!r}"


# Class 1 eval needs radionuclide and cath
@pytest.mark.parametrize(
    "browser_types_fixture",
    BROWSER_SUPERLIST,
    indirect=True
)

def test_chd_class1_initial_requires_radionuclide_and_cath(browser_types_fixture):
    '''
    CHD path verifying class 1 initial requires test and heart cat steps.
    param: browser_types_fixture- per test web driver from conftest.py
    '''
    driver = browser_types_fixture
    
    checkPageReady(driver, BASE_URL)
    choose_condition(driver, "chd")

    waitAndClick(driver, "Heart Attack (MI)", DEFAULT_TIMEOUT)
    waitAndClick(driver, "Stent Placement (Angioplasty)", DEFAULT_TIMEOUT)
    waitAndClick(driver, "Continue", DEFAULT_TIMEOUT)

    waitAndClick(driver, "First or Second Class", DEFAULT_TIMEOUT)
    waitAndClick(driver, "More than 6 months", DEFAULT_TIMEOUT)
    waitAndClick(driver, "No", DEFAULT_TIMEOUT)

    title = findElementById(driver, "result-title", DEFAULT_TIMEOUT)
    assert "FAA Review Required for Special Issuance" in title.text, \
        f"ERROR: Expected 'FAA Review Required for Special Issuance' in result title, got {title.text!r}"
    
        
# Parameters for diabetes management and expected outcomes
@pytest.mark.parametrize('management,expected', [
    ("Diet and Exercise Only", "Likely Qualifies for In-Office Issuance"),
    ("Oral Medications (Not Insulin)", "AME Assisted Special Issuance"),
    ("Insulin Injections or Pump", "FAA Review Required for Special Issuance"),
])

# diabetes paths make sure each choice are correct
@pytest.mark.parametrize(
    "browser_types_fixture",
    BROWSER_SUPERLIST,
    indirect=True)

def test_diabetes_paths(browser_types_fixture, management, expected):
    '''
    Parametrized: each diabetes management option maps to the expected outcome title.
    param: browser_types_fixture- per test web driver from conftest.py
    param: management- the diabetes management option to choose
    param: expected- the expected result title text
    '''
    driver = browser_types_fixture

    checkPageReady(driver, BASE_URL)
    choose_condition(driver, "diabetes")
    waitAndClick(driver, management, DEFAULT_TIMEOUT)
    title = findElementById(driver, "result-title", DEFAULT_TIMEOUT)
    assert expected in title.text, \
        f"ERROR: Expected {expected!r} in result title, got {title.text!r}"


# Tests start over button
@pytest.mark.parametrize(
    "browser_types_fixture",
    BROWSER_SUPERLIST,
    indirect=True
)

def test_restart_returns_to_condition_grid(browser_types_fixture):
    '''
    After reaching results, 'Start Over' returns to the condition grid
    param: browser_types_fixture- per test web driver from conftest.py
    '''
    driver = browser_types_fixture

    checkPageReady(driver, BASE_URL)
    choose_condition(driver, "anxiety")

    waitAndClick(driver, "PTSD", DEFAULT_TIMEOUT)
    waitAndClick(driver, "Continue", DEFAULT_TIMEOUT)
    for _ in range(4):
        waitAndClick(driver, "No", DEFAULT_TIMEOUT)

    waitAndClick(driver, "Start Over", DEFAULT_TIMEOUT)
    tiles = [
    findElementByRoleExisting(driver, "img", "worried face", DEFAULT_TIMEOUT),
    findElementByRoleExisting(driver, "img", "heart", DEFAULT_TIMEOUT),
    findElementByRoleExisting(driver, "img", "drop of blood", DEFAULT_TIMEOUT),
    ]
    
    assert all(t.is_displayed() for t in tiles), \
        f"ERROR: Not all condition tiles are displayed after restarting."
    


# Makes sure enter can select things when highlighted
@pytest.mark.parametrize(
    "browser_types_fixture",
    BROWSER_SUPERLIST,
    indirect=True
)

def test_keyboard_accessibility_starts_guide(browser_types_fixture):
    '''
    Pressing Enter on a focused tile starts the guide
    param: browser_types_fixture- per test web driver from conftest.py
    '''
    driver = browser_types_fixture

    checkPageReady(driver, BASE_URL)
    first = findElementByRoleExisting(driver, "img", "worried face", DEFAULT_TIMEOUT)
    
    # Makes keyboard focus on the first tile it finds
    driver.execute_script("arguments[0].focus();", first)
    
    # Actually sends the Enter key event to the focused element
    driver.execute_script("var e=new KeyboardEvent('keydown',{key:'Enter'}); arguments[0].dispatchEvent(e);", first)
    heading = WebDriverWait(driver, DEFAULT_TIMEOUT).until(
        EC.visibility_of_element_located((By.XPATH, "//*[self::h2 or self::h1][contains(., 'Anxiety & Depression Guide')]"))
    )
    
    assert "Anxiety & Depression Guide" in heading.text, \
        f"ERROR: Expected guide heading after pressing Enter, got {heading.text!r}"