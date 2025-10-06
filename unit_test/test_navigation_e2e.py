"""
Author: Dien Mai
Role: Scrum Master 4
Purpose: End-to-end tests for site navigation in the FAA tool. These tests simulate
         how a user moves around via mouse and keyboard in multiple browsers using Selenium.
Tests Implemented:
        1. Click a navigation element and verify URL change or in-page scroll
        2. Click multiple navigation elements in sequence and verify stability
        3. Keyboard navigation with Tab/Enter activates a visible control successfully
"""

# ---- Imports Required ----
import os

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# ---- Variables / Constants ----
LOCAL_HOST = os.getenv("BASE_URL", "http://localhost:3000").rstrip("/")
DEFAULT_TIMEOUT = int(os.getenv("E2E_TIMEOUT", "10"))
BROWSER_LIST = ["chrome", "firefox", "edge"]

# Heuristics for picking obvious nav items by text
COMMON_NAV_TEXT = ["home", "about", "guide", "medical", "certification", "help", "contact"]


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
def wait_dom_ready(driver):
    """Wait until the document is fully loaded and the <body> is present."""
    WebDriverWait(driver, timeout=DEFAULT_TIMEOUT).until(
        lambda d: d.execute_script("return document.readyState") == "complete"
    )
    WebDriverWait(driver, timeout=DEFAULT_TIMEOUT).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "body"))
    )


def wait_for_content(driver):
    """
    Wait for meaningful content:
      - #root OR <main>/<role='main'> OR a heading (h1/h2/h3),
      - fallback: non-empty body innerText.
    """
    wait_dom_ready(driver)
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
        WebDriverWait(driver, timeout=DEFAULT_TIMEOUT).until(
            lambda d: bool(
                d.execute_script(
                    "return document.body && document.body.innerText && document.body.innerText.trim().length"
                )
            )
        )


def content_present(driver) -> bool:
    """Non-blocking check mirroring wait_for_content criteria."""
    try:
        if driver.find_elements(By.CSS_SELECTOR, "#root"):
            return True
        if driver.find_elements(By.CSS_SELECTOR, "main, [role='main']"):
            return True
        if driver.find_elements(By.CSS_SELECTOR, "h1, h2, h3"):
            return True
        txt_len = driver.execute_script(
            "return (document.body && document.body.innerText) ? document.body.innerText.trim().length : 0;"
        )
        return bool(txt_len)
    except Exception:
        return False


def goto_home(driver):
    """Navigate to the app root and wait for the page to be fully loaded with content."""
    driver.get(LOCAL_HOST)
    wait_for_content(driver)


def find_nav_elements(driver):
    """
    Collect visible navigation-capable elements: <a> and <button>.
    Returns a list[WebElement].
    """
    candidates = []
    try:
        buttons = driver.find_elements(By.TAG_NAME, "button")
    except Exception:
        buttons = []
    try:
        links = driver.find_elements(By.TAG_NAME, "a")
    except Exception:
        links = []

    for el in buttons + links:
        try:
            if el.is_displayed():
                candidates.append(el)
        except Exception:
            continue
    return candidates


def pick_obvious_nav(nav_elements):
    """
    Prefer an element whose text matches common nav words; else return the first element.
    """
    for el in nav_elements:
        try:
            txt = (el.text or "").strip().lower()
            if any(w in txt for w in COMMON_NAV_TEXT):
                return el
        except Exception:
            continue
    return nav_elements[0] if nav_elements else None


def wait_url_change_or_scroll(driver, initial_url: str, initial_scroll: int):
    """
    Wait until either the URL changes OR the page scroll position increases.
    Used to replace arbitrary sleeps after navigation actions.
    """
    def _changed(d):
        url = d.current_url
        scroll = d.execute_script("return window.pageYOffset;") or 0
        return (url != initial_url) or (scroll > initial_scroll)

    WebDriverWait(driver, timeout=DEFAULT_TIMEOUT).until(_changed)
    # also ensure content has rendered
    wait_for_content(driver)


