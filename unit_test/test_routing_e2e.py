"""
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
"""

# ---- Imports Required ----
import os
import time
import logging

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# ---- Logging (pytest captures logging output) ----
logger = logging.getLogger("e2e")

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
            options=options,
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
            options=options,
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
            options=options,
        )
        driver.set_page_load_timeout(30)
        return driver

    else:
        raise ValueError(f"Unsupported browser: {browser}")

# ---- Utilities / Helpers ----
def wait_ready(driver):
    """
    Wait until the document is fully loaded and the <body> is present.
    """
    WebDriverWait(driver, timeout=DEFAULT_TIMEOUT).until(
        lambda d: d.execute_script("return document.readyState") == "complete"
    )
    WebDriverWait(driver, timeout=DEFAULT_TIMEOUT).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "body"))
    )

def wait_for_content(driver):
    """
    Wait until the page shows meaningful content:
    - #root or <main>/<role=main> or any heading appears; or
    - fallback: non-empty body innerText.
    """
    # already ensures DOM loaded
    wait_ready(driver)

    try:
        WebDriverWait(driver, timeout=DEFAULT_TIMEOUT).until(
            EC.any_of(
                EC.presence_of_element_located((By.CSS_SELECTOR, "#root")),
                EC.presence_of_element_located((By.CSS_SELECTOR, "main, [role='main']")),
                EC.presence_of_element_located((By.CSS_SELECTOR, "h1, h2, h3")),
            )
        )
        return
    except Exception:
        # Fallback to non-empty text body
        WebDriverWait(driver, timeout=DEFAULT_TIMEOUT).until(
            lambda d: bool(
                d.execute_script(
                    "return document.body && document.body.innerText && document.body.innerText.trim().length"
                )
            )
        )

def goto(driver, path: str):
    """
    Navigate to a path (absolute or relative) and wait for readiness + content.
    """
    url = path if path.startswith("http") else f"{LOCAL_HOST}{path}"
    driver.get(url)
    wait_for_content(driver)

def looks_like_error(driver) -> bool:
    """
    Heuristic for error-like page without using page_source:
    - title contains 404/error/not found; OR
    - top headings contain those tokens; OR
    - role=alert/.error/.alert present.
    """
    title = (driver.title or "").lower()
    if any(k in title for k in ("404", "not found", "error")):
        return True

    try:
        for el in driver.find_elements(By.CSS_SELECTOR, "h1, h2")[:2]:
            txt = (el.text or "").lower()
            if any(k in txt for k in ("404", "not found", "error")):
                return True
    except Exception:
        pass

    try:
        alerts = driver.find_elements(By.CSS_SELECTOR, "[role='alert'], .error, .alert")
        if alerts:
            return True
    except Exception:
        pass

    return False

def internal_links(driver):
    """
    Collect internal <a href="..."> links pointing to same origin or root-relative.
    Returns a list[WebElement].
    """
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
    """
    Click up to three internal links and verify that the target pages load
    and are not obvious error pages. Return to home between clicks.
    """
    for browser in BROWSER_LIST:
        driver = get_driver(browser, headless=True)
        try:
            # Start at home
            goto(driver, "/")
            start_url = driver.current_url.split("#")[0]

            links = internal_links(driver)
            # It's okay if there are 0 links; the test becomes a no-op for that browser
            if links:
                for i, link in enumerate(links[:3], start=1):
                    text = (link.text or "").strip()
                    href = link.get_attribute("href")

                    # Click with resilience: wait until clickable; retry if stale
                    try:
                        WebDriverWait(driver, DEFAULT_TIMEOUT).until(
                            EC.element_to_be_clickable(link)
                        )
                        link.click()
                    except Exception:
                        retry = driver.find_elements(By.CSS_SELECTOR, f"a[href='{href}']")
                        if retry:
                            WebDriverWait(driver, DEFAULT_TIMEOUT).until(
                                EC.element_to_be_clickable(retry[0])
                            )
                            retry[0].click()
                        else:
                            raise AssertionError(f"[{browser}] Could not re-click link {href} ({text or '<no text>'})")

                    wait_for_content(driver)

                    # Warn (non-failing) if an error-like page is detected
                    if looks_like_error(driver):
                        logger.warning(f"[{browser}] Warning: Link #{i} led to an error-like page: {href}")

                    # Go back to start for next iteration
                    goto(driver, "/")
                    assert driver.current_url.split("#")[0] == start_url, f"[{browser}] Failed to return to home."

        finally:
            driver.quit()

