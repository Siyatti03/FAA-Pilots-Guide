#   Author: Raimund Ilagan (@rilaag, raimund.r.ilagan-1@ou.edu)
#   Role: Sprint Master 3
#   Note: Values here are all placeholders, because we don't have an actual page set up, at time of writing.
#   Purpose:
#       Test whether a questionnaire flowchart's logic is valid
#       by simulating all possible flowchart paths,
#       verify that each path outcome matches expected results,
#       and document the results, noting which paths passed and failed.
#   Tests implemented:
#       Iterating through every expected path and outcome.

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# Define all expected paths and outcomes
test_cases = [
    (["yes", "hot"], "Recommend Hot Coffee"),
    (["yes", "iced"], "Recommend Iced Coffee"),
    (["no"], "Recommend Tea")
]

def run_flow_test(driver, path, expected):
    driver.get("http://localhost:3000")  # Replace with your app URL
    time.sleep(1)  # wait for page load

    for answer in path:
        btn = driver.find_element(By.CSS_SELECTOR, f'button[data-answer="{answer}"]')
        btn.click()
        time.sleep(0.5)

    result_elem = driver.find_element(By.ID, "result")
    result = result_elem.text.strip()

    return result == expected, result

if __name__ == "__main__":
    # Enable headless mode
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")  # modern headless mode
    chrome_options.add_argument("--disable-gpu")  # optional, for Windows
    chrome_options.add_argument("--window-size=1920,1080")

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=chrome_options
    )

    print("\nFLOWCHART TEST RESULTS:\n")
    for path, expected in test_cases:
        passed, result = run_flow_test(driver, path, expected)
        if passed:
            print(f"OK: Path {path} => {result}")
        else:
            print(f"!!ERR!!: Path {path} => Got '{result}', Expected '{expected}'")

    driver.quit()
