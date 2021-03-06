import abc
from functools import wraps

from .android_ui import AndroidBaseUI, DeviceOsOperation


def call_device_ui(func):
    # 适配不同设备的情况
    @wraps(func)
    def wrapper(ui, *args):
        assert isinstance(ui, AndroidUI)
        dev = ui.get_device_ui()
        fn = getattr(dev, func.__name__)
        if fn:
            return fn(*args)
        return func(*args)

    return wrapper


class AndroidUI(AndroidBaseUI, metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def get_device_ui(self) -> DeviceOsOperation:
        raise NotImplementedError

    @call_device_ui
    def install_app(self, file_path: str):
        return super().install_app(file_path)

    @call_device_ui
    def permission_device_info(self) -> bool:
        return False

    @call_device_ui
    def permission_screen_record(self) -> bool:
        return False

    @call_device_ui
    def permission_require(self) -> bool:
        return False

    @call_device_ui
    def permission_storage(self) -> bool:
        return False

    @call_device_ui
    def permission_phone(self) -> bool:
        return False

    @call_device_ui
    def permission_location(self) -> bool:
        return False

    @call_device_ui
    def close_all_app(self) -> bool:
        return False

    @call_device_ui
    def upgrade_apps(self) -> bool:
        return False

    @call_device_ui
    def get_main_container(self):
        return None

