"""
Author: Dien Mai
Role: Scrum Master 4

Purpose:
    End-to-end tests for dropdown functionality in the FAA tool.
    These tests simulate real user behavior in multiple browsers using Selenium.

Tests Implemented:
    1. Open dropdown, select first option, verify page remains stable
    2. Select up to three different options, verifying stability after each
"""

# ---- Imports Required ----
import os
import sys
import pytest

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from unit_test.e2e_helpers import checkPageReady, BASE_URL, DEFAULT_TIMEOUT


# ---- Variables / Constants ----
LOCAL_HOST = os.getenv("BASE_URL", BASE_URL)
E2E_TIMEOUT = int(os.getenv("E2E_TIMEOUT", str(DEFAULT_TIMEOUT)))

# Common selectors for locating dropdowns and their options
NATIVE_DROPDOWN_TAG = "select"
CUSTOM_DROPDOWN_ROOTS = [".dropdown", "[role='combobox']", "[data-testid='dropdown']"]
CUSTOM_OPTION_SELECTORS = [
    "[role='option']",
    ".dropdown-option",
    # fallback containers:
    "[role='listbox'] [role='option']",
    ".dropdown-menu .dropdown-item",
    ".menu .item",
    ".listbox li",
]


# ---- Utilities / Helpers ----
def goto_home(driver):
    """
    Navigate to the app root and wait for the page to be fully loaded.
    """
    checkPageReady(driver, LOCAL_HOST)


def find_dropdown(driver):
    """
    Try to detect a dropdown:
      - First, native <select>
      - Otherwise, a custom dropdown root element
    Returns: ("native"|"custom"|None, WebElement|None)
    """
    native = driver.find_elements(By.TAG_NAME, NATIVE_DROPDOWN_TAG)
    if native:
        return ("native", native[0])

    for sel in CUSTOM_DROPDOWN_ROOTS:
        els = driver.find_elements(By.CSS_SELECTOR, sel)
        if els:
            return ("custom", els[0])

    return (None, None)


def find_options(driver, kind):
    """
    Locate option elements for either a native or custom dropdown.
    Returns: list[WebElement]
    """
    if kind == "native":
        # Prefer scoping to the select when possible, but keep it simple:
        return driver.find_elements(By.TAG_NAME, "option")

    for sel in CUSTOM_OPTION_SELECTORS:
        opts = driver.find_elements(By.CSS_SELECTOR, sel)
        if opts:
            return opts

    return []


def wait_for_dom_stable(driver, timeout=E2E_TIMEOUT):
    """
    Lightweight stability check: the page still has HTML.
    """
    wait = WebDriverWait(driver, timeout)
    return wait.until(lambda d: bool(d.page_source))


def wait_for_dropdown(driver, timeout=E2E_TIMEOUT):
    """
    Wait until a dropdown (native or custom) is present.
    """
    wait = WebDriverWait(driver, timeout)

    def _has_dropdown(d):
        kind, el = find_dropdown(d)
        if el and el.is_displayed():
            return (kind, el)
        return False

    return wait.until(_has_dropdown)


def open_if_custom_and_wait_options(driver, kind, dropdown, timeout=E2E_TIMEOUT):
    """
    For custom dropdowns: click to open, then wait until options are present & visible.
    For native: no-op, just wait for options to exist.
    Returns the current options list.
    """
    wait = WebDriverWait(driver, timeout)

    if kind != "native":
        dropdown.click()

    def _opts_ready(d):
        opts = find_options(d, kind)
        visible = [o for o in opts if o.is_displayed()]
        return visible if visible else False

    return wait.until(_opts_ready)


def select_native_by_index_and_wait(driver, dropdown, index, timeout=E2E_TIMEOUT):
    """
    Select an option in a native <select> and wait until the selected index updates.
    """
    sel = Select(dropdown)
    sel.select_by_index(index)

    wait = WebDriverWait(driver, timeout)
    wait.until(lambda d: Select(dropdown).first_selected_option is not None)
    wait.until(lambda d: Select(dropdown).options[index].is_selected())
    return sel


# ---- Reuse the same superlist approach as baseline test ----
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
UTILS_DIR = os.path.join(ROOT_DIR, "tests", "utils")
sys.path.append(UTILS_DIR)
from driver_variables import BROWSER_SUPERLIST


# ---- Test 1: Open dropdown, select first option, verify page remains stable ----
@pytest.mark.parametrize("browser_types_fixture", BROWSER_SUPERLIST, indirect=True)
def test_Dropdown_Select_First_Option(browser_types_fixture):
    """
    Open dropdown, select first option, and verify page remains stable.
    """
    driver = browser_types_fixture
    goto_home(driver)

    kind, dropdown = wait_for_dropdown(driver)
    assert dropdown is not None, "Could not find a dropdown on the page."

    options = open_if_custom_and_wait_options(driver, kind, dropdown)
    assert options, "No options found for the dropdown."

    if kind == "native":
        # If you want to avoid placeholder options, change index to 1 when available.
        select_native_by_index_and_wait(driver, dropdown, 0)
    else:
        options[0].click()

    wait_for_dom_stable(driver)
    assert driver.page_source, "Page content disappeared after selection."


# ---- Test 2: Select up to three different options, verify stability after each ----
@pytest.mark.parametrize("browser_types_fixture", BROWSER_SUPERLIST, indirect=True)
def test_Dropdown_Select_Multiple_Options(browser_types_fixture):
    """
    Try selecting up to three different options, verifying the page stays stable.
    """
    driver = browser_types_fixture
    goto_home(driver)

    kind, dropdown = wait_for_dropdown(driver)
    assert dropdown is not None, "Dropdown not found."

    # Initial option load (also opens custom dropdown once)
    options = open_if_custom_and_wait_options(driver, kind, dropdown)
    assert options, "No options found in dropdown."

    max_picks = min(3, len(options))
    for i in range(max_picks):
        if kind == "native":
            select_native_by_index_and_wait(driver, dropdown, i)
        else:
            # For custom dropdowns, open before each selection (menus often close after a click)
            options = open_if_custom_and_wait_options(driver, kind, dropdown)
            # Recompute max index safety in case options change
            if i >= len(options):
                break
            options[i].click()

        wait_for_dom_stable(driver)
        assert driver.page_source, f"Page broke after selecting option {i+1}."
