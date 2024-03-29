import abc

from android_perf.perf_helper import AndroidPerfBaseHelper as _AndroidPerfBaseHelper
from android_perf.perf_helper import AndroidPerfBaseHelperWithWhistle as _AndroidPerfBaseHelperWithWhistle

from .ui_helper import AndroidBaseUI
from .log import default as logging


class AndroidPerfBaseHelper(_AndroidPerfBaseHelper, metaclass=abc.ABCMeta):

    @property
    @abc.abstractmethod
    def ui(self) -> AndroidBaseUI:
        raise NotImplementedError

    def close_all_app(self):
        logging.info('关闭所有App！')
        self.ui.home()
        self.ui.sleep(1)
        self.ui.close_all_app()

    def apply_screen_record_permission(self) -> bool:
        logging.info('请求录屏授权...')
        return self.ui.permission_screen_record()


class AndroidPerfBaseHelperWithWhistle(AndroidPerfBaseHelper, _AndroidPerfBaseHelperWithWhistle, metaclass=abc.ABCMeta):
    pass
