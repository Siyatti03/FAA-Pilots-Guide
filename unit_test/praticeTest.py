from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

opts = Options()
driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()),
                          options=opts)

driver.get("https://www.cnn.com/2025/09/25/politics/james-comey-justice-department-trump-bondi-perjury-virginia")
wait = WebDriverWait(driver,10)

wait.until(EC.title_contains('James Comey'))
print("Title ok: ", driver.title)



