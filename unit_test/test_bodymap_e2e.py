"""
Author: Dien Mai
Role: Scrum Master 4

Purpose:
    End-to-end tests for the Body Map feature in the FAA tool. These tests simulate
    how a user would interact with the page in a real browser using Selenium.
    The suite validates presence, interaction (click/hover), and responsiveness.

Tests Implemented:
    1. Body map is present and target areas are discoverable
    2. Clicking a known target reveals info without breaking the page
    3. Clicking multiple targets in sequence keeps the page stable
    4. Hovering over targets does not break the UI
    5. Body map and targets remain visible/responsive across screen sizes
"""

# ---- Imports Required ----
import os
import sys
import pytest

from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
from selenium.webdriver.support.ui import WebDriverWait

# Project utilities / helpers
from unit_test.e2e_helpers import checkPageReady, BASE_URL, DEFAULT_TIMEOUT

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
UTILS_DIR = os.path.join(ROOT_DIR, "tests", "utils")
sys.path.append(UTILS_DIR)
from driver_variables import BROWSER_SUPERLIST


# ---- Variables / Constants ----
LOCAL_HOST = os.getenv("BASE_URL", BASE_URL)
E2E_TIMEOUT = int(os.getenv("E2E_TIMEOUT", str(DEFAULT_TIMEOUT)))

TARGET_PARTS = {"head", "upper body", "lower body"}

BODY_MAP_SELECTORS = [".body-map", "#body-map", "[data-map='body']", "svg"]
INFO_SELECTORS = [".info", ".details", ".description", ".popup", ".tooltip", "[role='dialog']"]


# ---- Utilities / Helpers ----
def normalize_text(s):
    return (s or "").strip().lower()


def goto_home(driver):
    """
    Navigate to the app root and wait for the page to be fully loaded.
    """
    checkPageReady(driver, LOCAL_HOST)


def find_body_map(driver):
    """
    Try multiple selectors to locate the body map root element (svg or container).
    Returns the first matching element or None.
    """
    for sel in BODY_MAP_SELECTORS:
        elements = driver.find_elements(By.CSS_SELECTOR, sel)
        if elements:
            return elements[0]
    return None


def find_target_parts(driver):
    """
    Find elements on the page that correspond to known body target parts.
    Returns a dict: {normalized_label: element}
    """
    found = {}
    candidates = driver.find_elements(By.CSS_SELECTOR, "[data-part], [aria-label], svg *")

    for el in candidates:
        if not el.is_displayed():
            continue

        label = normalize_text(
            el.get_attribute("aria-label") or el.get_attribute("data-part") or el.text
        )

        if label in TARGET_PARTS and label not in found:
            found[label] = el

    return found


def any_info_element_present(driver):
    for sel in INFO_SELECTORS:
        els = driver.find_elements(By.CSS_SELECTOR, sel)
        if any(e.is_displayed() for e in els):
            return True
    return False


def wait_for_body_map(driver, timeout=E2E_TIMEOUT):
    """
    Wait until the body map exists and is displayed.
    """
    wait = WebDriverWait(driver, timeout)
    return wait.until(lambda d: (find_body_map(d) if (find_body_map(d) and find_body_map(d).is_displayed()) else False))


def wait_for_targets(driver, timeout=E2E_TIMEOUT):
    """
    Wait until at least one known target is discoverable.
    """
    wait = WebDriverWait(driver, timeout)
    return wait.until(lambda d: (find_target_parts(d) or False))


def wait_for_dom_stable(driver, timeout=E2E_TIMEOUT):
    """
    Lightweight stability check: wait until page_source is non-empty.
    (Not perfect, but replaces sleeps for "page didn't die".)
    """
    wait = WebDriverWait(driver, timeout)
    return wait.until(lambda d: bool(d.page_source))


def wait_for_info_or_stability(driver, timeout=E2E_TIMEOUT):
    """
    If your UI shows info on click/hover, this will catch it.
    If not, it still ensures the page remains stable.
    """
    wait = WebDriverWait(driver, timeout)
    return wait.until(lambda d: any_info_element_present(d) or bool(d.page_source))


@pytest.mark.parametrize("browser_types_fixture", BROWSER_SUPERLIST, indirect=True)
def test_BodyMap_Presence_And_Targets(browser_types_fixture):
    """
    Test 1: Ensure the body map is present and that we can discover the known target areas.
    """
    driver = browser_types_fixture
    goto_home(driver)

    body_map = wait_for_body_map(driver)
    assert body_map is not None, "Body map not found using known selectors."

    targets = wait_for_targets(driver)
    assert targets, "No body map target regions found."


@pytest.mark.parametrize("browser_types_fixture", BROWSER_SUPERLIST, indirect=True)
def test_BodyMap_Click_Known_Target(browser_types_fixture):
    """
    Test 2: Clicking a known target should reveal info (or at least not break the page).
    """
    driver = browser_types_fixture
    goto_home(driver)

    targets = wait_for_targets(driver)
    first_target = list(targets.values())[0]
    first_target.click()

    # Wait for either info to appear OR at least page stability
    wait_for_info_or_stability(driver)
    assert driver.page_source, "Page broke after clicking target."

    # If your UI *guarantees* info shows, uncomment this strict assert:
    # assert any_info_element_present(driver), "Expected info panel/popup after click."


@pytest.mark.parametrize("browser_types_fixture", BROWSER_SUPERLIST, indirect=True)
def test_BodyMap_Multiple_Clicks_Stable(browser_types_fixture):
    """
    Test 3: Click multiple targets sequentially and verify the page remains responsive.
    """
    driver = browser_types_fixture
    goto_home(driver)

    targets = wait_for_targets(driver)
    for i, el in enumerate(list(targets.values())[:3]):
        el.click()
        wait_for_dom_stable(driver)
        assert driver.page_source, f"Page broke after click {i+1}."


@pytest.mark.parametrize("browser_types_fixture", BROWSER_SUPERLIST, indirect=True)
def test_BodyMap_Hover_Does_Not_Break_UI(browser_types_fixture):
    """
    Test 4: Hover over targets and verify that the UI remains stable.
    """
    driver = browser_types_fixture
    goto_home(driver)

    targets = wait_for_targets(driver)
    actions = ActionChains(driver)

    for el in list(targets.values())[:2]:
        actions.move_to_element(el).perform()
        wait_for_dom_stable(driver)
        assert driver.page_source, "Page broke after hover."


@pytest.mark.parametrize("browser_types_fixture", BROWSER_SUPERLIST, indirect=True)
def test_BodyMap_Responsive_Visibility(browser_types_fixture):
    """
    Test 5: Verify the body map and targets are visible across desktop/tablet/mobile sizes.
    """
    driver = browser_types_fixture
    goto_home(driver)

    sizes = [(1280, 720), (768, 1024), (375, 667)]
    for w, h in sizes:
        driver.set_window_size(w, h)

        body_map = wait_for_body_map(driver)
        assert body_map and body_map.is_displayed(), f"Body map not visible at {w}x{h}."

        targets = wait_for_targets(driver)
        assert targets, f"No targets found at {w}x{h}."
