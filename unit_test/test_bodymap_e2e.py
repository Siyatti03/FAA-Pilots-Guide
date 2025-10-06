"""
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
"""

# ---- Imports Required ----
import os

from selenium import webdriver
from selenium.webdriver.common.by import By
# from selenium.webdriver.common.keys import Keys  # removed (unused)
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import ActionChains

# ---- Variables / Constants ----
LOCAL_HOST = os.getenv("BASE_URL", "http://localhost:3000").rstrip("/")
DEFAULT_TIMEOUT = int(os.getenv("E2E_TIMEOUT", "10"))
BROWSER_LIST = ["chrome", "firefox", "edge"]

# Target labels we expect to find on the body map
TARGET_PARTS = {"head", "upper body", "lower body"}

# Common selectors for locating the body map and info elements
BODY_MAP_SELECTORS = [".body-map", "#body-map", "[data-map='body']", "svg"]
INFO_SELECTORS = [".info", ".details", ".description", ".popup", ".tooltip", "[role='dialog']"]
TOOLTIP_SELECTORS = ["[role='tooltip']", ".tooltip"]

# ---- Download the necessary drivers / Driver Factory ----
def get_driver(browser, headless=True):
    """
    Return a Selenium WebDriver for the given browser.
    rtype: webdriver
    browser - The browser being used ("chrome", "firefox", "edge")
    headless - If True, run without a visible UI (useful for CI)
    """
    if browser.lower() == "chrome":
        from selenium.webdriver.chrome.service import Service as ChromeService
        from selenium.webdriver.chrome.options import Options
        from webdriver_manager.chrome import ChromeDriverManager

        options = Options()
        if headless:
            options.add_argument("--headless=new")
        options.add_argument("--window-size=1280,720")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")

        driver = webdriver.Chrome(
            service=ChromeService(ChromeDriverManager().install()),
            options=options
        )
        driver.set_page_load_timeout(30)
        return driver

    elif browser.lower() == "firefox":
        from selenium.webdriver.firefox.service import Service as FirefoxService
        from selenium.webdriver.firefox.options import Options
        from webdriver_manager.firefox import GeckoDriverManager

        options = Options()
        if headless:
            options.add_argument("--headless")
        driver = webdriver.Firefox(
            service=FirefoxService(GeckoDriverManager().install()),
            options=options
        )
        driver.set_page_load_timeout(30)
        driver.set_window_size(1280, 720)
        return driver

    elif browser.lower() == "edge":
        from selenium.webdriver.edge.service import Service as EdgeService
        from selenium.webdriver.edge.options import Options
        from webdriver_manager.microsoft import EdgeChromiumDriverManager

        options = Options()
        if headless:
            options.add_argument("--headless=new")
        options.add_argument("--window-size=1280,720")

        driver = webdriver.Edge(
            service=EdgeService(EdgeChromiumDriverManager().install()),
            options=options
        )
        driver.set_page_load_timeout(30)
        return driver

# ---- Utilities / Helpers ----
def normalize_text(s):
    return (s or "").strip().lower()

def goto_home(driver):
    """
    Navigate to the app root and wait for the page to be fully loaded.
    """
    driver.get(LOCAL_HOST)
    WebDriverWait(driver, timeout=DEFAULT_TIMEOUT).until(
        lambda d: d.execute_script("return document.readyState") == "complete"
    )

def find_body_map(driver):
    """
    Try multiple selectors to locate the body map root element (svg or container).
    Returns the first matching element or None.
    """
    for sel in BODY_MAP_SELECTORS:
        try:
            elements = driver.find_elements(By.CSS_SELECTOR, sel)
            if elements:
                return elements[0]
        except Exception:
            pass
    return None

def extract_label(el):
    """
    Extract a human-readable label for a body part from attributes or text.
    """
    for attr in ("data-part", "aria-label", "title"):
        try:
            v = el.get_attribute(attr)
            if v:
                return v
        except Exception:
            pass
    try:
        return el.text
    except Exception:
        return ""

def find_target_parts(driver):
    """
    Find elements on the page that correspond to known body target parts.
    Returns a dict: {normalized_label: element}
    """
    found = {}
    candidates = driver.find_elements(By.CSS_SELECTOR, "[data-part], [aria-label], [title], svg *, *")
    for el in candidates:
        try:
            if not el.is_displayed():
                continue
        except Exception:
            continue

        label = normalize_text(extract_label(el))
        if label in TARGET_PARTS and label not in found:
            found[label] = el
            if len(found) == len(TARGET_PARTS):
                break
    return found

