'''
Author: Devi Granec-Boydstun
    Role: Scrum Master 2
Purpose: This creates the pytest custom features used for our testing infastructure
'''

# ---- Imports ----
import pytest
import os
import sys

# ---- Pathing ----
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UTILS_DIR = os.path.join(ROOT_DIR, "tests", "utils")

# ---- Importing driver script ----
sys.path.append(UTILS_DIR)
print(sys.path)

import driver_manager as dm

# ---- Browser Capture Fixture ----
def pytest_addoption(parser):
    parser.addoption(
        "--browser", action="store", default="default", 
        choices = ["default", "chrome", "firefox", "edge", "safari"],
        help ="Browser option to pick what browsers needed to test on"
    )

# ---- Browser Fixture ----
@pytest.fixture(scope="function")
def browser_types_fixture(request, pytestconfig):
    # Use browser fixture to identify the browsers we are testing on from pytest command
    selected_browser = pytestconfig.getoption("browser")

    # Pull out the browser dict from paramater
    browser_param = request.param

    # Filter based on browser fixture, skip any not in the browser list
    if selected_browser == "default" and (browser_param["browser"] not in ["chrome", "firefox"]):
        pytest.skip(f"TEST SKIPPED: (DEFAULTED) Skipping {browser_param['browser']}")
    elif selected_browser != "default" and (browser_param["browser"] != selected_browser):
        pytest.skip(f"TEST SKIPPED: Skipping {browser_param['browser']} because not in browser list, --browser={selected_browser}")

    # Use script in ./test/utils function get_driver to download the browser's webdriver
    driver = dm.get_driver(browser_param["browser"], browser_param["headless"])

    # Yield can be used in a fixture to give control to the test function, then when control is returned the 
    # driver is safely killed by the fixture
    yield driver
    driver.quit()