# ---- Test 1: Click a nav element and verify URL change or in-page scroll ----
def test_Navigation_Click_Changes_URL_Or_Scroll():
    """
    Click a navigation element and verify that either the URL changes
    or the page scrolls to a new section. Also verify page stability afterward.
    """
    for browser in BROWSER_LIST:
        driver = get_driver(browser, headless=True)
        try:
            goto_home(driver)

            nav_elements = find_nav_elements(driver)
            assert nav_elements, f"[{browser}] No navigation elements found."

            nav_el = pick_obvious_nav(nav_elements)
            assert nav_el is not None, f"[{browser}] Could not choose a navigation element."

            initial_url = driver.current_url
            initial_scroll = driver.execute_script("return window.pageYOffset;") or 0

            # Click and wait for a real state change
            EC.element_to_be_clickable(nav_el)(driver)
            nav_el.click()
            wait_url_change_or_scroll(driver, initial_url, initial_scroll)

            # Determine outcome (re-check values after wait)
            new_url = driver.current_url
            new_scroll = driver.execute_script("return window.pageYOffset;") or 0
            url_changed = (new_url != initial_url)
            page_scrolled = (new_scroll > initial_scroll)

            # One of these should be true for successful navigation
            assert url_changed or page_scrolled, f"[{browser}] Clicked nav but no URL change or scroll detected."

            # Stability check: element/state-based
            assert content_present(driver), f"[{browser}] Page shows no meaningful content after navigation."
        finally:
            driver.quit()


# ---- Test 2: Click first three nav elements and verify stability ----
def test_Navigation_Click_Multiple_Elements():
    """
    Click up to the first three visible navigation elements and verify the page remains stable.
    """
    for browser in BROWSER_LIST:
        driver = get_driver(browser, headless=True)
        try:
            goto_home(driver)

            nav_elements = find_nav_elements(driver)
            assert nav_elements, f"[{browser}] No navigation elements found."

            limit = min(3, len(nav_elements))
            for i in range(limit):
                el = nav_elements[i]
                label = (el.text or "").strip()
                initial_url = driver.current_url
                initial_scroll = driver.execute_script("return window.pageYOffset;") or 0

                EC.element_to_be_clickable(el)(driver)
                el.click()
                wait_url_change_or_scroll(driver, initial_url, initial_scroll)

                # Element/state-based stability check
                assert content_present(driver), f"[{browser}] Page broke after clicking nav element #{i+1}: {label or '<no text>'}"

                # Reset to home for next iteration to reduce state coupling
                goto_home(driver)
        finally:
            driver.quit()


# ---- Test 3: Keyboard navigation with Tab/Enter ----
def test_Navigation_Keyboard_Tab_Enter():
    """
    Use keyboard navigation (Tab to focus a control, Enter to activate)
    and verify that either the URL changes or the page scrolls.
    """
    for browser in BROWSER_LIST:
        driver = get_driver(browser, headless=True)
        try:
            goto_home(driver)

            nav_elements = find_nav_elements(driver)
            if not nav_elements:
                # If there are truly no nav controls, nothing to test here.
                continue

            body = driver.find_element(By.TAG_NAME, "body")

            # Step 1: Try to focus a link/button with a bounded number of Tabs.
            def _focus_reached(d):
                active = d.switch_to.active_element
                return active and (active.tag_name.lower() in ("a", "button"))

            # Send up to 8 TABs, checking after each send.
            for _ in range(8):
                if _focus_reached(driver):
                    break
                body.send_keys(Keys.TAB)
                WebDriverWait(driver, timeout=DEFAULT_TIMEOUT).until(
                    lambda d: d.switch_to.active_element is not None
                )

            assert _focus_reached(driver), f"[{browser}] Could not focus a link/button via keyboard."

            # Step 2: Activate with Enter and observe effect
            initial_url = driver.current_url
            initial_scroll = driver.execute_script("return window.pageYOffset;") or 0

            driver.switch_to.active_element.send_keys(Keys.ENTER)
            wait_url_change_or_scroll(driver, initial_url, initial_scroll)

            new_url = driver.current_url
            new_scroll = driver.execute_script("return window.pageYOffset;") or 0
            url_changed = (new_url != initial_url)
            page_scrolled = (new_scroll > initial_scroll)

            # At least one indicator of successful navigation should be true
            assert url_changed or page_scrolled or content_present(driver), f"[{browser}] Keyboard navigation produced no visible effect."
        finally:
            driver.quit()
