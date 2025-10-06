"""
Author: Dien Mai
Role: Scrum Master 4
Purpose: End-to-end tests for dropdown functionality in the FAA tool.
         These tests simulate real user behavior in multiple browsers using Selenium.
Tests Implemented:
        1. Open dropdown, select first option, verify page remains stable
        2. Select up to three different options, verifying stability after each
"""

# ---- Imports Required ----
import os
import logging

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC

# (ActionChains not needed here)

# ---- Logging (pytest captures logger output) ----
logger = logging.getLogger("e2e.dropdown")

# ---- Variables / Constants ----
LOCAL_HOST = os.getenv("BASE_URL", "http://localhost:3000").rstrip("/")
DEFAULT_TIMEOUT = int(os.getenv("E2E_TIMEOUT", "10"))
BROWSER_LIST = ["chrome", "firefox", "edge"]

# Common selectors for locating dropdowns and their options
NATIVE_DROPDOWN_TAG = "select"
CUSTOM_DROPDOWN_ROOTS = [".dropdown", "[role='combobox']", "[data-testid='dropdown']"]
CUSTOM_OPTION_SELECTORS = [
    "[role='option']",
    ".dropdown-option",
    # fallback containers:
    "[role='listbox'] [role='option']",
    ".dropdown-menu .dropdown-item",
    ".menu .item",
    ".listbox li",
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
def wait_dom_ready(driver):
    """Wait until the document is fully loaded and the <body> is present."""
    WebDriverWait(driver, timeout=DEFAULT_TIMEOUT).until(
        lambda d: d.execute_script("return document.readyState") == "complete"
    )
    WebDriverWait(driver, timeout=DEFAULT_TIMEOUT).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "body"))
    )


def goto_home(driver):
    """Navigate to the app root and wait for the page to be fully loaded."""
    driver.get(LOCAL_HOST)
    wait_dom_ready(driver)


def find_dropdown(driver):
    """
    Try to detect a dropdown:
    - First, native <select>
    - Otherwise, a custom dropdown root element
    Returns a tuple: ("native"|"custom"|None, WebElement|None)
    """
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
    """
    Locate option elements for either a native or custom dropdown.
    Returns a list[WebElement].
    """
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


def wait_options_visible(driver, kind):
    """Explicit wait for dropdown options to be visible/rendered."""
    if kind == "native":
        # Native options always present under the select
        WebDriverWait(driver, DEFAULT_TIMEOUT).until(
            EC.presence_of_element_located((By.TAG_NAME, "option"))
        )
        return

    # For custom, wait until any known option selector is visible
    waited = False
    for sel in CUSTOM_OPTION_SELECTORS:
        try:
            WebDriverWait(driver, DEFAULT_TIMEOUT).until(
                EC.visibility_of_any_elements_located((By.CSS_SELECTOR, sel))
            )
            waited = True
            break
        except Exception:
            continue
    if not waited:
        # Last resort: visible listbox
        WebDriverWait(driver, DEFAULT_TIMEOUT).until(
            EC.visibility_of_any_elements_located((By.CSS_SELECTOR, "[role='listbox']"))
        )


def open_if_custom(driver, kind, dropdown):
    """
    Ensure the options are visible for custom dropdowns (click to open),
    and explicitly wait for them. No-op for native selects.
    """
    if kind != "native":
        EC.element_to_be_clickable(dropdown)(driver)
        dropdown.click()
        wait_options_visible(driver, kind)


def get_selected_text_native(dropdown):
    """Return the currently selected option text for a native <select>."""
    sel = Select(dropdown)
    return (sel.first_selected_option.text or "").strip()


