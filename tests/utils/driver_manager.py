'''
Author: Devi Granec-Boydstun
    Role: Scrum Master 2
Purpose: This is a script creates the necessary logic for the pytest WebDriver fixture.
         Specifically, downloading the drivers, starting them for use, and returning them.
Needs improvement: handles browser downloads?
'''

# ---- Imports ----
import os
from selenium import webdriver
import platform

# ---- Pathing ----
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BROWSER_DIR = os.path.join(ROOT_DIR, "binaries")

# ---- Variables ----
BROWSER_BINARIES = { # Known binary names for each browser (Linux, MacOS, Windows), excepting safari
        "chrome": ["chrome", "chrome.exe", "chromium", "chromium.exe"],
        "firefox": ["firefox", "firefox.exe"],
        # "edge": ["microsoft-edge", "msedge", "msedge.exe", "microsoftedge", "microsoftedge.exe"],
}

# ---- Find the Browser Binary ----
def find_browser_path(browser_name):
    """
    Searches a single folder (defined "BROWSER_DIR"), and subdirectories, for a known browser binary in BROWSER_BINARIES.
        Supports: Chrome, Firefox, Edge, Safari
    rtype: path to binary, or None for Safari due to not needing a path
    param: browser_name- the browser being used
    """
    # MacOS-specific Safari case
    if browser_name == "safari" and platform.system() == "Darwin":
        # Safari does NOT need to find the binary, the driver handles this
        return None 

    binary_candidates = BROWSER_BINARIES.get(browser_name.lower(), [])
    if not binary_candidates:
        raise ValueError(f"Unsupported browser: {browser_name}")
    
    # Windows/Linux/MacOS non-Safari search
    for root, _, files in os.walk(BROWSER_DIR):
        for file in files:
            if file in binary_candidates:
                return os.path.abspath(os.path.join(root, file))

    # If we get here, there is a problem, as in no binary...
    print(f"ERROR: Unable to find {browser_name} binary, please handle download into the folder: {BROWSER_DIR}") 
    return None

# ---- Download the Webdriver ----
def download_driver(browser):
    '''
    Return the necessary Selenium Webdriver for the the given browser
    rtype: webdriver's path
    param: browser- The browser being used
    '''
    driver_path = None

    # Select the correct browser
    if browser.lower() == "chrome":
        # import the manager that takes care of the page
        from webdriver_manager.chrome import ChromeDriverManager
        driver_path = ChromeDriverManager().install()
    
    elif browser.lower() == "firefox":
        from webdriver_manager.firefox import GeckoDriverManager
        driver_path = GeckoDriverManager().install()
    
    elif browser.lower() == "edge":
        from webdriver_manager.microsoft import EdgeChromiumDriverManager
        driver_path = EdgeChromiumDriverManager().install()

    # There is nothing for Safari to download as MacOS already has it on all devices
    
    return driver_path
    
# ---- Start Webdriver ----
def start_driver(browser_path, browser, headless = True):
    '''
    Return the necessary Selenium Webdriver for the the given browser
    rtype: webdriver
    param: browser_path- path to browser binary, found using func "find_browser_path"
    param: browser- The browser being used
    param: headless- default is true so the graphics don't load for the test
    '''
    options = None

    # Select the correct browser
    if browser.lower() == "chrome":
        # import the chrome services needed for the specifying the location of the downloaded driver
        # import the options for that browser, so we can make the test headless, ie no GUIs
        from selenium.webdriver.chrome.service import Service as ChromeService
        from selenium.webdriver.chrome.options import Options
        options = Options()
        if headless:
            options.add_argument("--headless=new")
        options.binary_location = browser_path
        # Try to return the correct webdriver using the imported Chrome tools, otherwise fail
        try: 
            return webdriver.Chrome(
                service = ChromeService(),
                options = options
            )
        except:
            print(f"ERROR: Unable to create Chrome webdriver") 
            return None

    elif browser.lower() == "firefox":
        # Firefox imports, see specifics above
        from selenium.webdriver.firefox.service import Service as FirefoxService
        from selenium.webdriver.firefox.options import Options
        options = Options()
        if headless:
            # Firefox is a little different with its API
            options.add_argument("--headless")
        options.binary_location = browser_path
        # Try to return the correct webdriver using the imported Firefox tools, otherwise fail
        try: 
            return webdriver.Firefox(
                service = FirefoxService(),
                options = options
            )
        except:
            print(f"ERROR: Unable to create FireFox webdriver") 
            return None
    
    elif browser.lower() == "safari":
        # Safari has the webdriver already, no need to download, also no headless option, and no need to find binary
        try:
            return webdriver.Safari()
        except:
            print(f"ERROR: Unable to create Safari webdriver") 
            return None
    
    else:
        print(f"ERROR: Unsupported Browser=={browser}") 
        return None

    '''
    elif browser.lower() == "edge":
        # Edge imports, see specifics above
        from selenium.webdriver.edge.service import Service as EdgeService
        from selenium.webdriver.edge.options import Options
        options = Options()
        if headless:
            options.add_argument("--headless=new")
        options.binary_location = browser_path
        # Try to return the correct webdriver using the imported Edge tools, otherwise fail
        try:
            return webdriver.Edge(
                service = EdgeService(),
                options = options
            )
        except:
            print(f"ERROR: Unable to create Edge webdriver") 
            return None
    '''
    
# ---- Check for WebDrivers Function ----
def get_driver(browser_type, headless):
    '''
    Returns webdriver with all the details set up
    rtype: the set up website driver
    param: browser_type- the browser being used
    param: headless- T/F to decide if the browser should be shown
    '''
    # Use custom function to identify the browser binary
    browser_path = find_browser_path(browser_type)

    # The webdriver checks local automatically, so we can "download" everytime even if the binary is already there
    _ = download_driver(browser_type)   

    website_driver = start_driver(browser_path, browser_type, headless)
    return website_driver