## 	   Copyright (c) 2003 Henk Punt

## Permission is hereby granted, free of charge, to any person obtaining
## a copy of this software and associated documentation files (the
## "Software"), to deal in the Software without restriction, including
## without limitation the rights to use, copy, modify, merge, publish,
## distribute, sublicense, and/or sell copies of the Software, and to
## permit persons to whom the Software is furnished to do so, subject to
## the following conditions:

## The above copyright notice and this permission notice shall be
## included in all copies or substantial portions of the Software.

## THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
## EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
## MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
## NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
## LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
## OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
## WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE

from ctypes import *

#TODO auto ie/comctl detection
WIN32_IE = 0x0550

#TODO: auto unicode selection,
#if unicode:
#  CreateWindowEx = windll.user32.CreateWindowExW
#else:
#  CreateWindowEx = windll.user32.CreateWindowExA
#etc, etc


DWORD = c_ulong
HANDLE = c_ulong
UINT = c_uint
BOOL = c_int
HWND = HANDLE
HINSTANCE = HANDLE
HICON = HANDLE
HDC = HANDLE
HCURSOR = HANDLE
HBRUSH = HANDLE
HMENU = HANDLE
HBITMAP = HANDLE
ULONG_PTR = DWORD
INT = c_int
LPCTSTR = c_char_p
LPTSTR = c_char_p
WORD = c_ushort
LPARAM = c_ulong
WPARAM = c_uint
LPVOID = c_voidp
LONG = c_ulong
BYTE = c_byte
TCHAR = c_char_p
DWORD_PTR = c_ulong #TODO what is this exactly?
INT_PTR = c_ulong  #TODO what is this exactly?
COLORREF = c_ulong


WndProc = WINFUNCTYPE(c_int, HWND, UINT, WPARAM, LPARAM)

CBTProc = WINFUNCTYPE(c_int, c_int, c_int, c_int)
MessageProc = CBTProc

class WNDCLASSEX(Structure):
    _fields_ = [("cbSize", UINT),
                ("style",  UINT),
                ("lpfnWndProc", WndProc),
                ("cbClsExtra", INT),
                ("cbWndExtra", INT),
                ("hInstance", HINSTANCE),
                ("hIcon", HICON),
                ("hCursor", HCURSOR),
                ("hbrBackground", HBRUSH),
                ("lpszMenuName", LPCTSTR),
                ("lpszClassName", LPCTSTR),
                ("hIconSm", HICON)]

class POINT(Structure):
    _fields_ = [("x", LONG),
                ("y", LONG)]

    def __str__(self):
        return "POINT {x: %d, y: %d}" % (self.x, self.y)

class RECT(Structure):
    _fields_ = [("left", LONG),
                ("top", LONG),
                ("right", LONG),
                ("bottom", LONG)]

    def __str__(self):
        return "RECT {left: %d, top: %d, right: %d, bottom: %d}" % (self.left, self.top,
                                                                    self.right, self.bottom)

    def getHeight(self):
        return self.bottom - self.top

    height = property(getHeight, None, None, "")

    def getWidth(self):
        return self.right - self.left

    width = property(getWidth, None, None, "")

    def getSize(self):
        return self.width, self.height

    size = property(getSize, None, None, "")

##class MSG(Structure):
##    _fields_ = [("hWnd", HWND),
##                ("message", UINT),
##                ("wParam", WPARAM),
##                ("lParam", LPARAM),
##                ("time", DWORD),
##                ("pt", POINT)]

##    def __str__(self):
##        return "MSG {%d %d %d %d %d %s}" % (self.hWnd, self.message, self.wParam, self.lParam,
##                                            self.time, str(self.pt))

#Hack: we need to use the same MSG type as ctypes.com.ole uses!
from ctypes.wintypes import MSG

class ACCEL(Structure):
    _fields_ = [("fVirt", BYTE),
                ("key", WORD),
                ("cmd", WORD)]
    
