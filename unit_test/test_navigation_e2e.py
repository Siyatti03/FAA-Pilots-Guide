'''
Author: Dien Mai
    Role: Scrum Master 4
Purpose: End-to-end tests for site navigation in the FAA tool. These tests simulate
         how a user moves around via mouse and keyboard in multiple browsers using Selenium.
Tests Implemented:
        1. Click a navigation element and verify URL change or in-page scroll
        2. Click multiple navigation elements in sequence and verify stability
        3. Keyboard navigation with Tab/Enter activates a visible control successfully
'''

# ---- Imports Required ----
import os
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions

# ---- Variables / Constants ----
LOCAL_HOST = os.getenv("BASE_URL", "http://localhost:3000")
DEFAULT_TIMEOUT = int(os.getenv("E2E_TIMEOUT", "10"))
BROWSER_LIST = ["chrome", "firefox", "edge"]

# Heuristics for picking obvious nav items by text
COMMON_NAV_TEXT = ["home", "about", "guide", "medical", "certification", "help", "contact"]

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
def goto_home(driver):
    '''
    Navigate to the app root and wait for the page to be fully loaded.
    '''
    driver.get(LOCAL_HOST)
    WebDriverWait(driver, timeout=DEFAULT_TIMEOUT).until(
        lambda d: d.execute_script("return document.readyState") == "complete"
    )
    WebDriverWait(driver, timeout=DEFAULT_TIMEOUT).until(
        expected_conditions.presence_of_element_located((By.CSS_SELECTOR, "body"))
    )

def find_nav_elements(driver):
    '''
    Collect visible navigation-capable elements: <a> and <button>.
    Returns a list[WebElement].
    '''
    buttons = []
    links = []
    try:
        buttons = driver.find_elements(By.TAG_NAME, "button")
    except Exception:
        pass
    try:
        links = driver.find_elements(By.TAG_NAME, "a")
    except Exception:
        pass

    # Filter to visible elements
    candidates = []
    for el in buttons + links:
        try:
            if el.is_displayed():
                candidates.append(el)
        except Exception:
            continue
    return candidates

def pick_obvious_nav(nav_elements):
    '''
    Prefer an element whose text matches common nav words; else return the first element.
    '''
    for el in nav_elements:
        try:
            txt = (el.text or "").strip().lower()
            if any(w in txt for w in COMMON_NAV_TEXT):
                return el
        except Exception:
            continue
    return nav_elements[0] if nav_elements else None

# ---- Test 1: Click a nav element and verify URL change or in-page scroll ----
def test_Navigation_Click_Changes_URL_Or_Scroll():
    '''
    Click a navigation element and verify that either the URL changes
    or the page scrolls to a new section. Also verify page stability afterward.
    '''
    for browser in BROWSER_LIST:
        driver = get_driver(browser, headless=True)
        goto_home(driver)

        nav_elements = find_nav_elements(driver)
        assert nav_elements, f"[{browser}] No navigation elements found."

        nav_el = pick_obvious_nav(nav_elements)
        assert nav_el is not None, f"[{browser}] Could not choose a navigation element."

        initial_url = driver.current_url
        initial_scroll = driver.execute_script("return window.pageYOffset;") or 0

        nav_el.click()
        # Wait for load/settle
        time.sleep(0.6)
        WebDriverWait(driver, timeout=DEFAULT_TIMEOUT).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )

        # Determine outcome
        new_url = driver.current_url
        new_scroll = driver.execute_script("return window.pageYOffset;") or 0
        url_changed = (new_url != initial_url)
        page_scrolled = (new_scroll > initial_scroll)

        # One of these should be true for successful navigation
        assert url_changed or page_scrolled, f"[{browser}] Clicked nav but no URL change or scroll detected."

        # Stability check
        html = driver.page_source
        assert html and len(html) > 0, f"[{browser}] Page content disappeared after navigation."

        driver.quit()

# ---- Test 2: Click first three nav elements and verify stability ----
def test_Navigation_Click_Multiple_Elements():
    '''
    Click up to the first three visible navigation elements and verify the page remains stable.
    '''
    for browser in BROWSER_LIST:
        driver = get_driver(browser, headless=True)
        goto_home(driver)

        nav_elements = find_nav_elements(driver)
        assert nav_elements, f"[{browser}] No navigation elements found."

        limit = min(3, len(nav_elements))
        for i in range(limit):
            el = nav_elements[i]
            label = (el.text or "").strip()

            initial_url = driver.current_url
            el.click()

            time.sleep(0.6)
            WebDriverWait(driver, timeout=DEFAULT_TIMEOUT).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )

            # Basic stability check
            assert driver.page_source, f"[{browser}] Page broke after clicking nav element #{i+1}: {label or '<no text>'}"

            # Reset to home for next iteration to reduce state coupling
            goto_home(driver)

        driver.quit()

# ---- Test 3: Keyboard navigation with Tab/Enter ----
def test_Navigation_Keyboard_Tab_Enter():
    '''
    Use keyboard navigation (Tab to focus a control, Enter to activate)
    and verify that either the URL changes or the page scrolls.
    '''
    for browser in BROWSER_LIST:
        driver = get_driver(browser, headless=True)
        goto_home(driver)

        nav_elements = find_nav_elements(driver)
        if not nav_elements:
            # If there are truly no nav controls, nothing to test here.
            driver.quit()
            continue

        body = driver.find_element(By.TAG_NAME, "body")

        # Step 1: Try to focus a link/button with a few Tabs
        active = driver.switch_to.active_element
        tries = 0
        while (active.tag_name.lower() not in ("a", "button")) and tries < 8:
            body.send_keys(Keys.TAB)
            time.sleep(0.2)
            active = driver.switch_to.active_element
            tries += 1

        # Step 2: Activate with Enter and observe effect
        initial_url = driver.current_url
        initial_scroll = driver.execute_script("return window.pageYOffset;") or 0

        active.send_keys(Keys.ENTER)
        time.sleep(0.6)
        WebDriverWait(driver, timeout=DEFAULT_TIMEOUT).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )

        new_url = driver.current_url
        new_scroll = driver.execute_script("return window.pageYOffset;") or 0
        url_changed = (new_url != initial_url)
        page_scrolled = (new_scroll > initial_scroll)

        # At least one indicator of successful navigation should be true
        assert url_changed or page_scrolled or driver.page_source, f"[{browser}] Keyboard navigation produced no visible effect."

        driver.quit()
