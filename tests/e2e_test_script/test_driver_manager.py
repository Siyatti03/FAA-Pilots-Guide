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
import sys

# ---- Paths ----
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
HTML_DIR = os.path.join(ROOT_DIR, "tests", "e2e_test_script", "HTML_Page")

# ---- Variables ----
if sys.argv[0] == "safari": # This is changed to account for using safari outside an image, because it can't be downloaded
    BROWSER_LIST = [
        {"browser": "safari", "headless": True},
    ]
else:
    BROWSER_LIST = [
        {"browser": "chrome", "headless": True},
        {"browser": "firefox", "headless": True},
        # {"browser": "edge", "headless": True}
    ]
LOCAL_HOST = "file://" + os.path.join(HTML_DIR, "index.html")

# ---- Test function ----
@pytest.mark.parametrize("browser_types_fixture", BROWSER_LIST, indirect = True) # Indirect allows parameterizing fixtures, browser_types_fixture
def test_scripts_work(browser_types_fixture):
    # Pytest will parameterize and pass the current browser/headless element into the fixture "browser_types_fixture"
    driver = browser_types_fixture
    driver.get(LOCAL_HOST)
    assert "Hello World" in driver.title