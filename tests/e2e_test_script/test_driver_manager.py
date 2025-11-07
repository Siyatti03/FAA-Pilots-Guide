'''
Author: Devi Granec-Boydstun
    Role: Scrum Master 2
Purpose: This test makes sure the example HTML page in the parent directory under: ./HTML_Page can be run, 
         seen, and use the Selenium scripts. The purpose is just to make sure all source code can be run without
         error on a given OS.
What needs to be changed: Eventually this will need to be run on our actual page
'''

# ---- Imports ----
import os
import pytest

# ---- Paths ----
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
HTML_DIR = os.path.join(ROOT_DIR, "tests", "e2e_test_script", "HTML_Page")

# ---- Variables ----
LOCAL_HOST = "file://" + os.path.join(HTML_DIR, "index.html")
# This is the superset of all browsers, to be filtered by the fixture
BROWSER_SUPERLIST = [{"browser": "chrome", "headless": True},
                    {"browser": "firefox", "headless": True},
                    {"browser": "safari", "headless": True},
                    {"browser": "edge", "headless": True},]

# ---- Test function ----
@pytest.mark.parametrize(
    "browser_types_fixture",
    BROWSER_SUPERLIST,
    indirect=True) # Indirect allows parameterizing fixtures, browser_types_fixture
def test_scripts_work(browser_types_fixture):
    # Pytest will parameterize and pass the current --browser element and use that to skip any not included browsers
    driver = browser_types_fixture
    driver.get(LOCAL_HOST)
    assert "Hello World" in driver.title