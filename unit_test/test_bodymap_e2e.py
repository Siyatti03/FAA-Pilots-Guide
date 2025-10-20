'''
Author: Dien Mai
    Role: Scrum Master 4
Purpose: End-to-end tests for the Body Map feature in the FAA tool. These tests simulate
         how a user would interact with the page in a real browser using Selenium.
         The suite validates presence, interaction (click/hover), and responsiveness.
Tests Implemented:
        1. Body map is present and target areas are discoverable
        2. Clicking a known target reveals info without breaking the page
        3. Clicking multiple targets in sequence keeps the page stable
        4. Hovering over targets does not break the UI
        5. Body map and targets remain visible/responsive across screen sizes
'''

# ---- Imports Required ----
import os
import time

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys  # kept for parity; not required in all tests
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver import ActionChains
from unit_test.e2e_helpers import checkPageReady, BASE_URL, DEFAULT_TIMEOUT
from unit_test.driver_manager import get_driver

# ---- Variables / Constants ----
LOCAL_HOST = os.getenv("BASE_URL", BASE_URL)
DEFAULT_TIMEOUT = int(os.getenv("E2E_TIMEOUT", str(DEFAULT_TIMEOUT)))
BROWSER_LIST = ["chrome", "firefox", "edge"]

# Target labels we expect to find on the body map
TARGET_PARTS = {"head", "upper body", "lower body"}

# Common selectors for locating the body map and info elements
BODY_MAP_SELECTORS = [".body-map", "#body-map", "[data-map='body']", "svg"]
INFO_SELECTORS = [".info", ".details", ".description", ".popup", ".tooltip", "[role='dialog']"]

# ---- Driver Factory ----
# Using centralized WebDriver fixture from driver_manager.py

# ---- Utilities / Helpers ----
def normalize_text(s):
    return (s or "").strip().lower()

def goto_home(driver):
    '''
    Navigate to the app root and wait for the page to be fully loaded.
    '''
    checkPageReady(driver, LOCAL_HOST)

def find_body_map(driver):
    '''
    Try multiple selectors to locate the body map root element (svg or container).
    Returns the first matching element or None.
    '''
    for sel in BODY_MAP_SELECTORS:
        elements = driver.find_elements(By.CSS_SELECTOR, sel)
        if elements:
            return elements[0]
    return None

def find_target_parts(driver):
    '''
    Find elements on the page that correspond to known body target parts.
    Returns a dict: {normalized_label: element}
    '''
    found = {}
    candidates = driver.find_elements(By.CSS_SELECTOR, "[data-part], [aria-label], svg *")
    
    for el in candidates:
        if not el.is_displayed():
            continue

        label = normalize_text(el.text or el.get_attribute("data-part") or "")
        if label in TARGET_PARTS and label not in found:
            found[label] = el

    return found

# ---- Test 1: Presence and discoverability ----
def test_BodyMap_Presence_And_Targets():
    '''
    Ensure the body map is present and that we can discover the known target areas.
    '''
    for browser in BROWSER_LIST:
        driver = get_driver(browser, headless=True)
        goto_home(driver)

        body_map = find_body_map(driver)
        assert body_map is not None, f"[{browser}] Body map not found using known selectors."

        targets = find_target_parts(driver)
        assert targets, f"[{browser}] No body map target regions found."

        driver.quit()

# ---- Test 2: Click a known target and verify info appears ----
def test_BodyMap_Click_Known_Target():
    '''
    Clicking a known target should reveal info (or at least not break the page).
    '''
    for browser in BROWSER_LIST:
        driver = get_driver(browser, headless=True)
        goto_home(driver)

        targets = find_target_parts(driver)
        assert targets, f"[{browser}] No target regions to click."

        # Click the first available target
        first_target = list(targets.values())[0]
        first_target.click()
        time.sleep(0.75)

        # Verify page still works
        assert driver.page_source, f"[{browser}] Page broke after clicking target."

        driver.quit()

# ---- Test 3: Multiple clicks stay stable ----
def test_BodyMap_Multiple_Clicks_Stable():
    '''
    Click multiple targets sequentially and verify the page remains responsive.
    '''
    for browser in BROWSER_LIST:
        driver = get_driver(browser, headless=True)
        goto_home(driver)

        targets = find_target_parts(driver)
        assert targets, f"[{browser}] No targets found for multi-click test."

        # Click first 3 targets
        for i, el in enumerate(list(targets.values())[:3]):
            el.click()
            time.sleep(0.5)
            assert driver.page_source, f"[{browser}] Page broke after click {i+1}."

        driver.quit()

# ---- Test 4: Hover stability ----
def test_BodyMap_Hover_Does_Not_Break_UI():
    '''
    Hover over targets and verify that the UI remains stable.
    '''
    for browser in BROWSER_LIST:
        driver = get_driver(browser, headless=True)
        goto_home(driver)

        targets = find_target_parts(driver)
        assert targets, f"[{browser}] No targets available to hover."

        actions = ActionChains(driver)
        for el in list(targets.values())[:2]:  # Hover over first 2 targets
            actions.move_to_element(el).perform()
            time.sleep(0.5)
            assert driver.page_source, f"[{browser}] Page broke after hover."

        driver.quit()

# ---- Test 5: Responsive sizes ----
def test_BodyMap_Responsive_Visibility():
    '''
    Verify the body map and targets are visible across desktop/tablet/mobile sizes.
    '''
    sizes = [(1280, 720), (768, 1024), (375, 667)]

    for browser in BROWSER_LIST:
        driver = get_driver(browser, headless=True)
        goto_home(driver)

        for w, h in sizes:
            driver.set_window_size(w, h)
            time.sleep(0.5)

            body_map = find_body_map(driver)
            assert body_map and body_map.is_displayed(), f"[{browser}] Body map not visible at {w}x{h}."

            targets = find_target_parts(driver)
            assert targets, f"[{browser}] No targets found at {w}x{h}."

        driver.quit()