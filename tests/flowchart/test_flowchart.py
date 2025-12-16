#   Author: Raimund Ilagan (@rilaag, raimund.r.ilagan-1@ou.edu)
#   Role: Sprint Master 3
#   Note: Values here are all placeholders, because we don't have an actual page set up, at time of writing.
#   Reliant on an external JSON to be issued, thus the use of path as a parameter.
#   Purpose:
#       Test whether a questionnaire flowchart's logic is valid
#       by simulating all possible flowchart paths,
#       verify that each path outcome matches expected results,
#       and document the results, noting which paths passed and failed.
#   Tests implemented:
#       Iterating through every expected path and outcome.
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import pytest
import sys
import os
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
UTILS_DIR = os.path.join(ROOT_DIR, "tests", "utils")
E2E_DIR = os.path.join(ROOT_DIR, "tests", "e2e_test_script")
sys.path.append(UTILS_DIR)
sys.path.append(E2E_DIR)

from e2e_helpers import (
    checkPageReady,
    findElementByRoleExisting,
    waitAndClick,
    BASE_URL,
)
from test_driver_manager import BROWSER_SUPERLIST

# All (placeholder) expected paths and outcomes
test_cases = [
    (["Blood Pressure Disorders", "No"], ["Form Name 1", "Form Name 2"]),
]

# ---- Variables ----
LOCAL_HOST = "http://localhost:3000"
WAIT_TIMEOUT = 10

# --- Test ---
@pytest.mark.parametrize(
    "browser_types_fixture",
    BROWSER_SUPERLIST,
    indirect=True) # Indirect allows parameterizing fixtures, browser_types_fixture
def test_run_flow(driver, path, expected):
    """
    Clicks through the flowchart following the given path and verifies result text.
    Returns: (bool: passed, str: result)
    """

    # use the e2e page ready helper to load and wait for page ready
    checkPageReady(driver, LOCAL_HOST)

    # Follow the defined button path
    for answer in path:
        css_selector = f'button[data-answer="{answer}"]'
        waitAndClick(driver, css_selector)

    # Use helper to find final result element
    result_elem = findElementByRoleExisting(driver, "text-summary", "summary")
    result = result_elem.text.strip()

    assert result == expected, result