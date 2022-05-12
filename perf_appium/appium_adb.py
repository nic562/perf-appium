import types
import base64
from http.client import RemoteDisconnected

from selenium.common.exceptions import WebDriverException

from android_perf.base_adb import AdbInterface

from .appium_device import AppiumDevice
from .log import default as log


class AppiumAdb(AdbInterface):
    # 通过Appium 服务（http方式）执行adb 指令，经实测，效率很差，对实时性要求高的不建议用

    def __init__(self, dev: AppiumDevice):
        self.dev = dev

    def run_shell(self, cmd: str, clean_wrap=False) -> str:
        try:
            rs = self.dev.execute_script('mobile: shell', {
                'command': cmd,
                # 'args': [''],
                'includeStderr': True,
                'timeout': 5000
            })
            out = rs['stdout'] or rs['stderr']
            if clean_wrap:
                return out.strip()
            return out
        except WebDriverException as e:
            return str(e)
        except RemoteDisconnected as e:
            log.warning(f'Appium请求失败 {e}，重试...')
            return self.run_shell(cmd, clean_wrap)

    def stream_shell(self, cmd: str) -> types.GeneratorType:
        raise NotImplementedError('Appium-adb not support for `stream shell`')

    def close(self):
        self.dev.quit()

    def install_app(self, apk_path):
        return self.dev.install_app(apk_path, replace=True)

    def uninstall_app(self, app_bundle: str):
        return self.dev.remove_app(app_bundle)

    def push_file(self, local_path: str, device_path: str):
        return self.dev.push_file(device_path, source_path=local_path)

    def pull_file(self, device_path: str, local_path: str):
        ct_b64 = self.dev.pull_file(device_path)
        rs = base64.b64decode(ct_b64)
        with open(local_path, 'wb') as f:
            f.write(rs)
        return local_path

    def get_device_serial(self) -> str:
        return self.dev.get_device_name()

    def devices(self):
        raise NotImplementedError('Appium-adb not support for `devices`')



