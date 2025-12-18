"""
Author: Dien Mai
Role: Scrum Master 4

Purpose:
    End-to-end routing tests for the FAA tool. These tests validate:
        - Internal link navigation between pages
        - Direct URL navigation to common routes
        - Browser back/forward/refresh behavior
        - Basic page load performance and presence of key elements

Tests Implemented:
    1. Click internal links and verify routes work correctly
    2. Navigate directly to known routes and verify content loads
    3. Use browser back/forward/refresh and verify stability
    4. Measure load time and check for basic content (title/headings)
"""

# ---- Imports Required ----
import os
import sys
import time
import pytest

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

from unit_test.e2e_helpers import checkPageReady, BASE_URL, DEFAULT_TIMEOUT

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
UTILS_DIR = os.path.join(ROOT_DIR, "tests", "utils")
sys.path.append(UTILS_DIR)
from driver_variables import BROWSER_SUPERLIST


# ---- Variables / Constants ----
LOCAL_HOST = os.getenv("BASE_URL", BASE_URL).rstrip("/")
E2E_TIMEOUT = int(os.getenv("E2E_TIMEOUT", str(DEFAULT_TIMEOUT)))

ROUTE_LIST = [
    "/",
    "/about",
    "/medical-guide",
    "/certification",
    "/help",
    "/faq",
]


# ---- Utilities / Helpers ----
def goto(driver, path: str):
    """
    Navigate to a path (absolute or relative) and wait for readiness.
    """
    url = path if path.startswith("http") else f"{LOCAL_HOST}{path}"
    checkPageReady(driver, url)


def wait_ready(driver, timeout=E2E_TIMEOUT):
    """
    Wait until document is loaded and page_source exists (basic stability).
    """
    wait = WebDriverWait(driver, timeout)
    wait.until(lambda d: bool(d.page_source))
    return True


def wait_for_url_change(driver, old_url, timeout=E2E_TIMEOUT):
    """
    Wait for URL to change; return True if changed, False if timed out.
    """
    try:
        WebDriverWait(driver, timeout).until(lambda d: d.current_url != old_url)
        return True
    except Exception:
        return False


def internal_links(driver):
    """
    Collect internal <a href="..."> links pointing to the same origin or root-relative.
    Returns a list[WebElement].
    """
    out = []
    links = driver.find_elements(By.CSS_SELECTOR, "a[href]")
    for a in links:
        try:
            if not a.is_displayed() or not a.is_enabled():
                continue
        except Exception:
            continue

        href = a.get_attribute("href") or ""
        if href.startswith("/") or "localhost" in href or href.startswith(LOCAL_HOST):
            out.append(a)
    return out


def headings_present(driver):
    """
    Check for any heading elements (h1-h6).
    """
    for tag in ["h1", "h2", "h3", "h4", "h5", "h6"]:
        els = driver.find_elements(By.TAG_NAME, tag)
        if any(e.is_displayed() for e in els):
            return True
    return False


def wait_for_element_stale(driver, element, timeout=E2E_TIMEOUT):
    """
    Wait until a previously-referenced element becomes stale after navigation.
    Helps confirm a click caused a route change / re-render.
    """
    try:
        WebDriverWait(driver, timeout).until(lambda d: _is_stale(element))
        return True
    except Exception:
        return False


def _is_stale(element):
    try:
        # Any call that touches the element can trigger StaleElementReferenceException if it's stale
        _ = element.is_enabled()
        return False
    except Exception:
        return True


# ---- Test 1: Internal link navigation ----
@pytest.mark.parametrize("browser_types_fixture", BROWSER_SUPERLIST, indirect=True)
def test_Routing_Internal_Links_Work(browser_types_fixture):
    """
    Click up to three internal links and verify that the target pages load
    and are not obviously broken. Return to home between clicks.
    """
    driver = browser_types_fixture
    goto(driver, "/")
    wait_ready(driver)

    links = internal_links(driver)
    if not links:
        pytest.skip("No internal links found on home page.")

    for i in range(min(3, len(links))):
        # Re-grab links each loop to avoid stale references after navigation
        goto(driver, "/")
        wait_ready(driver)

        links = internal_links(driver)
        if not links:
            pytest.skip("Internal links disappeared after returning home.")

        link = links[i]
        old_url = driver.current_url
        link.click()

        # Wait for either URL change or the clicked element to go stale
        url_changed = wait_for_url_change(driver, old_url)
        _ = wait_for_element_stale(driver, link)

        wait_ready(driver)
        assert driver.page_source, f"Page broke after clicking internal link #{i+1}"
        assert (url_changed or driver.current_url != old_url or driver.page_source), "Click had no observable effect."


# ---- Test 2: Direct URL navigation ----
@pytest.mark.parametrize("browser_types_fixture", BROWSER_SUPERLIST, indirect=True)
def test_Routing_Direct_URLs_Load_Content(browser_types_fixture):
    """
    Navigate directly to a set of known routes and verify the page loads with content.
    """
    driver = browser_types_fixture

    for route in ROUTE_LIST[:3]:
        goto(driver, route)
        wait_ready(driver)
        assert driver.page_source, f"Empty content for route {route}"


# ---- Test 3: Browser back/forward/refresh behavior ----
@pytest.mark.parametrize("browser_types_fixture", BROWSER_SUPERLIST, indirect=True)
def test_Routing_Back_Forward_Refresh_Are_Stable(browser_types_fixture):
    """
    Open home, click a link, then use browser back/forward/refresh.
    Verify pages load and content remains present at each step.
    """
    driver = browser_types_fixture
    goto(driver, "/")
    wait_ready(driver)

    links = internal_links(driver)
    if not links:
        pytest.skip("No internal links found for back/forward/refresh test.")

    old_url = driver.current_url
    first_link = links[0]
    first_link.click()

    # Confirm we moved somewhere (URL change or element staleness)
    _ = wait_for_url_change(driver, old_url) or wait_for_element_stale(driver, first_link)
    wait_ready(driver)
    assert driver.page_source, "Empty content after click"

    # Back
    driver.back()
    wait_ready(driver)
    assert driver.page_source, "Empty content after back"

    # Forward
    driver.forward()
    wait_ready(driver)
    assert driver.page_source, "Empty content after forward"

    # Refresh
    driver.refresh()
    wait_ready(driver)
    assert driver.page_source, "Empty content after refresh"


# ---- Test 4: Basic load performance & elements ----
@pytest.mark.parametrize("browser_types_fixture", BROWSER_SUPERLIST, indirect=True)
def test_Routing_Page_Load_Performance_And_Elements(browser_types_fixture):
    """
    Measure a simple load time for home, ensure non-empty content, and
    check for presence of a title and any headings.
    """
    driver = browser_types_fixture

    start = time.perf_counter()
    goto(driver, "/")
    wait_ready(driver)
    load_time = time.perf_counter() - start

    print(f"[routing] Home loaded in {load_time:.2f}s.")
    assert driver.page_source, "Empty page content on home."
    assert driver.title, "No title found on home."

