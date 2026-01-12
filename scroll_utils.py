import time


def scroll_down(driver, times=6, pause=2):
    """
    Scrolls down the current Safari page multiple times using iOS native swipe.

    :param driver: Appium driver
    :param times: Number of scrolls (default = 3)
    :param pause: Seconds to wait between scrolls
    """
    for _ in range(times):
        driver.execute_script(
            "mobile: swipe",
            {
                "direction": "up",
                "velocity": 1500
            }
        )
        time.sleep(pause)
