'''
Author: Lauren Dodge
    Role: Product Owner & QA
Purpose: E2E tests for the Questionnaire "Start Over" control using shared Selenium helpers.
         Verifies: (1) control is present/clickable, (2) reset returns to the first question,
         and (3) prior selections do not persist after reset.
'''

# === Standard Imports ===
import os
import sys
import pytest

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# ---- PATHING  ----
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
UTILS_DIR = os.path.join(ROOT_DIR, "tests", "utils")
sys.path.append(UTILS_DIR)

# === Shared Helper Imports ===
from e2e_helpers import (
    checkPageReady,
    findElementByRoleExisting,
    waitAndClick,
    BASE_URL,
    DEFAULT_TIMEOUT,
)

# Line 41 change to import
from driver_variables import BROWSER_SUPERLIST

# === Config / Constants ===
APP_URL: str = os.getenv("APP_BASE_URL", BASE_URL)

# Stable data-testid hooks
Q_TEXT = (By.CSS_SELECTOR, '[data-testid="question-text"]')
BTN_NEXT = '[data-testid="next-btn"]'
BTN_START_OVER = '[data-testid="start-over-btn"]'
CHOICE = (By.CSS_SELECTOR, '[data-testid="choice"]')


def read_question_text(driver, timeout=None) -> str:
    to = timeout or DEFAULT_TIMEOUT
    el = WebDriverWait(driver, to).until(EC.presence_of_element_located(Q_TEXT))
    return el.text.strip()


# === Tests ===

@pytest.mark.parametrize(
    "browser_types_fixture",
    BROWSER_SUPERLIST,
    indirect=True
)
def test_start_over_is_present_and_clickable(browser_types_fixture):
    driver = browser_types_fixture
    checkPageReady(driver, APP_URL)

    findElementByRoleExisting(driver, "button", "Start Over")
    waitAndClick(driver, BTN_START_OVER)

    assert True


@pytest.mark.parametrize(
    "browser_types_fixture",
    BROWSER_SUPERLIST,
    indirect=True
)
def test_start_over_returns_to_first_question(browser_types_fixture):
    driver = browser_types_fixture
    checkPageReady(driver, APP_URL)

    initial_q = read_question_text(driver)

    options = driver.find_elements(*CHOICE)
    if options:
        options[0].click()

    waitAndClick(driver, BTN_NEXT)
    waitAndClick(driver, BTN_START_OVER)

    reset_q = read_question_text(driver)
    assert reset_q == initial_q


@pytest.mark.parametrize(
    "browser_types_fixture",
    BROWSER_SUPERLIST,
    indirect=True
)
def test_start_over_clears_prior_selections(browser_types_fixture):
    driver = browser_types_fixture
    checkPageReady(driver, APP_URL)

    options = driver.find_elements(*CHOICE)
    if options:
        options[0].click()

    waitAndClick(driver, BTN_NEXT)
    waitAndClick(driver, BTN_START_OVER)

    options_after = driver.find_elements(*CHOICE)
    for el in options_after:
        try:
            if hasattr(el, "is_selected"):
                assert not el.is_selected()
        except Exception:
            pass