def any_visible(driver, selectors):
    """
    Return True if any element matching any selector is displayed.
    """
    for sel in selectors:
        try:
            elems = driver.find_elements(By.CSS_SELECTOR, sel)
            if any(e.is_displayed() for e in elems):
                return True
        except Exception:
            continue
    return False

def wait_info_visible(driver):
    """
    Wait for an info/panel/tooltip/dialog to become visible after an interaction.
    Conditions:
      - any INFO_SELECTORS visible
      - OR a [role='dialog'][aria-hidden='false'] visible
      - OR any element with [aria-expanded='true'] visible
    """
    def _info():
        if any_visible(driver, INFO_SELECTORS):
            return True
        try:
            dialogs = driver.find_elements(By.CSS_SELECTOR, "[role='dialog']")
            for d in dialogs:
                if d.is_displayed() and (d.get_attribute("aria-hidden") in (None, "", "false")):
                    return True
        except Exception:
            pass
        try:
            expanded = driver.find_elements(By.CSS_SELECTOR, "[aria-expanded='true']")
            if any(e.is_displayed() for e in expanded):
                return True
        except Exception:
            pass
        return False

    WebDriverWait(driver, DEFAULT_TIMEOUT).until(lambda d: _info())

def wait_bodymap_visible(driver):
    """
    Wait for the body map root to be present and visible.
    """
    def _visible(d):
        for sel in BODY_MAP_SELECTORS:
            try:
                elems = d.find_elements(By.CSS_SELECTOR, sel)
                if any(e.is_displayed() for e in elems):
                    return True
            except Exception:
                continue
        return False

    WebDriverWait(driver, DEFAULT_TIMEOUT).until(_visible)

def assert_panel_or_state_visible(driver, target_el=None):
    """
    Replace page_source checks: assert that either an info panel is visible
    OR a target element reflects an 'active/open' state via class/aria.
    """
    if any_visible(driver, INFO_SELECTORS + TOOLTIP_SELECTORS):
        return
    # aria/dialog states
    dialogs = driver.find_elements(By.CSS_SELECTOR, "[role='dialog']")
    for d in dialogs:
        if d.is_displayed() and (d.get_attribute("aria-hidden") in (None, "", "false")):
            return
    if any(e.is_displayed() for e in driver.find_elements(By.CSS_SELECTOR, "[aria-expanded='true']")):
        return
    # active class on target or ancestors (common pattern)
    if target_el is not None:
        try:
            classes = (target_el.get_attribute("class") or "").split()
            if any(c in ("active", "selected", "open") for c in classes):
                return
            parent = target_el.find_element(By.XPATH, "..")
            classes_p = (parent.get_attribute("class") or "").split()
            if any(c in ("active", "selected", "open") for c in classes_p):
                return
        except Exception:
            pass
    raise AssertionError("No visible info/panel/tooltip and no active/expanded state detected.")

def wait_layout_settled_after_resize(driver, w, h):
    """
    Wait until the window size reflects the requested size and the body map is visible.
    """
    def _settled(d):
        size_ok = d.execute_script("return [window.innerWidth, window.innerHeight];")
        return (int(size_ok[0]) == int(w)) and (int(size_ok[1]) == int(h))
    WebDriverWait(driver, DEFAULT_TIMEOUT).until(_settled)
    wait_bodymap_visible(driver)

# ---- Test 1: Presence and discoverability ----
def test_BodyMap_Presence_And_Targets():
    """
    Ensure the body map is present and that we can discover the known target areas.
    """
    for browser in BROWSER_LIST:
        driver = get_driver(browser, headless=True)
        try:
            goto_home(driver)

            # Wait for the body map to be visible
            wait_bodymap_visible(driver)
            body_map = find_body_map(driver)
            assert body_map is not None and body_map.is_displayed(), f"[{browser}] Body map not found using known selectors."

            targets = find_target_parts(driver)
            assert targets, f"[{browser}] No body map target regions found."
            assert any(k in targets for k in TARGET_PARTS), f"[{browser}] Expected target labels not discovered."
        finally:
            driver.quit()

