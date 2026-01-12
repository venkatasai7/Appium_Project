from appium import webdriver
from appium.options.ios import XCUITestOptions
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException
import time


def click_with_retry(wait: WebDriverWait, locator, attempts: int = 5):
    last_err = None
    for _ in range(attempts):
        try:
            el = wait.until(EC.presence_of_element_located(locator))
            # Re-check clickability without keeping old references too long
            wait.until(EC.element_to_be_clickable(locator))
            el.click()
            return
        except StaleElementReferenceException as e:
            last_err = e
            time.sleep(0.5)
    raise last_err if last_err else RuntimeError("Failed to click element")


def test_read_device_about():
    options = XCUITestOptions()
    options.platform_name = "iOS"
    options.platform_version = "26.2"
    options.device_name = "iPhone 17 Pro Max"
    options.automation_name = "XCUITest"
    options.bundle_id = "com.apple.Preferences"
    options.set_capability("newCommandTimeout", 200000)

    driver = webdriver.Remote("http://127.0.0.1:4723", options=options)
    wait = WebDriverWait(driver, 60)

    try:
        # Open General
        click_with_retry(wait, (AppiumBy.ACCESSIBILITY_ID, "General"))

        # Wait until we're actually on the General screen (helps avoid stale UI)
        wait.until(EC.presence_of_element_located((AppiumBy.ACCESSIBILITY_ID, "About")))

        # Open About (tap the cell text)
        click_with_retry(wait, (AppiumBy.ACCESSIBILITY_ID, "About"))

        # Wait for About page content to load (pick something that exists there)
        # "Name" is usually present on About screen
        wait.until(EC.presence_of_element_located((AppiumBy.ACCESSIBILITY_ID, "Name")))

        print("\n📱 Settings → General → About")
        print("=" * 55)

        cells = driver.find_elements(AppiumBy.CLASS_NAME, "XCUIElementTypeCell")
        for cell in cells:
            texts = cell.find_elements(AppiumBy.CLASS_NAME, "XCUIElementTypeStaticText")
            if len(texts) >= 2:
                label = texts[0].text.strip()
                value = texts[-1].text.strip()
                if label and value and label != value:
                    print(f"{label}: {value}")

    finally:
        driver.quit()
