import time
import abc
from typing import Union, List

from appium.webdriver.webelement import WebElement

from .appium_device import AppiumDevice


class BaseUI(metaclass=abc.ABCMeta):

    def __init__(self, dev: AppiumDevice):
        self.dev = dev

    def find_element(self, value: str, by: str = None) -> WebElement:
        return self.dev.find_element(value, by)

    def find_elements(self, value: str, by: str = None) -> Union[List[WebElement], List]:
        return self.dev.find_elements(value, by)

    def find_element_by_xpath(self, value: str, view_tag=None, key=None):
        return self.dev.find_element_by_xpath(value, view_tag, key)

    def find_elements_by_xpath(self, value: str, view_tag=None, key=None):
        return self.dev.find_elements_by_xpath(value, view_tag, key)

    def exist(self, resource: str, by: str = None, timeout: int = None):
        return self.dev.exist(resource, by, timeout)

    def click(self, resource: str, by: str = None, on_exists=False, timeout: int = None):
        return self.dev.click(resource, by, on_exists, timeout)

    @abc.abstractmethod
    def input(self, value: str):
        raise NotImplementedError

    def match_content(self, resource: str, txt_or_re, by: str = None, on_exists=False, timeout: int = None) -> bool:
        return self.dev.match_content(resource, txt_or_re, by, on_exists, timeout)

    def swipe(self, x0: int, y0: int, x1: int, y1: int, duration: int = 300):
        return self.dev.swipe(x0, y0, x1, y1, duration=duration)

    @abc.abstractmethod
    def get_device_resolution(self) -> (int, int):
        raise NotImplementedError

    def quit(self):
        return self.dev.quit()

    @staticmethod
    def sleep(seconds: int):
        time.sleep(seconds)
