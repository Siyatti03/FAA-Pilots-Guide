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

from unit_test.e2e_helpers import (
    checkPageReady,
    findElementById,
    waitAndClick,
    BASE_URL,
)

# All (placeholder) expected paths and outcomes
test_cases = [
    (["yes", "hot"], "Recommend Hot Coffee"),
    (["yes", "iced"], "Recommend Iced Coffee"),
    (["no"], "Recommend Tea")
]

# ---- Variables ----
LOCAL_HOST = "http://localhost:3000"
BROWSER_LIST = ["chrome", "firefox", "edge"]
WAIT_TIMEOUT = 10

# ---- Download the necessary drivers (borrowed from Devi's test script) ----
def get_driver(browser, headless=True):
    '''
    Return the necessary Selenium Webdriver for the the given browser
    rtype: webdriver
    browser - The browser being used
    headless - default is false so the graphics don't load for the test
    '''
    options = None

    # Select the correct browser
    if browser.lower() == "chrome":
        # import the chrome services needed for the specifying the location of the downloaded driver
        # import the options for that browser, so we can make the test headless, ie no GUIs
        # import the manager that takes care of the page
        from selenium.webdriver.chrome.service import Service as ChromeService
        from selenium.webdriver.chrome.options import Options
        from webdriver_manager.chrome import ChromeDriverManager
        options = Options()
        if headless:
            options.add_argument("--headless=new")
        # Return the correct webdriver using the imported Chrome tools
        return webdriver.Chrome(
            service = ChromeService(ChromeDriverManager().install()),
            options = options
        )
    
    elif browser.lower() == "firefox":
        # Firefox imports, see specifics above
        from selenium.webdriver.firefox.service import Service as FirefoxService
        from selenium.webdriver.firefox.options import Options
        from webdriver_manager.firefox import GeckoDriverManager
        options = Options()
        if headless:
            # Firefox is a little different with its API
            options.add_argument("--headless")
        # Return the correct webdriver using the imported Firefox tools
        return webdriver.Firefox(
            service = FirefoxService(GeckoDriverManager().install()),
            options = options
        )
    
    elif browser.lower() == "edge":
        # Edge imports, see specifics above
        from selenium.webdriver.edge.service import Service as EdgeService
        from selenium.webdriver.edge.options import Options
        from webdriver_manager.microsoft import EdgeChromiumDriverManager
        options = Options()
        if headless:
            options.add_argument("--headless=new")
        # Return the correct webdriver using the imported Edge tools
        return webdriver.Edge(
            service = EdgeService(EdgeChromiumDriverManager().install()),
            options = options
        )

# --- Test Runner ---
def run_flow_test(driver, path, expected):
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
    result_elem = findElementById(driver, "result")
    result = result_elem.text.strip()

    return result == expected, result

# --- Full/Main Test Runner ---
def flow_test_runner(browser="chrome", headless=True):
    '''
    Main function to run all flowchart tests and report results.
    '''
    print(f"Starting Flowchart Tests in {browser.capitalize()} (Headless: {headless})...")

    driver = None
    all_passed = True
    
    try:
        # Get the driver
        driver = get_driver(browser, headless=headless)
        
        print("\nFLOWCHART TEST RESULTS:\n")
        all_passed = True
        
        # Iterate through all defined test cases
        for path, expected in test_cases:
            # Run the test for the specific path
            passed, result = run_flow_test(driver, path, expected)
            
            if passed:
                print(f"OK: Path {path} => Got '{result}' (Expected '{expected}')")
            else:
                all_passed = False
                print(f"!!ERR!!: Path {path} => Got '{result}', Expected '{expected}'")

        if all_passed:
            print("\nAll tests passed.")
        else:
            print("\nSome tests failed.")
            
    except Exception as e:
        print(f"\nAn error occurred during testing: {e}")
        all_passed = False
        
    finally:
        # Ensure the driver is closed even if an error occurs
        if 'driver' in locals() and driver:
            driver.quit()