"""Small Windows input adapter. No third-party keyboard hook required."""
import ctypes
from ctypes import wintypes


class WindowsInput:
    def __init__(self):
        self.api = ctypes.WinDLL('user32', use_last_error=True)
        self.api.GetForegroundWindow.restype = wintypes.HWND
        self.api.GetWindowTextW.argtypes = [wintypes.HWND, wintypes.LPWSTR, ctypes.c_int]
        self.api.GetWindowTextLengthW.argtypes = [wintypes.HWND]
        self.held = False

    def focused(self, title):
        handle = self.api.GetForegroundWindow()
        text = ctypes.create_unicode_buffer(self.api.GetWindowTextLengthW(handle) + 1)
        self.api.GetWindowTextW(handle, text, len(text))
        return title.casefold() in text.value.casefold()

    def hold(self, value):
        if value != self.held:
            self.api.mouse_event(0x0002 if value else 0x0004, 0, 0, 0, 0)
            self.held = value

    def key(self, value):
        code = ord(value.upper())
        self.api.keybd_event(code, 0, 0, 0)
        self.api.keybd_event(code, 0, 2, 0)

    def move(self, point):
        self.api.SetCursorPos(*point)

    def position(self):
        point = wintypes.POINT()
        self.api.GetCursorPos(ctypes.byref(point))
        return [point.x, point.y]

    def down(self, code):
        return bool(self.api.GetAsyncKeyState(code) & 0x8000)

    def make_clickthrough(self, window):
        self.api.GetAncestor.argtypes = [wintypes.HWND, wintypes.UINT]
        self.api.GetAncestor.restype = wintypes.HWND
        hwnd = self.api.GetAncestor(window.winfo_id(), 2)
        get_style = self.api.GetWindowLongPtrW
        set_style = self.api.SetWindowLongPtrW
        get_style.argtypes = [wintypes.HWND, ctypes.c_int]
        get_style.restype = ctypes.c_ssize_t
        set_style.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_ssize_t]
        set_style.restype = ctypes.c_ssize_t
        # WS_EX_TRANSPARENT | LAYERED | NOACTIVATE | TOOLWINDOW
        set_style(hwnd, -20, get_style(hwnd, -20) | 0x20 | 0x80000 | 0x08000000 | 0x80)

    def place_overlay(self, window, x, y, width, height):
        # SetWindowPos handles negative virtual-desktop coordinates literally.
        hwnd = self.api.GetAncestor(window.winfo_id(), 2)
        self.api.SetWindowPos.argtypes = [wintypes.HWND, wintypes.HWND,
                                         ctypes.c_int, ctypes.c_int, ctypes.c_int,
                                         ctypes.c_int, wintypes.UINT]
        self.api.SetWindowPos(hwnd, -1, x, y, width, height, 0x0010 | 0x0040)
