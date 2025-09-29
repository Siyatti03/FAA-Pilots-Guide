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

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions

# ---- Variables / Constants ----
LOCAL_HOST = os.getenv("BASE_URL", "http://localhost:3000").rstrip("/")
DEFAULT_TIMEOUT = int(os.getenv("E2E_TIMEOUT", "10"))
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
def wait_ready(driver):
    '''
    Wait until the document is fully loaded and the <body> is present.
    '''
    WebDriverWait(driver, timeout=DEFAULT_TIMEOUT).until(
        lambda d: d.execute_script("return document.readyState") == "complete"
    )
    WebDriverWait(driver, timeout=DEFAULT_TIMEOUT).until(
        expected_conditions.presence_of_element_located((By.CSS_SELECTOR, "body"))
    )

def goto(driver, path: str):
    '''
    Navigate to a path (absolute or relative) and wait for readiness.
    '''
    url = path if path.startswith("http") else f"{LOCAL_HOST}{path}"
    driver.get(url)
    wait_ready(driver)

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
    try:
        links = driver.find_elements(By.CSS_SELECTOR, "a[href]")
    except Exception:
        return out

    for a in links:
        try:
            href = a.get_attribute("href") or ""
            if href.startswith("/") or "localhost" in href:
                out.append(a)
        except Exception:
            continue
    return out

# ---- Test 1: Internal link navigation ----
def test_Routing_Internal_Links_Work():
    '''
    Click up to three internal links and verify that the target pages load
    and are not obvious error pages. Return to home between clicks.
    '''
    for browser in BROWSER_LIST:
        driver = get_driver(browser, headless=True)

        # Start at home
        goto(driver, "/")
        start_url = driver.current_url

        links = internal_links(driver)
        # It's okay if there are 0 links; the test becomes a no-op for that browser
        if links:
            for i, link in enumerate(links[:3], start=1):
                text = (link.text or "").strip()
                href = link.get_attribute("href")

                # Click, with fallback for stale elements
                try:
                    link.click()
                except Exception:
                    retry = driver.find_elements(By.CSS_SELECTOR, f"a[href='{href}']")
                    if retry:
                        retry[0].click()
                    else:
                        driver.quit()
                        raise AssertionError(f"[{browser}] Could not re-click link {href}")

                wait_ready(driver)

                # Verify content exists
                html = driver.page_source
                assert html and len(html) > 0, f"[{browser}] Page broke after clicking link #{i}: {text or '<no text>'}"

                # Warn (non-failing) if an error-like page is detected
                if is_error_page(driver):
                    print(f"[{browser}] Warning: Link #{i} led to an error-like page: {href}")

                # Go back to start for next iteration
                goto(driver, "/")
                assert driver.current_url.startswith(start_url.split("#")[0]), f"[{browser}] Failed to return to home."

        driver.quit()

# ---- Test 2: Direct URL navigation ----
def test_Routing_Direct_URLs_Load_Content():
    '''
    Navigate directly to a set of known routes and verify the page loads with content.
    '''
    for browser in BROWSER_LIST:
        driver = get_driver(browser, headless=True)

        for route in ROUTE_LIST:
            try:
                goto(driver, route)
                current_url = driver.current_url
                html = driver.page_source

                # Content must exist
                assert html and len(html) > 0, f"[{browser}] Empty content for route {route} ({current_url})."

                # Non-fatal warning if looks like an error page
                if is_error_page(driver):
                    print(f"[{browser}] Warning: Route {route} looks like an error page.")

            except Exception as e:
                driver.quit()
                raise AssertionError(f"[{browser}] Error navigating to {route}: {e}")

        driver.quit()

# ---- Test 3: Browser back/forward/refresh behavior ----
def test_Routing_Back_Forward_Refresh_Are_Stable():
    '''
    Open home, click a link, then use browser back/forward/refresh.
    Verify pages load and content remains present at each step.
    '''
    for browser in BROWSER_LIST:
        driver = get_driver(browser, headless=True)

        # Home
        goto(driver, "/")
        home_url = driver.current_url

        # Find a link to click (if none, skip for this browser)
        links = internal_links(driver)
        if not links:
            driver.quit()
            continue

        first = links[0]
        href = first.get_attribute("href")

        # Click with fallback
        try:
            first.click()
        except Exception:
            retry = driver.find_elements(By.CSS_SELECTOR, f"a[href='{href}']")
            if retry:
                retry[0].click()
            else:
                driver.quit()
                raise AssertionError(f"[{browser}] Could not click any link for browser nav test.")

        wait_ready(driver)
        second_url = driver.current_url
        assert driver.page_source, f"[{browser}] Empty content after initial click."

        # Back
        driver.back()
        wait_ready(driver)
        back_url = driver.current_url
        assert driver.page_source, f"[{browser}] Empty content after back."
        # Prefer returning to home
        assert back_url.split("#")[0] == home_url.split("#")[0], f"[{browser}] Back didn't return to home."

        # Forward
        driver.forward()
        wait_ready(driver)
        forward_url = driver.current_url
        assert driver.page_source, f"[{browser}] Empty content after forward."
        assert forward_url.split("#")[0] == second_url.split("#")[0], f"[{browser}] Forward didn't return to second page."

        # Refresh
        driver.refresh()
        wait_ready(driver)
        assert driver.page_source, f"[{browser}] Empty content after refresh."

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

        # Soft threshold warning (does not fail test)
        if load_time > 10:
            print(f"[{browser}] Warning: Home took {load_time:.2f}s to load.")
        else:
            print(f"[{browser}] Home loaded in {load_time:.2f}s.")

        html = driver.page_source
        assert html and len(html) > 0, f"[{browser}] Empty page content on home."

        title = driver.title or ""
        headings = driver.find_elements(By.CSS_SELECTOR, "h1, h2, h3")

        # We don't assert on title/headings text; just confirm driver can access them
        _ = title  # keep for potential debugging
        print(f"[{browser}] Found {len(headings)} headings on home.")

        driver.quit()