class CREATESTRUCT(Structure):
    _fields_ = [("lpCreateParams", LPVOID),
                ("hInstance", HINSTANCE),
                ("hMenu", HMENU),
                ("hwndParent", HWND),
                ("cx", INT),
                ("cy", INT),
                ("x", INT),
                ("y", INT),
                ("style", LONG),
                ("lpszName", LPCTSTR),
                ("lpszClass", LPCTSTR),
                ("dwExStyle", DWORD)]



class NMHDR(Structure):
    _fields_ = [("hwndFrom", HWND),
                ("idFrom", UINT),
                ("code", UINT)]

class PAINTSTRUCT(Structure):
    _fields_ = [("hdc", HDC),
                ("fErase", BOOL),
                ("rcPaint", RECT),
                ("fRestore", BOOL),
                ("fIncUpdate", BOOL),
                ("rgbReserved", c_char * 32)]

    
class MENUITEMINFO(Structure):
    _fields_ = [("cbSize", UINT),
                ("fMask", UINT),
                ("fType", UINT),
                ("fState", UINT),                
                ("wID", UINT),
                ("hSubMenu", HMENU),
                ("hbmpChecked", HBITMAP),
                ("hbmpUnchecked", HBITMAP),
                ("dwItemData", ULONG_PTR),
                ("dwTypeData", LPTSTR),                
                ("cch", UINT),
                ("hbmpItem", HBITMAP)]

def LOWORD(dword):
    return dword & 0x0000ffff

def HIWORD(dword):
    return dword >> 16

TRUE = 1
FALSE = 0
NULL = 0

IDI_APPLICATION = 32512
IDC_ARROW = 32512
SW_SHOW = 5
SW_HIDE = 0

WM_DESTROY = 2
WM_SETREDRAW = 11
WM_PAINT = 15
WM_MOUSEMOVE = 512
WM_MOUSEHOVER = 0x2A1
WM_MOUSELEAVE = 0x2A3
WM_LBUTTONDOWN = 513
WM_LBUTTONUP = 514
WM_LBUTTONDBLCLK = 515
WM_KEYDOWN = 256
WM_KEYUP = 257
WM_KEYFIRST = 256
WM_KEYLAST = 264
WM_COMMAND = 273
WM_INITMENUPOPUP = 279
WM_SETFONT =48
WM_GETFONT =49
WM_SETCURSOR = 32
WM_CAPTURECHANGED = 533
WM_ERASEBKGND = 20
WM_MENUSELECT = 287
WM_CANCELMODE = 31
WM_NCCREATE = 129
WM_NCDESTROY = 130
WM_SIZE = 5
WM_NOTIFY = 78
WM_MOVE = 3
WM_USER = 1024
WM_SYSKEYDOWN = 260
WM_SYSKEYUP = 261

VK_DOWN = 40
VK_LEFT = 37
VK_RIGHT = 39

CS_HREDRAW = 2
CS_VREDRAW = 1
WHITE_BRUSH = 0

MIIM_STATE= 1
MIIM_ID= 2
MIIM_SUBMENU =4
MIIM_CHECKMARKS= 8
MIIM_TYPE= 16
MIIM_DATA= 32
MIIM_STRING= 64
MIIM_BITMAP= 128
MIIM_FTYPE =256

MFT_BITMAP= 4
MFT_MENUBARBREAK =32
MFT_MENUBREAK= 64
MFT_OWNERDRAW= 256
MFT_RADIOCHECK= 512
MFT_RIGHTJUSTIFY= 0x4000
MFT_SEPARATOR =0x800
MFT_RIGHTORDER= 0x2000L
MFT_STRING = 0

