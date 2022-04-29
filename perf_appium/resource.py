import re


def get_android_id(app_id: str, element_id: str) -> str:
    return f'{app_id}:id/{element_id}'


class AndroidResourceBase(type):
    """用于识别特定的界面元素id
    定义的元素id类属性名称请以`_ID`结尾"""
    ROOT = None

    def get_root(cls):
        v = object.__getattribute__(cls, 'ROOT')
        return v

    def __getattribute__(cls, item: str):
        v = object.__getattribute__(cls, item)
        if item.endswith('_ID') and isinstance(v, str):
            return get_android_id(cls.get_root(), v)
        if type(v) == AndroidResourceBase:
            if object.__getattribute__(v, 'ROOT') is None:
                _r = cls.get_root()
                v.ROOT = _r
        return v


class AndroidOsResource(metaclass=AndroidResourceBase):
    ROOT = 'android'
    MAIN_CONTENT_ID = 'content'

    class Permission(metaclass=AndroidResourceBase):
        ROOT = 'com.android.permissioncontroller'

        TXT_PHONE_RE = re.compile(r'\S+需要使用电话权限')
        TXT_MESSAGE_ID = 'permission_message'
        BTN_ALLOW_ID = 'permission_allow_button'
        BTN_DENY_ID = 'permission_deny_button'


if __name__ == '__main__':
    print(AndroidOsResource, 'main content id:', AndroidOsResource.MAIN_CONTENT_ID)
    print(AndroidOsResource.Permission, 'message id:', AndroidOsResource.Permission.TXT_MESSAGE_ID)
