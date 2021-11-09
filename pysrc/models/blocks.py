import html
import itertools
import string
from typing import Literal

from pysrc.models.block_bases import *


class EmptyBlock(BlockBase):
    """ 空積木 """

    def ahkscr(self) -> Literal['']:
        return ''


class TextBlock(StringBlockBase, BuildInBlockBase):
    """ 文字積木 """
    arg_dicts = {
        'TEXT': {
            'type': 'field_input',
        },
    }

    def ahkscr(self) -> str:
        return f'"{self.TEXT}"'


class MathNumberBlock(NumberBlockBase, BuildInBlockBase):
    """ 數字積木 """
    arg_dicts = {
        'NUM': {
            'type': 'field_input',
        },
    }

    def ahkscr(self) -> str:
        return str(self.NUM)


class MsgboxBlock(ActionBlockBase):
    """ 跳出訊息積木 """
    template = '跳出訊息 {TEXT}'
    colour = BlockBase.Colour.String
    arg_dicts = {
        'TEXT': {
            'type': 'input_value',
            'check': ['String', 'Number'],  # .## add Boolean or more
        },
    }

    def ahkscr(self) -> str:
        return f"Msgbox % {self.TEXT.ahkscr() or '\"\"'}"


class NormalKeyBlock(ObjectBlockBase):
    """ 普通按鍵積木 """
    template = '{KEY}'
    colour = BlockBase.Colour.hotkey
    arg_dicts = {
        'KEY': {
            'type': 'field_dropdown',
            "options": [
                # A-Z 英文按鍵
                [option_name, option_value]
                for (option_name, option_value) in zip(
                    string.ascii_uppercase,
                    string.ascii_lowercase,
                )
            ] + [
                # 其他按鍵 #.## 滑鼠中文名稱要可以被替換
                ["滑鼠左鍵", "LButton"],
                ["滑鼠右鍵", "RButton"],
                ["滑鼠中鍵", "MButton"],
                ["滑鼠上滾", "WheelUp"],
                ["滑鼠下滾", "WheelDown"],
                ["↑", "Up"],
                ["↓", "Down"],
                ["←", "Left"],
                ["→", "Right"],
                ["F1", "F1"],
                ["F2", "F2"],
                ["F3", "F3"],
                ["F4", "F4"],
                ["F5", "F5"],
                ["F6", "F6"],
                ["F7", "F7"],
                ["F8", "F8"],
                ["F9", "F9"],
                ["F10", "F10"],
                ["F11", "F11"],
                ["F12", "F12"],
                ["` (～)", "`"],
                ["0 (）)", "0"],
                ["1 (！)", "1"],
                ["2 (＠)", "2"],
                ["3 (＃)", "3"],
                ["4 (＄)", "4"],
                ["5 (％)", "5"],
                ["6 (︿)", "6"],
                ["7 (＆)", "7"],
                ["8 (＊)", "8"],
                ["9 (（)", "9"],
                ["－　(＿)", "-"],
                ["＝　(＋)", "="],
                ["［　(｛)", "["],
                ["］　(｝)", "]"],
                ["＼　(｜)", "\\"],
                ["；　(：)", "`;"],
                ["　’　(＂)", "'"],
                ["，　(＜)", "`,"],
                ["．　(＞)", "."],
                ["／　(？)", "/"],
                ["Numpad0", "Numpad0"],
                ["Numpad1", "Numpad1"],
                ["Numpad2", "Numpad2"],
                ["Numpad3", "Numpad3"],
                ["Numpad4", "Numpad4"],
                ["Numpad5", "Numpad5"],
                ["Numpad6", "Numpad6"],
                ["Numpad7", "Numpad7"],
                ["Numpad8", "Numpad8"],
                ["Numpad9", "Numpad9"],
                ["Numpad.", "NumpadDot"],
                ["Numpad/", "NumpadDiv"],
                ["Numpad*", "NumpadMult"],
                ["Numpad-", "NumpadSub"],
                ["Numpad+", "NumpadAdd"],
                ["NumpadEnter", "NumpadEnter"],
                ["NumLock", "NumLock"],
                ["Ctrl", "Ctrl"],
                ["Shift", "Shift"],
                ["Alt", "Alt"],
                ["Win", "Win"],
                ["LCtrl", "LCtrl"],
                ["LShift", "LShift"],
                ["LAlt", "LAlt"],
                ["LWin", "LWin"],
                ["RCtrl", "RCtrl"],
                ["RShift", "RShift"],
                ["RAlt", "RAlt"],
                ["RWin", "RWin"],
                ["Enter", "Enter"],
                ["Space", "Space"],
                ["Tab", "Tab"],
                ["CapsLock", "CapsLock"],
                ["Esc", "Esc"],
                ["Backspace", "Backspace"],
                ["Delete", "Delete"],
                ["Home", "Home"],
                ["End", "End"],
                ["PgUp", "PgUp"],
                ["PgDn", "PgDn"],
                ["Insert", "Insert"],
                ["PrintScreen", "PrintScreen"],
                ["AppsKey", "AppsKey"],
                ["ScrollLock", "ScrollLock"],
                ["Pause", "Pause"],
            ],
        },
    }
    register_dict = {
        "output": "normal_key",
    }

    def ahkscr(self) -> str:
        return f"{self.KEY}"


class HotKeyBlock(ObjectBlockBase):
    """ 熱鍵積木
    指 Ctrl、Shift、Alt、Win 這些可長押的輔助型的按鍵
    """
    template = '{KEY_A}+{KEY_B}'
    colour = BlockBase.Colour.hotkey
    arg_dicts = {
        'KEY_A': {
            'type': 'field_dropdown',
            "options": [
                [
                    left_or_right+key_name,
                    (left_or_right+key_name).replace(
                        'Ctrl', '^'
                    ).replace(
                        'Shift', '+'
                    ).replace(
                        'Alt', '!'
                    ).replace(
                        'Win', '#'
                    ).replace(
                        'L', '<'
                    ).replace(
                        'R', '>'
                    )
                ]
                for left_or_right, key_name in itertools.product(
                    ['', 'L', 'R'],
                    ['Ctrl', 'Shift', 'Alt', 'Win'],
                )
            ]
        },
        'KEY_B': {
            'type': 'input_value',
            'check': ["hot_key", "normal_key", "special_key"]
        },
    }
    register_dict = {
        "output": "hot_key",
    }

    def ahkscr(self) -> str:
        return f"{html.unescape(self.KEY_A)}{self.KEY_B.ahkscr()}"


class ShortCutBlock(BlockBase):
    """ 快捷鍵積木 """
    template = '當按下{KEY}執行{DO}'
    colour = BlockBase.Colour.hotkey
    arg_dicts = {
        'KEY': {
            'type': 'input_value',
            'check': ["normal_key", "hot_key", "special_key"],
        },
        'DO': {
            'type': 'input_statement',
        }
    }

    def ahkscr(self) -> str:
        TAB4_INDENT: str = '    '
        do_ahkscr_list = [do_block.ahkscr() for do_block in self.DO]
        # 根據執行積木數量，決定是否需要換行(縮排)，並於結尾加上Return
        if len(do_ahkscr_list) == 1:
            do_ahkscr = do_ahkscr_list[0]
        else:
            do_ahkscr = f"\n{TAB4_INDENT}" + \
                f"\n{TAB4_INDENT}".join(do_ahkscr_list + ["Return"])
        return f"{self.KEY.ahkscr()}:: {do_ahkscr}"
