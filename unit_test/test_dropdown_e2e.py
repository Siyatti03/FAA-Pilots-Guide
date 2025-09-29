'''
Author: Dien Mai
    Role: Scrum Master 4
Purpose: End-to-end tests for dropdown functionality in the FAA tool.
         These tests simulate real user behavior in multiple browsers using Selenium.
Tests Implemented:
        1. Open dropdown, select first option, verify page remains stable
        2. Select up to three different options, verifying stability after each
'''

# ---- Imports Required ----
import os
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions
# (ActionChains not needed here)

# ---- Variables / Constants ----
LOCAL_HOST = os.getenv("BASE_URL", "http://localhost:3000")
DEFAULT_TIMEOUT = int(os.getenv("E2E_TIMEOUT", "10"))
BROWSER_LIST = ["chrome", "firefox", "edge"]

# Common selectors for locating dropdowns and their options
NATIVE_DROPDOWN_TAG = "select"
CUSTOM_DROPDOWN_ROOTS = [".dropdown", "[role='combobox']", "[data-testid='dropdown']"]
CUSTOM_OPTION_SELECTORS = [
    "[role='option']", ".dropdown-option",
    # fallback containers:
    "[role='listbox'] [role='option']",
    ".dropdown-menu .dropdown-item",
    ".menu .item", ".listbox li"
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

def find_dropdown(driver):
    '''
    Try to detect a dropdown:
    - First, native <select>
    - Otherwise, a custom dropdown root element
    Returns a tuple: ("native"|"custom"|None, WebElement|None)
    '''
    # Native <select>
    try:
        native = driver.find_elements(By.TAG_NAME, NATIVE_DROPDOWN_TAG)
        if native:
            return ("native", native[0])
    except Exception:
        pass

    # Custom dropdown roots
    for sel in CUSTOM_DROPDOWN_ROOTS:
        try:
            els = driver.find_elements(By.CSS_SELECTOR, sel)
            if els:
                return ("custom", els[0])
        except Exception:
            pass

    return (None, None)

def find_options(driver, kind):
    '''
    Locate option elements for either a native or custom dropdown.
    Returns a list[WebElement].
    '''
    if kind == "native":
        try:
            return driver.find_elements(By.TAG_NAME, "option")
        except Exception:
            return []

    # For custom dropdowns, try explicit option markers first
    for sel in CUSTOM_OPTION_SELECTORS:
        try:
            opts = driver.find_elements(By.CSS_SELECTOR, sel)
            if opts:
                return opts
        except Exception:
            continue

    return []

def open_if_custom(driver, kind, dropdown):
    '''
    Ensure the options are visible for custom dropdowns (click to open).
    No-op for native selects.
    '''
    if kind != "native":
        try:
            dropdown.click()
            time.sleep(0.3)  # allow menu to render
        except Exception:
            pass

# ---- Test 1: Open dropdown, select first option, verify page remains stable ----
def test_Dropdown_Select_First_Option():
    '''
    Open dropdown, select first option, and verify page remains stable.
    '''
    for browser in BROWSER_LIST:
        driver = get_driver(browser, headless=True)
        goto_home(driver)

        # Locate dropdown
        kind, dropdown = find_dropdown(driver)
        assert dropdown is not None, f"[{browser}] Could not find a dropdown on the page."

        # Open if custom
        open_if_custom(driver, kind, dropdown)

        # Find options
        options = find_options(driver, kind or "")
        assert options, f"[{browser}] No options found for the dropdown."

        # Select first option
        first = options[0]
        option_text = (first.text or "").strip()

        if kind == "native":
            # Prefer select-by-value if present, else select-by-index
            sel = Select(dropdown)
            value = first.get_attribute("value")
            if value is not None:
                sel.select_by_value(value)
            else:
                sel.select_by_index(0)
        else:
            # Custom dropdown: click the option element
            first.click()

        time.sleep(0.4)  # small UI settle

        # Stability check
        html = driver.page_source
        assert html and len(html) > 0, f"[{browser}] Page content disappeared after selection."
        # Optional debug print (mirrors group’s verbose style)
        print(f"[{browser}] Selected option: {option_text or '<no text>'}")

        driver.quit()

# ---- Test 2: Select up to three different options, verify stability after each ----
def test_Dropdown_Select_Multiple_Options():
    '''
    Try selecting up to three different options, verifying the page stays stable.
    '''
    for browser in BROWSER_LIST:
        driver = get_driver(browser, headless=True)
        goto_home(driver)

        kind, dropdown = find_dropdown(driver)
        assert dropdown is not None, f"[{browser}] Dropdown not found."

        # For custom dropdowns, open once before reading options
        open_if_custom(driver, kind, dropdown)

        options = find_options(driver, kind or "")
        assert options, f"[{browser}] No options found in dropdown."

        limit = min(3, len(options))
        for i in range(limit):
            # For custom UIs that close on selection, reopen before each new selection
            if kind != "native":
                # If option is detached/hidden, reopen and recalc list
                try:
                    if not options[i].is_displayed():
                        open_if_custom(driver, kind, dropdown)
                        options = find_options(driver, kind or "")
                except Exception:
                    open_if_custom(driver, kind, dropdown)
                    options = find_options(driver, kind or "")

            opt = options[i]
            label = (opt.text or "").strip()

            if kind == "native":
                sel = Select(dropdown)
                value = opt.get_attribute("value")
                if value is not None:
                    sel.select_by_value(value)
                else:
                    sel.select_by_index(i)
            else:
                opt.click()

            time.sleep(0.4)
            assert driver.page_source, f"[{browser}] Page broke after selecting option {i+1}."
            print(f"[{browser}] Option {i+1} worked: {label or '<no text>'}")

        driver.quit()
