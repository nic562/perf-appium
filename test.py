import unittest

from android_perf import PureAdb
from android_perf.adb_with_tools import AdbProxyWithToolsAll

from perf_appium import AndroidPerfBaseHelper, AndroidBaseUI
from perf_appium.android_ui import DeviceOsOperation


class AndroidUI(AndroidBaseUI):

    def get_device_ui(self) -> DeviceOsOperation:
        pass


class MyHelper(AndroidPerfBaseHelper):

    def on_test_cpu_memory(self, current_second: int, max_listen_seconds: int, data: dict):
        pass

    def on_start_cpu_memory_test(self) -> str:
        pass

    def on_start_test_netflow(self):
        pass

    def on_start_screen_record(self):
        pass

    def __init__(self):
        adb = PureAdb.get_proxy()
        super().__init__(AdbProxyWithToolsAll(adb))
        self._ui = AndroidUI(adb)

    @property
    def ui(self) -> AndroidUI:
        return self._ui

    def exit(self, kill_tools=True, kill_process=True):
        self.ui.close()


class Test(unittest.TestCase):
    helper = None
    tools_pkg = 'io.github.nic562.screen.recorder'

    @classmethod
    def setUpClass(cls) -> None:
        print('setUpClass......')
        cls.helper = MyHelper()

    @classmethod
    def tearDownClass(cls) -> None:
        print('tearDownClass......')
        cls.helper.exit()

    def test_home(self):
        self.helper.ui.home()

    def test_launch_tools(self):
        pkg = self.tools_pkg
        self.helper.ui.launch_app(pkg)
        ps = self.helper.adb.dump_running_activities()
        assert pkg in ps

    def test_back(self):
        pkg = self.tools_pkg
        self.helper.ui.launch_app(pkg)
        assert self.helper.ui.find_element(f'{pkg}:id/btn_upload_api')
        self.helper.ui.go_back()


if __name__ == '__main__':
    unittest.main()