WS_BORDER	= 0x800000
WS_CAPTION	= 0xc00000
WS_CHILD	= 0x40000000
WS_CHILDWINDOW	= 0x40000000
WS_CLIPCHILDREN = 0x2000000
WS_CLIPSIBLINGS = 0x4000000
WS_DISABLED	= 0x8000000
WS_DLGFRAME	= 0x400000
WS_GROUP	= 0x20000
WS_HSCROLL	= 0x100000
WS_ICONIC	= 0x20000000
WS_MAXIMIZE	= 0x1000000
WS_MAXIMIZEBOX	= 0x10000
WS_MINIMIZE	= 0x20000000
WS_MINIMIZEBOX	= 0x20000
WS_OVERLAPPED	= 0
WS_OVERLAPPEDWINDOW = 0xcf0000
WS_POPUP	= 0x80000000
WS_POPUPWINDOW	= 0x80880000
WS_SIZEBOX	= 0x40000
WS_SYSMENU	= 0x80000
WS_TABSTOP	= 0x10000
WS_THICKFRAME	= 0x40000
WS_TILED	= 0
WS_TILEDWINDOW	= 0xcf0000
WS_VISIBLE	= 0x10000000
WS_VSCROLL	= 0x200000

WS_EX_TOOLWINDOW = 128
WS_EX_LEFT = 0
WS_EX_LTRREADING = 0
WS_EX_RIGHTSCROLLBAR = 0
WS_EX_WINDOWEDGE = 256
WS_EX_STATICEDGE = 0x20000
WS_EX_CLIENTEDGE = 512
WS_EX_OVERLAPPEDWINDOW   =     0x300
WS_EX_APPWINDOW    =   0x40000

MF_ENABLED    =0
MF_GRAYED     =1
MF_DISABLED   =2
MF_BITMAP     =4
MF_CHECKED    =8
MF_MENUBARBREAK= 32
MF_MENUBREAK  =64
MF_OWNERDRAW  =256
MF_POPUP      =16
MF_SEPARATOR  =0x800
MF_STRING     =0
MF_UNCHECKED  =0
MF_DEFAULT    =4096
MF_SYSMENU    =0x2000
MF_HELP       =0x4000
MF_END        =128
MF_RIGHTJUSTIFY=       0x4000
MF_MOUSESELECT =       0x8000
MF_INSERT= 0
MF_CHANGE= 128
MF_APPEND= 256
MF_DELETE= 512
MF_REMOVE= 4096
MF_USECHECKBITMAPS= 512
MF_UNHILITE= 0
MF_HILITE= 128
MF_BYCOMMAND=  0
MF_BYPOSITION= 1024
MF_UNCHECKED=  0
MF_HILITE =    128
MF_UNHILITE =  0
 

RB_SETBARINFO = WM_USER + 4
RB_GETBANDCOUNT = WM_USER +  12
RB_INSERTBANDA = WM_USER + 1
RB_INSERTBANDW = WM_USER + 10

RB_INSERTBAND = RB_INSERTBANDA

RBBIM_STYLE = 1
RBBIM_COLORS = 2
RBBIM_TEXT = 4
RBBIM_IMAGE = 8
RBBIM_CHILD = 16
RBBIM_CHILDSIZE = 32
RBBIM_SIZE = 64
RBBIM_BACKGROUND = 128
RBBIM_ID = 256
RBBIM_IDEALSIZE = 0x00000200

TPM_CENTERALIGN =4
TPM_LEFTALIGN =0
TPM_RIGHTALIGN= 8
TPM_LEFTBUTTON= 0
TPM_RIGHTBUTTON= 2
TPM_HORIZONTAL= 0
TPM_VERTICAL= 64
TPM_TOPALIGN= 0
TPM_VCENTERALIGN= 16
TPM_BOTTOMALIGN= 32
TPM_NONOTIFY= 128
TPM_RETURNCMD= 256

TBIF_TEXT = 0x00000002

DT_NOPREFIX   =      0x00000800
DT_HIDEPREFIX =      1048576

WH_CBT       =  5
WH_MSGFILTER =  (-1)

I_IMAGENONE = -2
TBSTATE_ENABLED = 4

BTNS_SHOWTEXT = 0x00000040
CW_USEDEFAULT = 0x80000000

COLOR_3DFACE = 15

