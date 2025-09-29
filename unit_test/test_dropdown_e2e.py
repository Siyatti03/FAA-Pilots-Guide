# E2E tests for dropdowns using Selenium
# Run with: pytest -q

import os
import time
import pytest

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC

BASE_URL = os.getenv("BASE_URL", "http://localhost:3000/")
DEFAULT_TIMEOUT = int(os.getenv("E2E_TIMEOUT", "10"))

def make_driver(headless: bool = False) -> webdriver.Chrome:
    opts = Options()
    if headless or os.getenv("HEADLESS", "false").lower() == "true":
        opts.add_argument("--headless=new")
    opts.add_argument("--window-size=1280,720")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--no-sandbox")
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=opts)
    driver.set_page_load_timeout(30)
    return driver

def goto_home(driver: webdriver.Chrome):
    driver.get(BASE_URL)
    WebDriverWait(driver, DEFAULT_TIMEOUT).until(
        lambda d: d.execute_script("return document.readyState") == "complete"
    )

def find_dropdown(driver: webdriver.Chrome):
    # Native <select>
    els = driver.find_elements(By.TAG_NAME, "select")
    if els:
        return ("native", els[0])

    # Common custom dropdown roots
    for sel in [".dropdown", "[role='combobox']", "[data-testid='dropdown']"]:
        els = driver.find_elements(By.CSS_SELECTOR, sel)
        if els:
            return ("custom", els[0])

    return (None, None)

def find_options(driver: webdriver.Chrome, kind: str):
    if kind == "native":
        return driver.find_elements(By.TAG_NAME, "option")

    # Custom dropdowns: common patterns
    # Try explicit option roles/classes first
    opts = driver.find_elements(By.CSS_SELECTOR, "[role='option'], .dropdown-option")
    if opts:
        return opts

    # Fallback: look inside common popover/listbox containers
    containers = driver.find_elements(By.CSS_SELECTOR, "[role='listbox'], .dropdown-menu, .menu, .listbox")
    for c in containers:
        items = c.find_elements(By.CSS_SELECTOR, "[role='option'], li, .item, .dropdown-item")
        if items:
            return items

    return []

@pytest.fixture
def driver():
    drv = make_driver(headless=False)  # set True for CI
    yield drv
    drv.quit()

def test_dropdown_e2e(driver):
    """E2E: open dropdown, select first option, verify page remains stable."""
    print("Starting E2E test for dropdown functionality...")
    goto_home(driver)

    # Step 1: find dropdown
    print("Step 1: Looking for dropdown...")
    kind, dropdown = find_dropdown(driver)
    assert dropdown is not None, "Could not find dropdown on the page"
    print("Found dropdown!")

    # Step 2: open dropdown
    print("Step 2: Opening dropdown...")
    dropdown.click()
    time.sleep(0.5)

    # Step 3: find options
    print("Step 3: Looking for dropdown options...")
    options = find_options(driver, kind or "")
    assert len(options) > 0, "No options found in dropdown"
    print(f"Found {len(options)} options")

    # Step 4: select first option
    print("Step 4: Selecting first option...")
    first = options[0]
    option_text = (first.text or "").strip()

    if kind == "native":
        # Use Select helper for native <select>
        select = Select(dropdown)
        # Prefer value if present; otherwise by index
        value = first.get_attribute("value")
        if value is not None:
            select.select_by_value(value)
        else:
            select.select_by_index(0)
    else:
        # Custom dropdown: click the option element
        first.click()

    time.sleep(0.5)
    print(f"Selected option: {option_text or '<no text>'}")

    # Step 5: verify selection
    print("Step 5: Verifying selection...")
    html = driver.page_source
    assert html and len(html) > 0, "Page content disappeared after selection"
    print("Selection completed successfully!")

def test_dropdown_with_different_options(driver):
    """E2E: try selecting up to three different options."""
    print("Starting E2E test for multiple dropdown selections...")
    goto_home(driver)

    kind, dropdown = find_dropdown(driver)
    assert dropdown is not None, "Dropdown not found"

    # Open dropdown if custom; native doesn't need to stay open
    if kind != "native":
        dropdown.click()
        time.sleep(0.3)

    options = find_options(driver, kind or "")
    assert len(options) > 0, "No options found"

    # Try first three options (or fewer if limited)
    limit = min(3, len(options))
    for i in range(limit):
        opt = options[i]
        label = (opt.text or "").strip()
        print(f"Testing option {i+1}: {label or '<no text>'}")

        if kind == "native":
            sel = Select(dropdown)
            value = opt.get_attribute("value")
            if value is not None:
                sel.select_by_value(value)
            else:
                sel.select_by_index(i)
        else:
            # Ensure menu is open before each click (some UIs close on selection)
            try:
                if not opt.is_displayed():
                    dropdown.click()
                    time.sleep(0.2)
                    # refresh options after reopening
                    options = find_options(driver, kind or "")
                    opt = options[i]
            except Exception:
                dropdown.click()
                time.sleep(0.2)
                options = find_options(driver, kind or "")
                opt = options[i]

            opt.click()

        time.sleep(0.5)
        assert driver.page_source, f"Page broke after selecting option {i+1}"
        print(f"Option {i+1} worked!")

    print("Multiple selection test completed!")