# ---- Test 2: Click a known target and verify info appears ----
def test_BodyMap_Click_Known_Target():
    """
    Clicking a known target should reveal info (or at least not break the page).
    """
    for browser in BROWSER_LIST:
        driver = get_driver(browser, headless=True)
        try:
            goto_home(driver)
            wait_bodymap_visible(driver)

            targets = find_target_parts(driver)
            assert targets, f"[{browser}] No target regions to click."

            # Click the first available known target in a preferred order
            clicked = None
            for key in ("head", "upper body", "lower body"):
                if key in targets:
                    el = targets[key]
                    # ensure clickable
                    WebDriverWait(driver, DEFAULT_TIMEOUT).until(EC.element_to_be_clickable(el))
                    el.click()
                    clicked = el
                    break

            # Wait specifically for an info/panel/expanded state (replaces time.sleep)
            wait_info_visible(driver)

            # Assert visible panel or state instead of page_source
            assert_panel_or_state_visible(driver, target_el=clicked)
        finally:
            driver.quit()

# ---- Test 3: Multiple clicks stay stable ----
def test_BodyMap_Multiple_Clicks_Stable():
    """
    Click multiple targets sequentially and verify the page remains responsive.
    """
    for browser in BROWSER_LIST:
        driver = get_driver(browser, headless=True)
        try:
            goto_home(driver)
            wait_bodymap_visible(driver)

            targets = find_target_parts(driver)
            assert targets, f"[{browser}] No targets found for multi-click test."

            order = [k for k in ("head", "upper body", "lower body") if k in targets]
            assert order, f"[{browser}] No matching labeled targets to click."

            for idx, key in enumerate(order, start=1):
                el = targets[key]
                WebDriverWait(driver, DEFAULT_TIMEOUT).until(EC.element_to_be_clickable(el))
                el.click()

                # Wait for bodymap-driven UI signal (panel/expanded)
                wait_info_visible(driver)
                # Replace page_source with visible state assertion
                assert_panel_or_state_visible(driver, target_el=el)
        finally:
            driver.quit()

# ---- Test 4: Hover stability ----
def test_BodyMap_Hover_Does_Not_Break_UI():
    """
    Hover over up to two targets and verify that the UI remains stable.
    """
    for browser in BROWSER_LIST:
        driver = get_driver(browser, headless=True)
        try:
            goto_home(driver)
            wait_bodymap_visible(driver)

            targets = find_target_parts(driver)
            keys = [k for k in ("head", "upper body", "lower body") if k in targets][:2]
            assert keys, f"[{browser}] No targets available to hover."

            actions = ActionChains(driver)
            body_map = find_body_map(driver)
            for key in keys:
                el = targets[key]
                actions.move_to_element(el).perform()

                # Wait for either tooltip/panel to appear OR at least body map remains visible
                try:
                    WebDriverWait(driver, DEFAULT_TIMEOUT).until(
                        lambda d: any_visible(d, TOOLTIP_SELECTORS) or (body_map.is_displayed())
                    )
                except Exception:
                    # If condition failed, assert explicitly that body map is still visible
                    assert body_map and body_map.is_displayed(), f"[{browser}] Body map not visible after hover on {key}."
        finally:
            driver.quit()

# ---- Test 5: Responsive sizes ----
def test_BodyMap_Responsive_Visibility():
    """
    Verify the body map and targets are visible across desktop/tablet/mobile sizes.
    """
    sizes = [(1280, 720), (768, 1024), (375, 667)]
    labels = ["desktop", "tablet", "mobile"]

    for browser in BROWSER_LIST:
        driver = get_driver(browser, headless=True)
        try:
            goto_home(driver)
            wait_bodymap_visible(driver)

            for (w, h), name in zip(sizes, labels):
                driver.set_window_size(w, h)
                # Wait for layout to settle instead of sleeping
                wait_layout_settled_after_resize(driver, w, h)

                body_map = find_body_map(driver)
                assert body_map and body_map.is_displayed(), f"[{browser}] Body map not visible on {name} size."

                targets = find_target_parts(driver)
                assert targets, f"[{browser}] No targets found on {name} size."

            # Restore to desktop at end of test (optional)
            driver.set_window_size(1280, 720)
            wait_layout_settled_after_resize(driver, 1280, 720)
        finally:
            driver.quit()