BF_LEFT      = 1
BF_TOP       = 2
BF_RIGHT     = 4
BF_BOTTOM    = 8

BDR_RAISEDOUTER =      1
BDR_SUNKENOUTER =      2
BDR_RAISEDINNER =      4
BDR_SUNKENINNER =      8
BDR_OUTER    = 3
BDR_INNER    = 0xc
BDR_RAISED   = 5
BDR_SUNKEN   = 10

EDGE_RAISED  = (BDR_RAISEDOUTER|BDR_RAISEDINNER)
EDGE_SUNKEN  = (BDR_SUNKENOUTER|BDR_SUNKENINNER)
EDGE_ETCHED  = (BDR_SUNKENOUTER|BDR_RAISEDINNER)
EDGE_BUMP    = (BDR_RAISEDOUTER|BDR_SUNKENINNER)

IDC_SIZEWE = 32644

TCIF_TEXT    =1
TCIF_IMAGE   =2
TCIF_RTLREADING=      4
TCIF_PARAM  = 8


TCS_MULTILINE = 512

MK_LBUTTON    = 1
MK_RBUTTON    = 2
MK_SHIFT      = 4
MK_CONTROL    = 8
MK_MBUTTON    = 16

ILC_COLOR = 0
ILC_COLOR4 = 4
ILC_COLOR8 = 8
ILC_COLOR16 = 16
ILC_COLOR24 = 24
ILC_COLOR32 = 32
ILC_COLORDDB = 254
ILC_MASK = 1
ILC_PALETTE = 2048

IMAGE_BITMAP = 0
IMAGE_ICON = 1

LR_LOADFROMFILE = 16
LR_VGACOLOR = 0x0080
LR_LOADMAP3DCOLORS = 4096
LR_LOADTRANSPARENT = 32

LVSIL_NORMAL = 0
LVSIL_SMALL  = 1
LVSIL_STATE  = 2

TVSIL_NORMAL = 0
TVSIL_STATE  = 2

SRCCOPY = 0xCC0020

GWL_WNDPROC = -4

HWND_BOTTOM = 1

SWP_DRAWFRAME= 32
SWP_FRAMECHANGED= 32
SWP_HIDEWINDOW= 128
SWP_NOACTIVATE= 16
SWP_NOCOPYBITS= 256
SWP_NOMOVE= 2
SWP_NOSIZE= 1
SWP_NOREDRAW= 8
SWP_NOZORDER= 4
SWP_SHOWWINDOW= 64
SWP_NOOWNERZORDER =512
SWP_NOREPOSITION= 512
SWP_NOSENDCHANGING= 1024
SWP_DEFERERASE= 8192
SWP_ASYNCWINDOWPOS=  16384

DCX_WINDOW = 1
DCX_CACHE = 2
DCX_PARENTCLIP = 32
DCX_CLIPSIBLINGS= 16
DCX_CLIPCHILDREN= 8
DCX_NORESETATTRS= 4
DCX_LOCKWINDOWUPDATE= 0x400
DCX_EXCLUDERGN= 64
DCX_INTERSECTRGN =128
DCX_VALIDATE= 0x200000

GCL_STYLE = -26

def GET_XY_LPARAM(lParam):
    x = LOWORD(lParam)
    if x > 32768:
        x = x - 65536
    y = HIWORD(lParam)
    return x, y 

def GET_POINT_LPARAM(lParam):
    x, y = GET_XY_LPARAM(lParam)
    return POINT(x, y)

FCONTROL = 8
FVIRTKEY = 1

def ValidHandle(value):
    if value == 0:
        raise WinError()
    else:
        return value


GetModuleHandle = windll.kernel32.GetModuleHandleA
PostQuitMessage= windll.user32.PostQuitMessage
DefWindowProc = windll.user32.DefWindowProcA
CallWindowProc = windll.user32.CallWindowProcA
GetDCEx = windll.user32.GetDCEx
ReleaseDC = windll.user32.ReleaseDC
LoadIcon = windll.user32.LoadIconA
DestroyIcon = windll.user32.DestroyIcon
LoadCursor = windll.user32.LoadCursorA
LoadCursor.restype = ValidHandle
LoadImage = windll.user32.LoadImageA
LoadImage.restype = ValidHandle

