from __future__ import annotations

import ctypes
from ctypes import wintypes
from dataclasses import dataclass
from pathlib import Path


# Win32 constants
PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
MAX_PATH = 260


GetForegroundWindow = ctypes.windll.user32.GetForegroundWindow
GetWindowThreadProcessId = ctypes.windll.user32.GetWindowThreadProcessId
GetWindowTextLengthW = ctypes.windll.user32.GetWindowTextLengthW
GetWindowTextW = ctypes.windll.user32.GetWindowTextW
OpenProcess = ctypes.windll.kernel32.OpenProcess
CloseHandle = ctypes.windll.kernel32.CloseHandle
QueryFullProcessImageNameW = ctypes.windll.kernel32.QueryFullProcessImageNameW


@dataclass
class WindowInfo:
    process_name: str
    process_path: Path
    window_title: str


def _get_window_title(hwnd: int) -> str:
    length = GetWindowTextLengthW(hwnd)
    if length == 0:
        return ""
    buffer = ctypes.create_unicode_buffer(length + 1)
    GetWindowTextW(hwnd, buffer, length + 1)
    return buffer.value


def _get_process_path(pid: int) -> Path:
    handle = OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, pid)
    if not handle:
        return Path("")
    try:
        buf_len = wintypes.DWORD(MAX_PATH)
        buffer = ctypes.create_unicode_buffer(MAX_PATH)
        if QueryFullProcessImageNameW(handle, 0, buffer, ctypes.byref(buf_len)):
            return Path(buffer.value)
        return Path("")
    finally:
        CloseHandle(handle)


def get_foreground_window_info() -> WindowInfo | None:
    hwnd = GetForegroundWindow()
    if not hwnd:
        return None

    pid = wintypes.DWORD()
    GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
    if not pid.value:
        return None

    process_path = _get_process_path(pid.value)
    process_name = process_path.name.lower() if process_path else ""
    window_title = _get_window_title(hwnd)
    return WindowInfo(process_name=process_name, process_path=process_path, window_title=window_title)
