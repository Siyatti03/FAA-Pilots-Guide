'''
Author: Dien Mai
    Role: Scrum Master 4
Purpose: End-to-end tests for dropdown functionality in the FAA tool.
         These tests simulate real user behavior in multiple browsers using Selenium.
Tests Implemented:
        1. Open dropdown, select first option, verify page remains stable
        2. Select up to three different options, verifying stability after each
'''

# ---- Imports Required ----
import os
import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions
from unit_test.e2e_helpers import checkPageReady, BASE_URL, DEFAULT_TIMEOUT
from unit_test.driver_manager import get_driver
# (ActionChains not needed here)

# ---- Variables / Constants ----
LOCAL_HOST = os.getenv("BASE_URL", BASE_URL)
DEFAULT_TIMEOUT = int(os.getenv("E2E_TIMEOUT", str(DEFAULT_TIMEOUT)))
BROWSER_LIST = ["chrome", "firefox", "edge"]

# Common selectors for locating dropdowns and their options
NATIVE_DROPDOWN_TAG = "select"
CUSTOM_DROPDOWN_ROOTS = [".dropdown", "[role='combobox']", "[data-testid='dropdown']"]
CUSTOM_OPTION_SELECTORS = [
    "[role='option']", ".dropdown-option",
    # fallback containers:
    "[role='listbox'] [role='option']",
    ".dropdown-menu .dropdown-item",
    ".menu .item", ".listbox li"
]

# ---- Driver Factory ----
# Using centralized WebDriver fixture from driver_manager.py

# ---- Utilities / Helpers ----
def goto_home(driver):
    '''
    Navigate to the app root and wait for the page to be fully loaded.
    '''
    checkPageReady(driver, LOCAL_HOST)

def find_dropdown(driver):
    '''
    Try to detect a dropdown:
    - First, native <select>
    - Otherwise, a custom dropdown root element
    Returns a tuple: ("native"|"custom"|None, WebElement|None)
    '''
    # Native <select>
    native = driver.find_elements(By.TAG_NAME, NATIVE_DROPDOWN_TAG)
    if native:
        return ("native", native[0])

    # Custom dropdown roots
    for sel in CUSTOM_DROPDOWN_ROOTS:
        els = driver.find_elements(By.CSS_SELECTOR, sel)
        if els:
            return ("custom", els[0])

    return (None, None)

def find_options(driver, kind):
    '''
    Locate option elements for either a native or custom dropdown.
    Returns a list[WebElement].
    '''
    if kind == "native":
        return driver.find_elements(By.TAG_NAME, "option")

    # For custom dropdowns, try explicit option markers first
    for sel in CUSTOM_OPTION_SELECTORS:
        opts = driver.find_elements(By.CSS_SELECTOR, sel)
        if opts:
            return opts

    return []

def open_if_custom(driver, kind, dropdown):
    '''
    Ensure the options are visible for custom dropdowns (click to open).
    No-op for native selects.
    '''
    if kind != "native":
        dropdown.click()
        time.sleep(0.3)  # allow menu to render

# ---- Test 1: Open dropdown, select first option, verify page remains stable ----
def test_Dropdown_Select_First_Option():
    '''
    Open dropdown, select first option, and verify page remains stable.
    '''
    for browser in BROWSER_LIST:
        driver = get_driver(browser, headless=True)
        goto_home(driver)

        # Locate dropdown
        kind, dropdown = find_dropdown(driver)
        assert dropdown is not None, f"[{browser}] Could not find a dropdown on the page."

        # Open if custom
        open_if_custom(driver, kind, dropdown)

        # Find options
        options = find_options(driver, kind or "")
        assert options, f"[{browser}] No options found for the dropdown."

        # Select first option
        first = options[0]
        if kind == "native":
            sel = Select(dropdown)
            sel.select_by_index(0)
        else:
            first.click()

        time.sleep(0.4)
        assert driver.page_source, f"[{browser}] Page content disappeared after selection."

        driver.quit()

# ---- Test 2: Select up to three different options, verify stability after each ----
def test_Dropdown_Select_Multiple_Options():
    '''
    Try selecting up to three different options, verifying the page stays stable.
    '''
    for browser in BROWSER_LIST:
        driver = get_driver(browser, headless=True)
        goto_home(driver)

        kind, dropdown = find_dropdown(driver)
        assert dropdown is not None, f"[{browser}] Dropdown not found."

        # For custom dropdowns, open once before reading options
        open_if_custom(driver, kind, dropdown)

        options = find_options(driver, kind or "")
        assert options, f"[{browser}] No options found in dropdown."

        # Select first 3 options
        for i in range(min(3, len(options))):
            if kind != "native":
                # Reopen for custom dropdowns
                open_if_custom(driver, kind, dropdown)
                options = find_options(driver, kind or "")

            opt = options[i]
            if kind == "native":
                sel = Select(dropdown)
                sel.select_by_index(i)
            else:
                opt.click()

            time.sleep(0.4)
            assert driver.page_source, f"[{browser}] Page broke after selecting option {i+1}."

        driver.quit()