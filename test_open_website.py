import time
import pytest
from scroll_utils import scroll_down

from appium import webdriver
from appium.options.ios import XCUITestOptions
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException

URL = "https://venkatasaik.netlify.app/"

@pytest.fixture
def driver():
    options = XCUITestOptions()
    options.platform_name = "iOS"
    options.platform_version = "26.2"
    options.device_name = "iPhone 17 Pro Max"
    options.automation_name = "XCUITest"
    options.bundle_id = "com.apple.mobilesafari"
    options.no_reset = True
    options.set_capability("appium:boundElementsByIndex", True)

    drv = webdriver.Remote("http://localhost:4723", options=options)
    yield drv
    drv.quit()


def test_open_website_in_safari(driver):
    wait = WebDriverWait(driver, 60)

    # 1) Find address bar
    address_bar = wait.until(
        EC.presence_of_element_located((AppiumBy.IOS_PREDICATE, "type == 'XCUIElementTypeTextField'"))
    )
    time.sleep(5)

    # 2) Tap address bar
    address_bar.click()
    time.sleep(5)

    # 3) Wait keyboard
    wait.until(EC.presence_of_element_located((AppiumBy.CLASS_NAME, "XCUIElementTypeKeyboard")))
    time.sleep(5)

    # 4) Type URL (stale-safe)
    for _ in range(3):
        try:
            active = driver.switch_to.active_element
            try:
                active.clear()
                time.sleep(2)
            except Exception:
                pass
            active.send_keys(URL)
            break
        except StaleElementReferenceException:
            time.sleep(1)
            address_bar = wait.until(
                EC.presence_of_element_located((AppiumBy.IOS_PREDICATE, "type == 'XCUIElementTypeTextField'"))
            )
            address_bar.click()
            wait.until(EC.presence_of_element_located((AppiumBy.CLASS_NAME, "XCUIElementTypeKeyboard")))

    time.sleep(5)

    # ✅ IMPORTANT: re-focus so Go submits the typed URL, not a suggestion list
    driver.switch_to.active_element.click()
    time.sleep(1)

    # 5) Tap keyboard Go button (most reliable)
    try:
        wait.until(EC.element_to_be_clickable((AppiumBy.ACCESSIBILITY_ID, "Go"))).click()
    except Exception:
        try:
            wait.until(EC.element_to_be_clickable((AppiumBy.ACCESSIBILITY_ID, "Search"))).click()
        except Exception:
            driver.execute_script("mobile: performEditorAction", {"action": "go"})

    time.sleep(8)
    scroll_down(driver)
    # 6) Validation
    assert "venkatasaik" in driver.page_source.lower()
