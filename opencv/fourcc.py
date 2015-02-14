# -*- coding: utf-8 -*-
"""
显示所选中的编码的FOURCC
"""
import ctypes
from ctypes import Structure, POINTER, c_int, c_void_p, c_char, pointer
from ctypes.wintypes import LPCSTR, WORD, DWORD, LONG, LPVOID, HWND, UINT

OF_WRITE = 0x00000001
OF_CREATE = 0x00001000

def fourcc(s):
    return sum(256**i*ord(c) for i, c in enumerate(s))
    
def unfourcc(v):
    return "".join(chr(v>>(i*8)&0xff) for i in xrange(4))

class RECT(Structure):
    _fields_ = zip(["left","top","right","bottom"], [LONG]*4)

class AVICOMPRESSOPTIONS(Structure):
    _fields_ = [
        ("fccType", DWORD),
        ("fccHandler", DWORD),
        ("dwKeyFrameEvery", DWORD),
        ("dwQuality", DWORD),
        ("dwBytesPerSecond", DWORD),
        ("dwFlags", DWORD),
        ("lpFormat", LPVOID),
        ("cbFormat", DWORD),
        ("lpParams", LPVOID),
        ("cbParams", DWORD),
        ("dwInterLeaveEvery", DWORD)
   ]
   
class AVISTREAMINFOA(Structure):
    _fields_ = [
        ("fccType", DWORD),
        ("fccHandler", DWORD),
        ("dwFlags", DWORD),
        ("dwCaps", DWORD),
        ("wPriority", WORD),
        ("wLanguage", WORD),
        ("dwScale", DWORD),
        ("dwRate", DWORD),
        ("dwStart", DWORD),
        ("dwLength", DWORD),
        ("dwInitialFrames", DWORD),
        ("dwSuggestedBufferSize", DWORD),
        ("dwQuality", DWORD),
        ("dwSampleSize", DWORD),
        ("rcFrame", RECT),
        ("dwEditCount", DWORD),
        ("dwFormatChangeCount", DWORD),
        ("szName", c_char*64)
        ]
        
avi = ctypes.windll.LoadLibrary("avifil32.dll")

avi.AVIFileOpenA.argtypes = [POINTER(c_int), LPCSTR, c_int, c_int]
avi.AVIFileOpenA.restype = c_int

avi.AVIFileCreateStreamA.argtypes = [c_int, POINTER(c_void_p), POINTER(AVISTREAMINFOA)]
avi.AVIFileCreateStreamA.restype = c_int

avi.AVISaveOptions.argtypes = [HWND, UINT, c_int, POINTER(c_void_p), c_void_p]
avi.AVISaveOptions.restype = c_int

avi.AVIFileRelease.argtypes = [c_int]
avi.AVIFileRelease.restype = c_int

avi.AVIStreamRelease.argtypes = [c_void_p]
avi.AVIStreamRelease.restype = c_int

if __name__ == "__main__":
    avifile = c_int(0)
    avi.AVIFileInit()
    avi.AVIFileOpenA(pointer(avifile), LPCSTR("__tmp__.avi"), OF_WRITE|OF_CREATE, 0)

    aviinfo = AVISTREAMINFOA()
    aviinfo.fccType = fourcc("vids")

    stream = c_void_p(0)
    avi.AVIFileCreateStreamA(avifile, pointer(stream), pointer(aviinfo))

    opt = AVICOMPRESSOPTIONS()
    popt = ctypes.pointer(opt)
    opt.fccType = fourcc("vids")
    avi.AVISaveOptions(0, 0, 1, pointer(stream), pointer(ctypes.pointer(opt)))
    print unfourcc(opt.fccHandler)
    
    avi.AVIStreamRelease(stream)
    avi.AVIFileRelease(avifile)
    avi.AVIFileExit()
    
    import os
    os.remove("__tmp__.avi")
    
    import time
    time.sleep(2.0)