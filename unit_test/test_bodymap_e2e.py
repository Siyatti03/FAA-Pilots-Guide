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

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys  # kept for parity; not required in all tests
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver import ActionChains

# ---- Variables / Constants ----
LOCAL_HOST = os.getenv("BASE_URL", "http://localhost:3000")
DEFAULT_TIMEOUT = int(os.getenv("E2E_TIMEOUT", "10"))
BROWSER_LIST = ["chrome", "firefox", "edge"]

# Target labels we expect to find on the body map
TARGET_PARTS = {"head", "upper body", "lower body"}

# Common selectors for locating the body map and info elements
BODY_MAP_SELECTORS = [".body-map", "#body-map", "[data-map='body']", "svg"]
INFO_SELECTORS = [".info", ".details", ".description", ".popup", ".tooltip", "[role='dialog']"]

# ---- Download the necessary drivers / Driver Factory ----
def get_driver(browser, headless=True):
    '''
    Return a Selenium WebDriver for the given browser.
    rtype: webdriver
    browser - The browser being used ("chrome", "firefox", "edge")
    headless - If True, run without a visible UI (useful for CI)
    '''
    options = None

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
        # window-size in Firefox is set on driver, not via argument consistently
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
    '''
    Navigate to the app root and wait for the page to be fully loaded.
    '''
    driver.get(LOCAL_HOST)
    WebDriverWait(driver, timeout=DEFAULT_TIMEOUT).until(
        lambda d: d.execute_script("return document.readyState") == "complete"
    )

def find_body_map(driver):
    '''
    Try multiple selectors to locate the body map root element (svg or container).
    Returns the first matching element or None.
    '''
    for sel in BODY_MAP_SELECTORS:
        try:
            elements = driver.find_elements(By.CSS_SELECTOR, sel)
            if elements:
                # Ensure it is present in DOM
                return elements[0]
        except Exception:
            pass
    return None

def extract_label(el):
    '''
    Extract a human-readable label for a body part from attributes or text.
    '''
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
    '''
    Find elements on the page that correspond to known body target parts.
    Returns a dict: {normalized_label: element}
    '''
    found = {}

    # Broad search over potential body map children; restrict to displayed
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

def get_visible_info_blocks(driver):
    '''
    Try standard info selectors first; if not found, fall back to visible text blocks.
    '''
    # Wait briefly for any UI updates (e.g., animations/popups)
    WebDriverWait(driver, timeout=DEFAULT_TIMEOUT).until(
        expected_conditions.presence_of_all_elements_located((By.CSS_SELECTOR, "body"))
    )

    results = []
    for sel in INFO_SELECTORS:
        try:
            results.extend(driver.find_elements(By.CSS_SELECTOR, sel))
        except Exception:
            pass

    # If none matched, fallback: visible blocks with enough text content to be "info-like"
    if not results:
        try:
            blocks = driver.find_elements(By.CSS_SELECTOR, "div, p, span")
            results = [b for b in blocks if b.is_displayed() and len(normalize_text(b.text)) > 10]
        except Exception:
            results = []

    return results

# ---- Test 1: Presence and discoverability ----
def test_BodyMap_Presence_And_Targets():
    '''
    Ensure the body map is present and that we can discover the known target areas.
    '''
    for browser in BROWSER_LIST:
        driver = get_driver(browser, headless=True)
        goto_home(driver)

        # Wait for something that implies the app has rendered
        WebDriverWait(driver, timeout=DEFAULT_TIMEOUT).until(
            expected_conditions.presence_of_element_located((By.CSS_SELECTOR, "body"))
        )

        body_map = find_body_map(driver)
        assert body_map is not None, f"[{browser}] Body map not found using known selectors."

        targets = find_target_parts(driver)
        assert targets, f"[{browser}] No body map target regions found."
        assert any(k in targets for k in TARGET_PARTS), f"[{browser}] Expected target labels not discovered."

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

        # Click the first available known target in a preferred order
        for key in ("head", "upper body", "lower body"):
            if key in targets:
                el = targets[key]
                label = extract_label(el) or key
                # Click
                el.click()
                # Allow UI to update (alternative: wait on specific popup root)
                time.sleep(0.75)
                break

        info_blocks = get_visible_info_blocks(driver)
        assert info_blocks, f"[{browser}] No info UI found after clicking a target."

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

        order = [k for k in ("head", "upper body", "lower body") if k in targets]
        assert order, f"[{browser}] No matching labeled targets to click."

        for idx, key in enumerate(order, start=1):
            el = targets[key]
            label = extract_label(el) or key
            el.click()
            time.sleep(0.5)

            # Simple stability check: page source still available and non-empty
            html = driver.page_source
            assert html and len(html) > 0, f"[{browser}] Page became empty after clicking {key} (#{idx})."

        driver.quit()

# ---- Test 4: Hover stability ----
def test_BodyMap_Hover_Does_Not_Break_UI():
    '''
    Hover over up to two targets and verify that the UI remains stable.
    '''
    for browser in BROWSER_LIST:
        driver = get_driver(browser, headless=True)
        goto_home(driver)

        targets = find_target_parts(driver)
        keys = [k for k in ("head", "upper body", "lower body") if k in targets][:2]
        assert keys, f"[{browser}] No targets available to hover."

        actions = ActionChains(driver)
        for key in keys:
            el = targets[key]
            actions.move_to_element(el).perform()
            time.sleep(0.5)

            html = driver.page_source
            assert html and len(html) > 0, f"[{browser}] Page broke after hover on {key}."

        driver.quit()

# ---- Test 5: Responsive sizes ----
def test_BodyMap_Responsive_Visibility():
    '''
    Verify the body map and targets are visible across desktop/tablet/mobile sizes.
    '''
    sizes = [(1280, 720), (768, 1024), (375, 667)]
    labels = ["desktop", "tablet", "mobile"]

    for browser in BROWSER_LIST:
        driver = get_driver(browser, headless=True)
        goto_home(driver)

        for (w, h), name in zip(sizes, labels):
            driver.set_window_size(w, h)
            time.sleep(0.75)  # allow layout to settle

            body_map = find_body_map(driver)
            assert body_map and body_map.is_displayed(), f"[{browser}] Body map not visible on {name} size."

            targets = find_target_parts(driver)
            assert targets, f"[{browser}] No targets found on {name} size."

        # Restore to desktop at end of test (optional)
        driver.set_window_size(1280, 720)
        driver.quit()
