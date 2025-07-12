from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.wait import WebDriverWait
from watchfiles import awatch


def new_driver() -> Chrome:
    service = ChromeService(executable_path="/home/tongle/chromedriver/chromedriver-138-0-7204-92")
    options = ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--window-size=1920x1080")
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-popup-posting")
    options.add_argument("--disable-popup-content")
    options.add_argument("--disable-popup-menu")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--hide-scrollbars")
    driver = Chrome(service=service, options=options)
    driver.set_page_load_timeout(5)
    driver.implicitly_wait(2)
    return driver

def find_element_by_css_selector(driver: Chrome, css_selector: str) -> WebElement:
    return driver.find_element(By.CSS_SELECTOR, css_selector)