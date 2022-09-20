import abc

from android_perf.base_adb import AdbProxy

from .ui import BaseUI
from .log import default as log
from .appium_device import AppiumDevice


class DeviceOsOperation(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def permission_device_info(self) -> bool:
        raise NotImplementedError

    @abc.abstractmethod
    def permission_screen_record(self) -> bool:
        raise NotImplementedError

    @abc.abstractmethod
    def permission_require(self) -> bool:
        raise NotImplementedError

    @abc.abstractmethod
    def permission_storage(self) -> bool:
        raise NotImplementedError

    @abc.abstractmethod
    def permission_phone(self) -> bool:
        raise NotImplementedError

    @abc.abstractmethod
    def permission_location(self) -> bool:
        raise NotImplementedError

    @abc.abstractmethod
    def close_all_app(self) -> bool:
        raise NotImplementedError

    @abc.abstractmethod
    def upgrade_app(self, pkg: str) -> bool:
        # 升级指定应用
        raise NotImplementedError

    @abc.abstractmethod
    def get_main_container(self):
        raise NotImplementedError


class AndroidBaseUI(BaseUI, DeviceOsOperation, metaclass=abc.ABCMeta):

    @staticmethod
    def open_android_driver_by_adb(adb: AdbProxy, appium_server_url: str = None, **cfg) -> AppiumDevice:
        """
        启动 Appium 客户端
        :param adb:
        :param appium_server_url: Appium服务端地址
        :param cfg: 键值对配置项，不指定的话，则单纯直接进入Android界面。参数健值请参考appium客户端配置，如：
            appPackage: 需启动的 app 包名
            appActivity: app 启动的主 Activity
            noReset: bool，是否保留 session 信息，默认 True 可以避免重新登录
        :return:
        """
        config = {
            "platformName": "Android",  # 操作系统
            "udid": adb.get_device_serial(),  # 设备 ID
            "platformVersion": adb.get_device_info().os_version,  # 设备版本号
            # 'noReset': True
        }
        config.update(cfg)
        return AppiumDevice.open_remote_driver(appium_server_url, **config)

    @staticmethod
    def open_android_driver(serial: str = None, appium_server_url: str = None, **cfg) -> AppiumDevice:
        config = {
            "platformName": "Android",  # 操作系统
            "udid": serial,  # 设备 ID
        }
        config.update(cfg)
        return AppiumDevice.open_remote_driver(appium_server_url, **config)

    def __init__(self, adb: AdbProxy, dev: AppiumDevice = None):
        assert adb
        if dev is None:
            dev = self.open_android_driver_by_adb(adb)
        super().__init__(dev)
        self.adb = adb
        self.device_info = self.adb.get_device_info()
        res = self.get_device_resolution()
        self.screen_width = res[0]
        self.screen_height = res[1]

    def close(self):
        self.quit()
        self.adb.close()

    def home(self):
        self.adb.home()

    def go_back(self):
        self.adb.go_back()

    def task_manager(self):
        self.adb.task_manager()

    def input(self, value: str):
        # 向界面元素对象输入文本，前提是必须先对对象执行click事件
        return self.adb.input(value)

    def get_device_resolution(self) -> (int, int):
        return self.adb.get_device_resolution()

    def open_app_market(self, pkg: str):
        return self.adb.run_shell(f'am start -d market://details?id={pkg}')

    @property
    def device_brand(self):
        k = '_device_brand'
        if not hasattr(self, k):
            setattr(self, k, self.device_info.brand.lower())
        return getattr(self, k)

    def clear_app(self, pkg: str):
        """清理App所有数据，需要到开发者选项中开启’禁止权限监控‘"""
        try:
            rs = self.adb.clear_app(pkg)
            if rs and rs.find('Exception') != -1:
                raise Exception(rs)
        except Exception as e:
            raise Exception(f'清理 App 失败: {e}\n请尝试到开发者选项中开启’禁止权限监控‘！')

    def launch_app(self, pkg: str, activity: str = None):
        self.adb.launch_app(pkg, activity)

    def kill_app(self, pkg: str):
        self.adb.kill_app(pkg)

    def remove_app(self, pkg: str):
        try:
            self.adb.uninstall_app(pkg)
        except Exception as e:
            log.warning(f'Remove App Failed: {e}')

    def install_app(self, file_path: str):
        """直接执行安装过程，安装过程会卡住主进程，不同设备可能会有界面操作上的问题"""
        return self.adb.install_app(file_path)

    def exists_app(self, pkg: str) -> str:
        return self.adb.get_app_version(pkg)
