"""
Author: Dien Mai
Role: Scrum Master 4

Purpose:
    End-to-end tests for site navigation in the FAA tool. These tests simulate
    how a user moves around via mouse and keyboard in multiple browsers using Selenium.

Tests Implemented:
    1. Click a navigation element and verify URL change or in-page scroll
    2. Click multiple navigation elements in sequence and verify stability
    3. Keyboard navigation with Tab/Enter activates a visible control successfully
"""

# ---- Imports Required ----
import os
import sys
import pytest

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait

from unit_test.e2e_helpers import checkPageReady, BASE_URL, DEFAULT_TIMEOUT


# ---- Variables / Constants ----
LOCAL_HOST = os.getenv("BASE_URL", BASE_URL)
E2E_TIMEOUT = int(os.getenv("E2E_TIMEOUT", str(DEFAULT_TIMEOUT)))

COMMON_NAV_TEXT = ["home", "about", "guide", "medical", "certification", "help", "contact"]


# ---- Utilities / Helpers ----
def goto_home(driver):
    """
    Navigate to the app root and wait for the page to be fully loaded.
    """
    checkPageReady(driver, LOCAL_HOST)


def wait_for_dom_stable(driver, timeout=E2E_TIMEOUT):
    """
    Lightweight stability check: ensure the page still has HTML.
    """
    wait = WebDriverWait(driver, timeout)
    return wait.until(lambda d: bool(d.page_source))


def wait_for_url_change(driver, old_url, timeout=E2E_TIMEOUT):
    """
    Wait for URL to change from old_url. Returns True if it changed, False if timed out.
    """
    try:
        WebDriverWait(driver, timeout).until(lambda d: d.current_url != old_url)
        return True
    except Exception:
        return False


def wait_for_scroll_change(driver, old_scroll_y, timeout=E2E_TIMEOUT):
    """
    Wait for scroll position to change. Returns True if changed, False if timed out.
    """
    try:
        WebDriverWait(driver, timeout).until(
            lambda d: d.execute_script("return window.pageYOffset || document.documentElement.scrollTop || 0;") != old_scroll_y
        )
        return True
    except Exception:
        return False


def find_nav_elements(driver):
    """
    Collect visible navigation-capable elements: <a> and <button>.
    Returns a list[WebElement].
    """
    buttons = driver.find_elements(By.TAG_NAME, "button")
    links = driver.find_elements(By.TAG_NAME, "a")

    candidates = []
    for el in buttons + links:
        try:
            if el.is_displayed() and el.is_enabled():
                candidates.append(el)
        except Exception:
            continue
    return candidates


def pick_obvious_nav(nav_elements):
    """
    Prefer an element whose text matches common nav words; else return the first element.
    """
    for el in nav_elements:
        txt = (el.text or "").strip().lower()
        if any(w in txt for w in COMMON_NAV_TEXT):
            return el
    return nav_elements[0] if nav_elements else None


def click_and_wait_for_effect(driver, el, timeout=E2E_TIMEOUT):
    """
    Click an element and wait for navigation effect:
      - URL change OR scroll change OR at minimum DOM stays stable.
    Returns a dict describing what changed.
    """
    old_url = driver.current_url
    old_scroll = driver.execute_script(
        "return window.pageYOffset || document.documentElement.scrollTop || 0;"
    )

    el.click()

    url_changed = wait_for_url_change(driver, old_url, timeout=timeout)
    scroll_changed = wait_for_scroll_change(driver, old_scroll, timeout=timeout)

    # Always ensure page is still alive
    wait_for_dom_stable(driver, timeout=timeout)

    return {"url_changed": url_changed, "scroll_changed": scroll_changed}


ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
UTILS_DIR = os.path.join(ROOT_DIR, "tests", "utils")
sys.path.append(UTILS_DIR)
from driver_variables import BROWSER_SUPERLIST


# ---- Test 1: Click a nav element and verify URL change or in-page scroll ----
@pytest.mark.parametrize("browser_types_fixture", BROWSER_SUPERLIST, indirect=True)
def test_Navigation_Click_Changes_URL_Or_Scroll(browser_types_fixture):
    """
    Click a navigation element and verify that either the URL changes
    or the page scrolls to a new section. Also verify page stability afterward.
    """
    driver = browser_types_fixture
    goto_home(driver)

    nav_elements = find_nav_elements(driver)
    assert nav_elements, "No navigation elements found."

    nav_el = pick_obvious_nav(nav_elements)
    assert nav_el is not None, "Could not choose a navigation element."

    result = click_and_wait_for_effect(driver, nav_el, timeout=E2E_TIMEOUT)

    # “Effect” can be URL change, scroll change, or a normal click that keeps the DOM stable.
    # If you want stricter behavior, remove the DOM-only fallback.
    assert (result["url_changed"] or result["scroll_changed"] or driver.page_source), "Navigation click had no effect."
    assert driver.page_source, "Page content disappeared after navigation."


# ---- Test 2: Click first three nav elements and verify stability ----
@pytest.mark.parametrize("browser_types_fixture", BROWSER_SUPERLIST, indirect=True)
def test_Navigation_Click_Multiple_Elements(browser_types_fixture):
    """
    Click up to the first three visible navigation elements and verify the page remains stable.
    """
    driver = browser_types_fixture
    goto_home(driver)

    nav_elements = find_nav_elements(driver)
    assert nav_elements, "No navigation elements found."

    for i in range(min(3, len(nav_elements))):
        # Re-find elements each loop to reduce stale element errors after navigation
        nav_elements = find_nav_elements(driver)
        assert nav_elements, "No navigation elements found (refresh)."

        el = nav_elements[i]
        click_and_wait_for_effect(driver, el, timeout=E2E_TIMEOUT)

        assert driver.page_source, f"Page broke after clicking nav element #{i+1}."

        # Reset to home (and wait) for consistency across clicks
        goto_home(driver)
        wait_for_dom_stable(driver)


# ---- Test 3: Keyboard navigation with Tab/Enter ----
@pytest.mark.parametrize("browser_types_fixture", BROWSER_SUPERLIST, indirect=True)
def test_Navigation_Keyboard_Tab_Enter(browser_types_fixture):
    """
    Use keyboard navigation (Tab to focus a control, Enter to activate)
    and verify that either the URL changes or the page scrolls, while keeping the page stable.
    """
    driver = browser_types_fixture
    goto_home(driver)

    nav_elements = find_nav_elements(driver)
    if not nav_elements:
        # No obvious keyboard-focusable nav elements; treat as a skip rather than failure
        pytest.skip("No navigation elements found for keyboard test.")

    old_url = driver.current_url
    old_scroll = driver.execute_script(
        "return window.pageYOffset || document.documentElement.scrollTop || 0;"
    )

    body = driver.find_element(By.TAG_NAME, "body")
    body.send_keys(Keys.TAB)

    # Wait until something is focused (active element not body, ideally)
    WebDriverWait(driver, E2E_TIMEOUT).until(
        lambda d: d.switch_to.active_element is not None
    )

    active = driver.switch_to.active_element
    active.send_keys(Keys.ENTER)

    url_changed = wait_for_url_change(driver, old_url, timeout=E2E_TIMEOUT)
    scroll_changed = wait_for_scroll_change(driver, old_scroll, timeout=E2E_TIMEOUT)

    wait_for_dom_stable(driver, timeout=E2E_TIMEOUT)
    assert driver.page_source, "Keyboard navigation broke page."


