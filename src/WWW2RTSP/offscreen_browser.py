#!/usr/bin/python3
import sys
from selenium import webdriver
from xvfbwrapper import Xvfb
from enum import Enum


class Browsers(Enum):
    FIREFOX = "firefox"
    CHROMIUM = "chromium"

    def __str__(self):
        return self.value

class OffscreenBrowserFactory():
    def __init__(self, browser_choice: Browsers, default_width: int, default_height: int):
        self.browser_choice = browser_choice
        self.default_width = default_width
        self.default_height = default_height

    def open_browser(self, url, width = None, height = None):
        width = self.default_width if width is None else width
        height = self.default_height if height is None else height

        return OffscreenBrowser(url, self.browser_choice, width, height)

class OffscreenBrowser():
    _cleanup = []
    browser = None
    xvfb = None
    display = None

    def __init__(self, url: str, browser_choice: Browsers, width: int = 1920, height: int = 1080):
        self.open_xvfb(width, height)
        self.open_browser(browser_choice, width, height)
        self.open_url(url)
        print("browser started on display: :{}".format(self.display))

    def cleanup(self):
        while len(self._cleanup) != 0:
            fn = self._cleanup.pop()
            try:
             fn()
            except Exception as e:
                print(e, file=sys.stderr)

    def add_cleanup(self, fn):
        self._cleanup.append(fn)

    def open_xvfb(self, width, height):
        self.xvfb = Xvfb(width=width, height=height, colordepth=24)
        self.xvfb.start()
        self.add_cleanup(self.xvfb.stop)
        self.display = self.xvfb.new_display

    def open_browser(self, browser_choice: Browsers, width: int, height: int):
        if browser_choice == Browsers.FIREFOX:
            self.browser = webdriver.Firefox()
            self.browser.maximize_window()
        else:
            options = get_chromium_options(width, height)
            self.browser = webdriver.Chrome(chrome_options=options)
        self.add_cleanup(self.browser.quit)

    def open_url(self, url):
        self.browser.get(url)


def get_chromium_options(width: int, height: int):
    options = webdriver.ChromeOptions()
    options.add_argument("--disable-infobars")
    options.add_argument("--start-maximized")
    options.add_argument("--kiosk")
    options.add_argument("--noerrdialogs")
    options.add_argument("--incognito")
    options.add_argument("--window-size={},{}".format(width, height))
    return options

# only used for dev purposes
if __name__ == "__main__":
    width = 1920
    height = 1080
    if len(sys.argv) < 2:
        raise Exception("url needed")

    url = sys.argv[1]
    try:
        ob = OffscreenBrowser(url, Browsers.CHROMIUM, width, height)
    except Exception as e:
        print(e, file=sys.stderr)
        ob.cleanup()

    print("DISPLAY=:{}".format(ob.display))
    input("press enter do exit")
    ob.cleanup()