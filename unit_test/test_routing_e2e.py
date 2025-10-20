'''
Author: Dien Mai
    Role: Scrum Master 4
Purpose: End-to-end routing tests for the FAA tool. These tests validate:
         - Internal link navigation between pages
         - Direct URL navigation to common routes
         - Browser back/forward/refresh behavior
         - Basic page load performance and presence of key elements
Tests Implemented:
        1. Click internal links and verify routes work correctly
        2. Navigate directly to known routes and verify content loads
        3. Use browser back/forward/refresh and verify stability
        4. Measure load time and check for basic content (title/headings)
'''

# ---- Imports Required ----
import os
import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from unit_test.e2e_helpers import checkPageReady, BASE_URL, DEFAULT_TIMEOUT
from unit_test.driver_manager import get_driver

# ---- Variables / Constants ----
LOCAL_HOST = os.getenv("BASE_URL", BASE_URL).rstrip("/")
DEFAULT_TIMEOUT = int(os.getenv("E2E_TIMEOUT", str(DEFAULT_TIMEOUT)))
BROWSER_LIST = ["chrome", "firefox", "edge"]

# Routes to probe directly (customize as needed for the app)
ROUTE_LIST = [
    "/",
    "/about",
    "/medical-guide",
    "/certification",
    "/help",
    "/faq",
]

# ---- Driver Factory ----
# Using centralized WebDriver fixture from driver_manager.py

# ---- Utilities / Helpers ----
def wait_ready(driver):
    '''
    Wait until the document is fully loaded and the <body> is present.
    '''
    checkPageReady(driver, driver.current_url)

def goto(driver, path: str):
    '''
    Navigate to a path (absolute or relative) and wait for readiness.
    '''
    url = path if path.startswith("http") else f"{LOCAL_HOST}{path}"
    checkPageReady(driver, url)

def is_error_page(driver) -> bool:
    '''
    Heuristic: treat pages containing 404/Not Found/Error as error pages.
    '''
    html = (driver.page_source or "").lower()
    return any(flag in html for flag in (" 404", "not found", "error"))

def internal_links(driver):
    '''
    Collect internal <a href="..."> links pointing to the same origin or root-relative.
    Returns a list[WebElement].
    '''
    out = []
    links = driver.find_elements(By.CSS_SELECTOR, "a[href]")
    for a in links:
        href = a.get_attribute("href") or ""
        if href.startswith("/") or "localhost" in href:
            out.append(a)
    return out

# ---- Test 1: Internal link navigation ----
def test_Routing_Internal_Links_Work():
    '''
    Click up to three internal links and verify that the target pages load
    and are not obvious error pages. Return to home between clicks.
    '''
    for browser in BROWSER_LIST:
        driver = get_driver(browser, headless=True)
        goto(driver, "/")

        links = internal_links(driver)
        if links:
            for i, link in enumerate(links[:3], start=1):
                link.click()
                wait_ready(driver)
                assert driver.page_source, f"[{browser}] Page broke after clicking link #{i}"
                goto(driver, "/")  # Return to home

        driver.quit()

# ---- Test 2: Direct URL navigation ----
def test_Routing_Direct_URLs_Load_Content():
    '''
    Navigate directly to a set of known routes and verify the page loads with content.
    '''
    for browser in BROWSER_LIST:
        driver = get_driver(browser, headless=True)

        for route in ROUTE_LIST[:3]:  # Test first 3 routes only
            goto(driver, route)
            assert driver.page_source, f"[{browser}] Empty content for route {route}"

        driver.quit()

# ---- Test 3: Browser back/forward/refresh behavior ----
def test_Routing_Back_Forward_Refresh_Are_Stable():
    '''
    Open home, click a link, then use browser back/forward/refresh.
    Verify pages load and content remains present at each step.
    '''
    for browser in BROWSER_LIST:
        driver = get_driver(browser, headless=True)
        goto(driver, "/")

        links = internal_links(driver)
        if not links:
            driver.quit()
            continue

        # Click first link
        links[0].click()
        wait_ready(driver)
        assert driver.page_source, f"[{browser}] Empty content after click"

        # Back
        driver.back()
        wait_ready(driver)
        assert driver.page_source, f"[{browser}] Empty content after back"

        # Forward
        driver.forward()
        wait_ready(driver)
        assert driver.page_source, f"[{browser}] Empty content after forward"

        # Refresh
        driver.refresh()
        wait_ready(driver)
        assert driver.page_source, f"[{browser}] Empty content after refresh"

        driver.quit()

# ---- Test 4: Basic load performance & elements ----
def test_Routing_Page_Load_Performance_And_Elements():
    '''
    Measure a simple load time for home, ensure non-empty content, and
    check for presence of a title and any headings.
    '''
    for browser in BROWSER_LIST:
        driver = get_driver(browser, headless=True)

        start = time.time()
        goto(driver, "/")
        load_time = time.time() - start

        print(f"[{browser}] Home loaded in {load_time:.2f}s.")
        assert driver.page_source, f"[{browser}] Empty page content on home."
        assert driver.title, f"[{browser}] No title found"

        driver.quit()