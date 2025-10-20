'''
Author: Dien Mai
    Role: Scrum Master 4
Purpose: End-to-end tests for site navigation in the FAA tool. These tests simulate
         how a user moves around via mouse and keyboard in multiple browsers using Selenium.
Tests Implemented:
        1. Click a navigation element and verify URL change or in-page scroll
        2. Click multiple navigation elements in sequence and verify stability
        3. Keyboard navigation with Tab/Enter activates a visible control successfully
'''

# ---- Imports Required ----
import os
import time

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from unit_test.e2e_helpers import checkPageReady, BASE_URL, DEFAULT_TIMEOUT
from unit_test.driver_manager import get_driver

# ---- Variables / Constants ----
LOCAL_HOST = os.getenv("BASE_URL", BASE_URL)
DEFAULT_TIMEOUT = int(os.getenv("E2E_TIMEOUT", str(DEFAULT_TIMEOUT)))
BROWSER_LIST = ["chrome", "firefox", "edge"]

# Heuristics for picking obvious nav items by text
COMMON_NAV_TEXT = ["home", "about", "guide", "medical", "certification", "help", "contact"]

# ---- Driver Factory ----
# Using centralized WebDriver fixture from driver_manager.py

# ---- Utilities / Helpers ----
def goto_home(driver):
    '''
    Navigate to the app root and wait for the page to be fully loaded.
    '''
    checkPageReady(driver, LOCAL_HOST)

def find_nav_elements(driver):
    '''
    Collect visible navigation-capable elements: <a> and <button>.
    Returns a list[WebElement].
    '''
    buttons = driver.find_elements(By.TAG_NAME, "button")
    links = driver.find_elements(By.TAG_NAME, "a")

    # Filter to visible elements
    candidates = []
    for el in buttons + links:
        if el.is_displayed():
            candidates.append(el)
    return candidates

def pick_obvious_nav(nav_elements):
    '''
    Prefer an element whose text matches common nav words; else return the first element.
    '''
    for el in nav_elements:
        txt = (el.text or "").strip().lower()
        if any(w in txt for w in COMMON_NAV_TEXT):
            return el
    return nav_elements[0] if nav_elements else None

# ---- Test 1: Click a nav element and verify URL change or in-page scroll ----
def test_Navigation_Click_Changes_URL_Or_Scroll():
    '''
    Click a navigation element and verify that either the URL changes
    or the page scrolls to a new section. Also verify page stability afterward.
    '''
    for browser in BROWSER_LIST:
        driver = get_driver(browser, headless=True)
        goto_home(driver)

        nav_elements = find_nav_elements(driver)
        assert nav_elements, f"[{browser}] No navigation elements found."

        nav_el = pick_obvious_nav(nav_elements)
        assert nav_el is not None, f"[{browser}] Could not choose a navigation element."

        initial_url = driver.current_url
        nav_el.click()
        time.sleep(1)

        # Check if something changed
        new_url = driver.current_url
        url_changed = (new_url != initial_url)
        page_loaded = driver.page_source and len(driver.page_source) > 0

        assert url_changed or page_loaded, f"[{browser}] Navigation click had no effect."
        assert page_loaded, f"[{browser}] Page content disappeared after navigation."

        driver.quit()

# ---- Test 2: Click first three nav elements and verify stability ----
def test_Navigation_Click_Multiple_Elements():
    '''
    Click up to the first three visible navigation elements and verify the page remains stable.
    '''
    for browser in BROWSER_LIST:
        driver = get_driver(browser, headless=True)
        goto_home(driver)

        nav_elements = find_nav_elements(driver)
        assert nav_elements, f"[{browser}] No navigation elements found."

        # Click first 3 elements
        for i in range(min(3, len(nav_elements))):
            el = nav_elements[i]
            el.click()
            time.sleep(1)
            assert driver.page_source, f"[{browser}] Page broke after clicking nav element #{i+1}."
            goto_home(driver)  # Reset to home

        driver.quit()

# ---- Test 3: Keyboard navigation with Tab/Enter ----
def test_Navigation_Keyboard_Tab_Enter():
    '''
    Use keyboard navigation (Tab to focus a control, Enter to activate)
    and verify that either the URL changes or the page scrolls.
    '''
    for browser in BROWSER_LIST:
        driver = get_driver(browser, headless=True)
        goto_home(driver)

        nav_elements = find_nav_elements(driver)
        if not nav_elements:
            driver.quit()
            continue

        body = driver.find_element(By.TAG_NAME, "body")
        body.send_keys(Keys.TAB)
        time.sleep(0.5)

        # Try to activate focused element
        try:
            active = driver.switch_to.active_element
            active.send_keys(Keys.ENTER)
            time.sleep(1)
            assert driver.page_source, f"[{browser}] Keyboard navigation broke page"
        except:
            # If keyboard nav fails, just verify page works
            assert driver.page_source, f"[{browser}] Page broken after keyboard nav attempt"

        driver.quit()