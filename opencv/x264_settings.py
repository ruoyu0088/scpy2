import _winreg

X264_KEY = r"Software\GNU\x264"


def set_quantizer(value):
    hkey = _winreg.OpenKey(_winreg.HKEY_CURRENT_USER, X264_KEY, 0, _winreg.KEY_ALL_ACCESS)
    _winreg.SetValueEx(hkey, "quantizer", None, _winreg.REG_DWORD, value)