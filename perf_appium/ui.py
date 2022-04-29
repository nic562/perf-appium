import time

from appium import webdriver
from appium.webdriver.common.appiumby import AppiumBy
from appium.webdriver.webelement import WebElement

from android_perf.base_adb import AdbProxy


class ElementNotFound(Exception):
    def __init__(self, resource: str):
        self.value = f'Element undefined: {resource}'

    def __str__(self):
        return self.value


class UI(object):

    @staticmethod
    def open_remote_android_driver(adb: AdbProxy, appium_server_url: str = None, **cfg):
        """
        启动 Appium 客户端
        :param adb:
        :param appium_server_url: Appium服务端地址
        :param cfg: 键值对配置项，参数健值请参考appium客户端配置，如：
            appPackage: 需启动的 app 包名
            appActivity: app 启动的主 Activity
            noReset: bool，是否保留 session 信息，默认 True 可以避免重新登录
        :return:
        """
        config = {
            "platformName": "Android",  # 操作系统
            "deviceName": adb.get_device_serial(),  # 设备 ID
            "platformVersion": adb.get_device_info().os_version,  # 设备版本号
            'noReset': True
        }
        config.update(cfg)
        return webdriver.Remote(appium_server_url or 'http://localhost:4723/wd/hub', config)

    def __init__(self, dev: webdriver.Remote, adb: AdbProxy):
        self.dev = dev
        self.adb = adb

    def find_element(self, value: str, by: str = None) -> WebElement:
        if value in self.dev.page_source:
            return self.dev.find_element(by=by or AppiumBy.ID, value=value)

    def exist(self, resource: str, by: str = None, timeout: int = None):
        """是否存在某元素
        :param resource: 要判断的资源，可以是 元素id，元素标签，x-path等，详情查看 AppiumBy
        :param by: 支持的资源筛查类型，详情查看 AppiumBy，可为空，则按默认：资源ID
        :param timeout: 要循环判断的秒数（每秒1次），为空则不重复判断
        :return 如果存在，则返回对应 Element 对象，否则返回 False
        """
        if not timeout:
            return self.find_element(resource, by) or False
        for i in range(timeout):
            time.sleep(1)
            v = self.find_element(resource, by)
            if v:
                return v
        return False

    def click(self, resource: str, by: str = None, on_exists=False, timeout: int = None):
        v = self.exist(resource=resource, by=by, timeout=timeout)
        if v:
            return v.click()
        if not on_exists:
            raise ElementNotFound(resource)

    def input(self, value: str):
        # 向界面元素对象输入文本，前提是必须先对对象执行click事件
        self.adb.input(value)

    def match_content(self, resource: str, txt_re, by: str = None, on_exists=False, timeout: int = None) -> bool:
        v = self.exist(resource=resource, by=by, timeout=timeout)
        if v:
            return txt_re.match(v.text)
        if not on_exists:
            raise ElementNotFound(resource)
        return False

    @staticmethod
    def sleep(seconds: int):
        time.sleep(seconds)