RegisterClassEx = windll.user32.RegisterClassExA
SetCursor = windll.user32.SetCursor

CreateWindowEx = windll.user32.CreateWindowExA
CreateWindowEx.restype = ValidHandle

ShowWindow = windll.user32.ShowWindow
UpdateWindow = windll.user32.UpdateWindow
GetMessage = windll.user32.GetMessageA
TranslateMessage = windll.user32.TranslateMessage
DispatchMessage = windll.user32.DispatchMessageA
GetWindowRect = windll.user32.GetWindowRect
MoveWindow = windll.user32.MoveWindow
DestroyWindow = windll.user32.DestroyWindow
CreateMenu = windll.user32.CreateMenu
CreatePopupMenu = windll.user32.CreatePopupMenu
DestroyMenu = windll.user32.DestroyMenu
AppendMenu = windll.user32.AppendMenuA
EnableMenuItem = windll.user32.EnableMenuItem
SendMessage = windll.user32.SendMessageA
PostMessage = windll.user32.PostMessageA
GetClientRect = windll.user32.GetClientRect
GetWindowRect = windll.user32.GetWindowRect
IsDialogMessage = windll.user32.IsDialogMessage
RegisterWindowMessage = windll.user32.RegisterWindowMessageA
GetParent = windll.user32.GetParent
SetWindowLong = windll.user32.SetWindowLongA
SetClassLong = windll.user32.SetClassLongA
GetClassLong = windll.user32.GetClassLongA
SetWindowPos = windll.user32.SetWindowPos
InvalidateRect = windll.user32.InvalidateRect
BeginPaint = windll.user32.BeginPaint
EndPaint = windll.user32.EndPaint
SetCapture = windll.user32.SetCapture
GetCapture = windll.user32.GetCapture
ReleaseCapture = windll.user32.ReleaseCapture
ScreenToClient = windll.user32.ScreenToClient
ClientToScreen = windll.user32.ClientToScreen

GetMessagePos = windll.user32.GetMessagePos
BeginDeferWindowPos = windll.user32.BeginDeferWindowPos
DeferWindowPos = windll.user32.DeferWindowPos
EndDeferWindowPos = windll.user32.EndDeferWindowPos
CreateAcceleratorTable = windll.user32.CreateAcceleratorTableA
DestroyAcceleratorTable = windll.user32.DestroyAcceleratorTable
TranslateAccelerator = windll.user32.TranslateAccelerator


ExpandEnvironmentStrings = windll.kernel32.ExpandEnvironmentStringsA
GetModuleHandle = windll.kernel32.GetModuleHandleA
GetModuleHandle.restype = ValidHandle
LoadLibrary = windll.kernel32.LoadLibraryA
LoadLibrary.restype = ValidHandle

TrackPopupMenuEx = windll.user32.TrackPopupMenuEx

GetMenuItemCount = windll.user32.GetMenuItemCount
GetMenuItemInfo = windll.user32.GetMenuItemInfoA
GetMenuItemInfo.restype = ValidHandle
GetSubMenu = windll.user32.GetSubMenu

SetWindowsHookEx = windll.user32.SetWindowsHookExA
CallNextHookEx = windll.user32.CallNextHookEx
UnhookWindowsHookEx = windll.user32.UnhookWindowsHookEx

GetCurrentThreadId = windll.kernel32.GetCurrentThreadId

def ErrorIfZero(handle):
    if handle == 0:
        raise WinError
    else:
        return handle

CreateWindowEx.argtypes = [c_int, c_char_p, c_char_p, c_int, c_int, c_int, c_int, c_int, c_int, c_int, c_int, c_int]
CreateWindowEx.restype = ErrorIfZero

