import time
from typing import Union, List, Any, Optional

from appium import webdriver
from appium.webdriver.common.appiumby import AppiumBy
from appium.webdriver.webelement import WebElement
from selenium.common.exceptions import WebDriverException, NoSuchElementException

from .log import default as log


class ElementNotFoundError(Exception):
    def __init__(self, resource: str):
        self.value = f'Element undefined: {resource}'

    def __str__(self):
        return self.value


class AppiumReconnectError(Exception):
    pass


class AppiumDevice:
    # 简单封装 appium webdriver.Remote.集中管理设备连接状态，防止在出现需要重连时，多个引用的状态无法同步的问题
    @classmethod
    def open_remote_driver(cls, appium_server_url: str = None, **cfg):
        """
        启动 Appium 客户端的封装
        :param appium_server_url: Appium服务端地址
        :param cfg: 键值对配置项，参数健值请参考appium客户端配置，
        :return: AppiumDevice
        """
        return AppiumDevice(cls._open_remote_driver(appium_server_url, **cfg))

    @staticmethod
    def _open_remote_driver(appium_server_url: str = None, **cfg) -> webdriver.Remote:
        """
        启动 Appium 客户端
        :param appium_server_url: Appium服务端地址
        :param cfg: 键值对配置项，参数健值请参考appium客户端配置，
        :return: webdriver.Remote
        """
        return webdriver.Remote(appium_server_url or 'http://localhost:4723/wd/hub', cfg)

    def __init__(self, dev: webdriver.Remote):
        self.dev = dev
        self.config = self.dev.capabilities['desired']
        self.appium_server_url = self.dev.command_executor._url
        log.debug(
            f'{type(self)} bind Appium device session [{dev.session_id}] '
            f'on server [{self.appium_server_url}] with config: {self.config}')

    def execute_script(self, script, *args):
        return self.dev.execute_script(script, *args)

    def install_app(self, app_path: str, **options: Any):
        return self.dev.install_app(app_path, **options)

    def remove_app(self, app_id: str, **options: Any):
        return self.dev.remove_app(app_id, **options)

    def push_file(self, destination_path: str, base64data: Optional[str] = None, source_path: Optional[str] = None):
        return self.dev.push_file(destination_path, base64data, source_path)

    def pull_file(self, path: str):
        return self.dev.pull_file(path)

    def get_device_name(self) -> str:
        return self.dev.capabilities['deviceName']

    def check_exists(self, value: str) -> bool:
        try:
            rs = self.dev.page_source
            return value in rs
        except WebDriverException as e:
            log.warning(f'!!! Appium get page source failed!\n===========\n{e}\n============\nTrying again...')
            self.reconnect()
            return self.check_exists(value)

    @staticmethod
    def mk_xpath(value: str, view_tag='*', key=None) -> str:
        """
        构建xpath
        :param value: 值
        :param view_tag: 标签，默认*
        :param key: text, content-desc, class. 默认：content-desc
        :return:
        """
        view_tag = view_tag or '*'
        key = key or "content-desc"
        return f'//{view_tag}[@{key}="{value}"]'

    def find_element_by_xpath(self, value: str, view_tag=None, key=None):
        if self.check_exists(value):
            # 关键字存在，但不一定代表指定的ui元素存在
            try:
                return self.dev.find_element(by=AppiumBy.XPATH, value=self.mk_xpath(value, view_tag, key))
            except NoSuchElementException:
                pass

    def find_elements_by_xpath(self, value: str, view_tag=None, key=None):
        if self.check_exists(value):
            try:
                return self.dev.find_elements(by=AppiumBy.XPATH, value=self.mk_xpath(value, view_tag, key))
            except NoSuchElementException:
                pass

    def find_element(self, value: str, by: str = None) -> WebElement:
        if self.check_exists(value):
            try:
                return self.dev.find_element(by=by or AppiumBy.ID, value=value)
            except NoSuchElementException:
                pass

    def find_elements(self, value: str, by: str = None) -> Union[List[WebElement], List]:
        if self.check_exists(value):
            try:
                return self.dev.find_elements(by=by or AppiumBy.ID, value=value)
            except NoSuchElementException:
                pass

    def exist(self, resource: str, by: str = None, timeout: int = None):
        """是否存在某元素，存在则返回对应元素
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
            try:
                v.click()
            except WebDriverException as e:
                # 经实测，这里都是点击触发后出现的异常(socket hang up)，点击动作能正常执行，暂未明确原因，可直接重连后继续其他操作。
                log.warning('点击后出现异常：%s\n\n即将重新连接...', e)
                self.reconnect()
            return v
        if not on_exists:
            raise ElementNotFoundError(resource)

    def match_content(self, resource: str, txt_or_re, by: str = None, on_exists=False, timeout: int = None) -> bool:
        v = self.exist(resource=resource, by=by, timeout=timeout)
        if v:
            if hasattr(txt_or_re, 'match'):
                return txt_or_re.match(v.text)
            return txt_or_re == v.text
        if not on_exists:
            raise ElementNotFoundError(resource)
        return False

    def swipe(self, x0: int, y0: int, x1: int, y1: int, duration: int = 300):
        return self.dev.swipe(x0, y0, x1, y1, duration=duration)

    def reconnect(self):
        self.quit()
        log.warning(f'!!! Appium reconnect device...')
        try:
            self.dev = self._open_remote_driver(self.appium_server_url, **self.config)
        except WebDriverException as e:
            log.error(f'!!! Appium reconnect failed!\n{e}')
            raise AppiumReconnectError

    def quit(self):
        log.warning('!!! Appium device quit !!!')
        try:
            self.dev.quit()
        except:
            pass
        finally:
            self.dev = None
