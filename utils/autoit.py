# -*- coding: utf-8 -*-
from os import path
from ctypes import windll

FOLDER = path.dirname(__file__)

autoit = windll.LoadLibrary(path.join(FOLDER, "AutoItX3.dll"))

def run(path, folder=u"", show_flag=1):
    return autoit.AU3_Run(path, folder, show_flag)
    
def win_wait(title, text=u"", timeout=0):
    return autoit.AU3_WinWait(title, text, timeout)
    
def win_exists(title, text=u""):
    return autoit.AU3_WinExists(title, text)    

def win_set_on_top(title, flag, text=u""):    
    return autoit.AU3_WinSetOnTop(title, text, flag)
 
def win_get_handle(title, text=u""):
    return autoit.AU3_WinGetHandle(title, text)
    
def control_get_handle(title, control, text=u""):
    win_handle = win_get_handle(title, text)
    return autoit.AU3_ControlGetHandle(win_handle, control)

def win_active(title, text=u""):
    return autoit.AU3_WinActive(title, text)
    
def win_activate(title, text=u""):
    return autoit.AU3_WinActivate(title, text)
    
def send(text, mode=0):
    return autoit.AU3_Send(text, mode)
    
def mouse_move(x, y, speed=-1):
    return autoit.AU3_MouseMove(x, y, speed)

    
if __name__ == "__main__":
    mouse_move(100, 100)
    