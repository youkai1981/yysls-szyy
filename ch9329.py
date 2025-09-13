import serial
import time
from enum import IntFlag
import threading


class CH9329:
    HEAD = [0x57, 0xAB]
    ADDR = 0x00

    CMD_GET_INFO = 0x01
    CMD_SEND_KB_GENERAL_DATA = 0x02
    CMD_SEND_KB_MEDIA_DATA = 0x03
    CMD_SEND_MS_ABS_DATA = 0x04
    CMD_SEND_MS_REL_DATA = 0x05
    CMD_SEND_MY_HID_DATA = 0x06
    CMD_GET_PARA_CFG = 0x08
    CMD_SET_PARA_CFG = 0x09
    CMD_RESET = 0x0F

    # ========== CH9329 键码表（部分常用键，完整可继续补充） ==========
    KEYCODES = {
        "A": 0x04, "B": 0x05, "C": 0x06, "D": 0x07, "E": 0x08, "F": 0x09,
        "G": 0x0A, "H": 0x0B, "I": 0x0C, "J": 0x0D, "K": 0x0E, "L": 0x0F,
        "M": 0x10, "N": 0x11, "O": 0x12, "P": 0x13, "Q": 0x14, "R": 0x15,
        "S": 0x16, "T": 0x17, "U": 0x18, "V": 0x19, "W": 0x1A, "X": 0x1B,
        "Y": 0x1C, "Z": 0x1D,
        "1": 0x1E, "2": 0x1F, "3": 0x20, "4": 0x21, "5": 0x22,
        "6": 0x23, "7": 0x24, "8": 0x25, "9": 0x26, "0": 0x27,
        "ENTER": 0x28, "ESC": 0x29, "BACKSPACE": 0x2A, "TAB": 0x2B,
        "SPACE": 0x2C, "-": 0x2D, "=": 0x2E, "[": 0x2F, "]": 0x30,
        "\\": 0x31, ";": 0x33, "'": 0x34, "`": 0x35, ",": 0x36,
        ".": 0x37, "/": 0x38,
        "CAPSLOCK": 0x39,
        "F1": 0x3A, "F2": 0x3B, "F3": 0x3C, "F4": 0x3D, "F5": 0x3E,
        "F6": 0x3F, "F7": 0x40, "F8": 0x41, "F9": 0x42, "F10": 0x43,
        "F11": 0x44, "F12": 0x45,
        "LEFT": 0x50, "RIGHT": 0x4F, "UP": 0x52, "DOWN": 0x51,
        "INSERT": 0x49, "DELETE": 0x4C, "HOME": 0x4A, "END": 0x4D,
        "PAGEUP": 0x4B, "PAGEDOWN": 0x4E,
    }

    # ================== 修饰键枚举 ==================
    class Modifiers(IntFlag):
        CTRL_L  = 0x01
        SHIFT_L = 0x02
        ALT_L   = 0x04
        WIN_L   = 0x08
        CTRL_R  = 0x10
        SHIFT_R = 0x20
        ALT_R   = 0x40
        WIN_R   = 0x80

    def __init__(self, port, baudrate=9600, timeout=0.5):
        self.ser = serial.Serial(port=port, baudrate=baudrate, timeout=timeout)

    def _checksum(self, data):
        return sum(data) & 0xFF

    def _send_cmd_no_resp(self, cmd, data=[]):
        packet = self.HEAD + [self.ADDR, cmd, len(data)] + data
        packet.append(self._checksum(packet))
        self.ser.write(bytearray(packet))

    def _send_cmd_with_resp(self, cmd, data=[], resp_len=64):
        packet = self.HEAD + [self.ADDR, cmd, len(data)] + data
        packet.append(self._checksum(packet))
        self.ser.write(bytearray(packet))
        return self.ser.read(resp_len)

    def _keycode(self, key):
        if isinstance(key, str):
            key = key.upper()
            return self.KEYCODES.get(key, 0x00)
        return key

    # ================= 键盘操作 =================
    def key_press(self, key, modifiers=0):
        keycode = self._keycode(key)
        if isinstance(modifiers, self.Modifiers):
            modifiers = modifiers.value
        data = [modifiers, 0x00] + [keycode] + [0x00] * 5
        return self._send_cmd_no_resp(self.CMD_SEND_KB_GENERAL_DATA, data)

    def key_release(self, key=None, modifiers=0):
        """
        只释放指定按键。如果key为None，则释放全部按键（兼容旧用法）。
        """
        # if key is None:
        #     data = [0x00] * 8
        # else:
        #     keycode = self._keycode(key)
        #     if isinstance(modifiers, self.Modifiers):
        #         modifiers = modifiers.value
        #     data = [modifiers, 0x00] + [keycode] + [0x00] * 5
        data = [0x00] * 8
        return self._send_cmd_no_resp(self.CMD_SEND_KB_GENERAL_DATA, data)

    def key_down(self, key, modifiers=0, delay=0.01):
        def click_task():
            self.key_press(key, modifiers)
        threading.Thread(target=click_task, daemon=True).start()
        time.sleep(delay)

    def key_up(self, key, modifiers=0, delay=0.01):
        def click_task():
            self.key_release(key, modifiers)
        threading.Thread(target=click_task, daemon=True).start()
        time.sleep(delay)


    def key_click(self, key, modifiers=0, delay=0.01):
        def click_task():
            self.key_press(key, modifiers)
            time.sleep(0.1)
            self.key_release(key, modifiers)
        threading.Thread(target=click_task, daemon=True).start()
        time.sleep(delay)

    def key_combo(self, keys, modifiers=0):
        keycodes = [self._keycode(k) for k in keys]
        if isinstance(modifiers, self.Modifiers):
            modifiers = modifiers.value
        data = [modifiers, 0x00] + keycodes[:6]
        data += [0x00] * (8 - len(data))
        return self._send_cmd_no_resp(self.CMD_SEND_KB_GENERAL_DATA, data)

    # ================= 鼠标相对移动 =================
    def mouse_move_rel(self, dx=0, dy=0, buttons=0, wheel=0):
        data = [0x01, buttons & 0x07, dx & 0xFF, dy & 0xFF, wheel & 0xFF]
        return self._send_cmd_no_resp(self.CMD_SEND_MS_REL_DATA, data)

    # ================= 鼠标绝对移动 =================
    def mouse_move_abs(self, x, y, screen_width=1920, screen_height=1080, buttons=0, wheel=0):
        x_val = (4096 * x) // screen_width
        y_val = (4096 * y) // screen_height
        data = [
            0x02,
            buttons & 0x07,
            x_val & 0xFF, (x_val >> 8) & 0xFF,
            y_val & 0xFF, (y_val >> 8) & 0xFF,
            wheel & 0xFF
        ]
        return self._send_cmd_no_resp(self.CMD_SEND_MS_ABS_DATA, data)

    # ================= 其他功能 =================
    def send_media_key(self, report_id, key_val):
        data = [report_id, key_val]
        return self._send_cmd_no_resp(self.CMD_SEND_KB_MEDIA_DATA, data)

    def send_custom_hid(self, hid_data):
        return self._send_cmd_no_resp(self.CMD_SEND_MY_HID_DATA, hid_data)

    def get_info(self):
        raw = self._send_cmd_with_resp(self.CMD_GET_INFO)
        if not raw or len(raw) < 14:
            return None

        data = raw[5:13]
        version = f"V{(data[0] >> 4)}.{(data[0] & 0x0F)}"
        usb_status = "Connected" if data[1] == 0x01 else "Disconnected"
        leds = {
            "NUM_LOCK": bool(data[2] & 0x01),
            "CAPS_LOCK": bool(data[2] & 0x02),
            "SCROLL_LOCK": bool(data[2] & 0x04),
        }
        return {
            "version_raw": data[0],
            "version": version,
            "usb_status": usb_status,
            "led_status": leds,
            "reserved": data[3:]
        }

    def reset(self):
        return self._send_cmd_with_resp(self.CMD_RESET)

    def close(self):
        if self.ser.is_open:
            self.ser.close()