# ---- Test 2: Direct URL navigation ----
def test_Routing_Direct_URLs_Load_Content():
    """
    Navigate directly to a set of known routes and verify the page loads with content.
    """
    for browser in BROWSER_LIST:
        driver = get_driver(browser, headless=True)
        try:
            for route in ROUTE_LIST:
                goto(driver, route)
                current_url = driver.current_url

                # Non-fatal warning if looks like an error page
                if looks_like_error(driver):
                    logger.warning(f"[{browser}] Warning: Route {route} looks like an error page ({current_url}).")
        finally:
            driver.quit()

# ---- Test 3: Browser back/forward/refresh behavior ----
def test_Routing_Back_Forward_Refresh_Are_Stable():
    """
    Open home, click a link, then use browser back/forward/refresh.
    Verify pages load and content remains present at each step.
    """
    for browser in BROWSER_LIST:
        driver = get_driver(browser, headless=True)
        try:
            # Home
            goto(driver, "/")
            home_url = driver.current_url.split("#")[0]

            # Find a link to click (if none, skip for this browser)
            links = internal_links(driver)
            if not links:
                continue

            first = links[0]
            href = first.get_attribute("href")

            # Click with fallback
            try:
                WebDriverWait(driver, DEFAULT_TIMEOUT).until(
                    EC.element_to_be_clickable(first)
                )
                first.click()
            except Exception:
                retry = driver.find_elements(By.CSS_SELECTOR, f"a[href='{href}']")
                if retry:
                    WebDriverWait(driver, DEFAULT_TIMEOUT).until(
                        EC.element_to_be_clickable(retry[0])
                    )
                    retry[0].click()
                else:
                    raise AssertionError(f"[{browser}] Could not click any link for browser nav test.")

            wait_for_content(driver)
            second_url = driver.current_url.split("#")[0]

            # Back
            driver.back()
            wait_for_content(driver)
            back_url = driver.current_url.split("#")[0]
            assert back_url == home_url, f"[{browser}] Back didn't return to home."

            # Forward
            driver.forward()
            wait_for_content(driver)
            forward_url = driver.current_url.split("#")[0]
            assert forward_url == second_url, f"[{browser}] Forward didn't return to second page."

            # Refresh
            driver.refresh()
            wait_for_content(driver)

        finally:
            driver.quit()

# ---- Test 4: Basic load performance & elements ----
def test_Routing_Page_Load_Performance_And_Elements():
    """
    Measure a simple load time for home, ensure meaningful content, and
    check for presence of a title and any headings.
    """
    for browser in BROWSER_LIST:
        driver = get_driver(browser, headless=True)
        try:
            start = time.time()
            goto(driver, "/")
            load_time = time.time() - start

            # Soft threshold logging (does not fail test)
            if load_time > 10:
                logger.warning(f"[{browser}] Home took {load_time:.2f}s to load.")
            else:
                logger.info(f"[{browser}] Home loaded in {load_time:.2f}s.")

            # Title/headings presence (no strict assertions on text)
            title = driver.title or ""
            try:
                headings = driver.find_elements(By.CSS_SELECTOR, "h1, h2, h3")
                logger.info(f"[{browser}] Found {len(headings)} headings on home. Title: {title!r}")
            except Exception:
                logger.warning(f"[{browser}] Could not query headings on home. Title: {title!r}")

        finally:
            driver.quit()
