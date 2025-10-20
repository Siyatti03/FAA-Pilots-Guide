"""
Author: Dien Mai
    Role: Scrum Master 4
Purpose: Shared Selenium E2E helpers for the FAA tool. These utilities make tests
         more readable, robust, and consistent across suites.
Functions Provided:
        1. checkPageReady(driver, url) - open a URL and wait until ready
        2. findElementById(driver, element_id, timeout=None) - wait for element by id
        3. findElementByRoleExisting(driver, role, name, timeout=None) - find by role + aria-label
        4. waitAndClick(driver, css, timeout=None) - wait until clickable then click
Config:
        - BASE_URL: app base URL (env: BASE_URL)
        - DEFAULT_TIMEOUT: wait timeout in seconds (env: E2E_TIMEOUT)
Usage Examples:
        from unit_test.e2e_helpers import (
            checkPageReady, findElementById, findElementByRoleExisting, waitAndClick, BASE_URL
        )
        checkPageReady(driver, BASE_URL)
        findElementById(driver, "FAA_Term_Search_Input").send_keys("airspeed\n")
        waitAndClick(driver, 'button[data-answer="yes"]')
        findElementByRoleExisting(driver, "button", "Print this checklist").click()
"""

from __future__ import annotations

import os
from typing import Optional

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# ---- Configuration ----
DEFAULT_TIMEOUT: int = int(os.getenv("E2E_TIMEOUT", "15"))
BASE_URL: str = os.getenv("BASE_URL", "http://localhost:3000")


# ---- Internal primitives ----
def _wait(driver, condition, timeout: Optional[int] = None):
    """Internal helper to standardize WebDriverWait usage."""
    to = timeout or DEFAULT_TIMEOUT
    return WebDriverWait(driver, to).until(condition)


# ---- Public API ----
def checkPageReady(driver, url: str) -> None:
    """Navigate to url and wait until <body> is present (page ready)."""
    driver.get(url)
    _wait(driver, EC.presence_of_element_located((By.TAG_NAME, "body")))

def findElementByRoleExisting(
    driver,
    role: str,
    name: str,
    timeout: Optional[int] = None,
):
    """Find element by ARIA role + aria-label (accessible and stable)."""
    xpath = f"//*[@role='{role}' and @aria-label='{name}']"
    return _wait(driver, EC.presence_of_element_located((By.XPATH, xpath)), timeout)


def waitAndClick(driver, css: str, timeout: Optional[int] = None) -> None:
    """Wait until a CSS target is clickable, then click it."""
    _wait(driver, EC.element_to_be_clickable((By.CSS_SELECTOR, css)), timeout).click()


__all__ = [
    "checkPageReady",
    "findElementById",
    "findElementByRoleExisting",
    "waitAndClick",
    "BASE_URL",
    "DEFAULT_TIMEOUT",
]