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

# ---- Browser Fixture ----
@pytest.fixture(scope="function")
def browser_types_fixture(request):
    # Get the paramaters from the fixture, and seperate with defaults to avoid issues
    params = request.param
    browser_type = params.get("browser", "chrome")
    headless = params.get("headless", True)

    # Use script in ./test/utils function get_driver to download the browser's webdriver
    driver = dm.get_driver(browser_type, headless)

    # Yield can be used in a fixture to give control to the test function, then when control is returned the 
    # driver is safely killed by the fixture
    yield driver
    driver.quit()