def wait_selected_state(driver, kind, dropdown, target_text, target_value=None):
    """
    Wait until the dropdown reflects the selected option:
      - Native: first_selected_option text matches target_text (or value matches).
      - Custom: either an option has aria-selected="true" with matching text,
                or the root/trigger text reflects the chosen label,
                or a data-selected/value attribute equals target_value.
    """
    target_text = (target_text or "").strip()

    def _native_ok(d):
        try:
            sel = Select(dropdown)
            opt = sel.first_selected_option
            if opt is None:
                return False
            txt = (opt.text or "").strip()
            if target_value is not None:
                return (opt.get_attribute("value") == target_value) or (txt == target_text)
            return txt == target_text
        except Exception:
            return False

    def _custom_ok(d):
        try:
            # 1) Selected option aria state
            selected_opts = d.find_elements(By.CSS_SELECTOR, "[role='option'][aria-selected='true'], .dropdown-option[aria-selected='true']")
            for so in selected_opts:
                if (so.text or "").strip() == target_text:
                    return True

            # 2) Root/trigger text changed to label (common pattern)
            trigger_text = (dropdown.text or "").strip()
            if trigger_text and target_text and target_text in trigger_text:
                return True

            # 3) Attribute-based contract
            if target_value is not None:
                val = dropdown.get_attribute("value") or dropdown.get_attribute("data-selected")
                if val == target_value:
                    return True
        except Exception:
            return False
        return False

    if kind == "native":
        WebDriverWait(driver, DEFAULT_TIMEOUT).until(_native_ok)
    else:
        WebDriverWait(driver, DEFAULT_TIMEOUT).until(_custom_ok)


# ---- Test 1: Open dropdown, select first option, verify page remains stable ----
def test_Dropdown_Select_First_Option():
    """
    Open dropdown, select first option, and verify state reflects selection.
    """
    for browser in BROWSER_LIST:
        driver = get_driver(browser, headless=True)
        try:
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
            option_value = first.get_attribute("value")

            if kind == "native":
                sel = Select(dropdown)
                if option_value is not None:
                    sel.select_by_value(option_value)
                else:
                    sel.select_by_index(0)
            else:
                EC.element_to_be_clickable(first)(driver)
                first.click()

            # Explicit wait for selected state (no page_source reliance)
            wait_selected_state(driver, kind, dropdown, option_text, option_value)

            # Log selection (pytest captures this)
            logger.info(f"[{browser}] Selected option: {option_text or '<no text>'}")
        finally:
            driver.quit()


# ---- Test 2: Select up to three different options, verify stability after each ----
def test_Dropdown_Select_Multiple_Options():
    """
    Try selecting up to three different options, verifying dropdown state after each selection.
    """
    for browser in BROWSER_LIST:
        driver = get_driver(browser, headless=True)
        try:
            goto_home(driver)

            kind, dropdown = find_dropdown(driver)
            assert dropdown is not None, f"[{browser}] Dropdown not found."

            # For custom dropdowns, open once before reading options
            open_if_custom(driver, kind, dropdown)

            options = find_options(driver, kind or "")
            assert options, f"[{browser}] No options found in dropdown."

            limit = min(3, len(options))
            for i in range(limit):
                # If custom UIs close on selection, reopen and refresh list before each selection
                if kind != "native":
                    try:
                        if not options[i].is_displayed():
                            open_if_custom(driver, kind, dropdown)
                            options = find_options(driver, kind or "")
                    except Exception:
                        open_if_custom(driver, kind, dropdown)
                        options = find_options(driver, kind or "")

                opt = options[i]
                label = (opt.text or "").strip()
                val = opt.get_attribute("value")

                if kind == "native":
                    sel = Select(dropdown)
                    if val is not None:
                        sel.select_by_value(val)
                    else:
                        sel.select_by_index(i)
                else:
                    EC.element_to_be_clickable(opt)(driver)
                    opt.click()

                # Wait explicitly for the selected state to reflect the choice
                wait_selected_state(driver, kind, dropdown, label, val)

                # Pytest-captured log instead of print/page_source
                logger.info(f"[{browser}] Option {i+1} selected: {label or '<no text>'}")
        finally:
            driver.quit()
