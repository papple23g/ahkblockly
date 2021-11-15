import html
import itertools
import string
from typing import Literal

from pysrc.models.block_bases import *


class EmptyBlock(BlockBase):
    """ 空積木 """

    def ahkscr(self, *args, **kwargs) -> Literal['']:
        return ''


class TextBlock(StringBlockBase, BuildInBlockBase):
    """ 文字積木 """
    arg_dicts = {
        'TEXT': {
            'type': 'field_input',
        },
    }

    def ahkscr(self, with_quotes: bool = True) -> str:
        if with_quotes:
            return f'"{self.TEXT}"'
        return self.TEXT


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
            # 'check': ['String', 'Number'],
        },
    }

    def ahkscr(self) -> str:
        return f"Msgbox % {self.TEXT.ahkscr() or '\"\"'}"


class NormalKeyBlock(NormalKeyBlockBase):
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

    def ahkscr(self, to_be_send: bool = False) -> str:
        """ 普通按鍵積木的 ahk script 型態

        Args:
            to_be_send (bool, optional): 該按鍵是否作為被發出的按鍵?(否則作為快捷鍵/熱鍵使用). Defaults to False.

        Returns:
            str
        """
        if not to_be_send:
            return f"{self.KEY}"
        return f"{{{self.KEY}}}"


class HotKeyBlock(HotKeyBlockBase):
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

    def ahkscr(self, to_be_send: bool = False) -> str:
        return f"{html.unescape(self.KEY_A)}{self.KEY_B.ahkscr(to_be_send=to_be_send)}"


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
        do_block_ahksrc_line_str = [
            do_block_ahksrc_line_str
            for do_block in self.DO
            for do_block_ahksrc_line_str in do_block.ahkscr().splitlines()
        ]
        # 根據執行積木的ahk指令行數，決定是否需要換行(縮排)，並於結尾加上Return
        if len(do_block_ahksrc_line_str) == 1:
            do_ahkscr = do_block_ahksrc_line_str[0]
        else:
            do_ahkscr = f"\n{TAB4_INDENT}" + \
                f"\n{TAB4_INDENT}".join(do_block_ahksrc_line_str + ["Return"])
        return ";"*(do_ahkscr == "") + f"{self.KEY.ahkscr()}:: {do_ahkscr}"


class OptionFileBlock(FilepathBlockBase):
    """ 選項檔案積木 """
    template = '{OBJ}'
    colour = BlockBase.Colour.filepath
    arg_dicts = {
        'OBJ': {
            'type': 'field_dropdown',
            "options": [
                ['記事本', '"Notepad.exe"'],
                ['小畫家', '"mspaint.exe"'],
                ["小算盤", 'windir . "\system32\calc.exe"'],
                ["剪取工具", ' windir . "\system32\SnippingTool.exe"'],
                ["命令提示字元", ' windir . "\system32\cmd.exe"'],
                ["AHK腳本", 'A_ScriptFullPath'],
                ["AHK主程式", 'A_AhkPath'],
            ],
        },
    }

    def ahkscr(self) -> str:
        return self.OBJ


class OptionDirBlock(DirpathBlockBase):
    """ 選項目錄積木 """
    template = '{OBJ}'
    colour = BlockBase.Colour.dirpath
    arg_dicts = {
        'OBJ': {
            'type': 'field_dropdown',
            "options": [
                ["桌面", "A_Desktop"],
                ["我的文件", "A_MyDocuments"],
                ["啟動資料夾", "A_Startup"],
                ["臨時資料夾", "A_Temp"],
                ["Windows資料夾", "A_WinDir"],
                ["AHK腳本目錄", "A_ScriptDir"],
            ],
        },
    }

    def ahkscr(self) -> str:
        return self.OBJ


class OptionLinkBlock(LinkBlockBase):
    """ 選項目錄積木 """
    template = '{OBJ}'
    colour = BlockBase.Colour.link
    arg_dicts = {
        'OBJ': {
            'type': 'field_dropdown',
            "options": [
                ["Google網頁", f'"https://www.google.com"'],
                ["Youtube網頁", f'"https://www.youtube.com"'],
                ["Facebook網頁", f'"https://www.facebook.com"'],
                ["百度搜尋", f'"https://www.baidu.com/"'],
                ["Wikipedia網頁", f'"https://zh.wikipedia.org"'],
                ["PChome網頁", f'"https://www.pchome.com.tw"'],
                ["Yahoo網頁", f'"https://yahoo.com"'],
                ["Google地圖", f'"https://www.google.com.tw/maps"'],
                ["AHK官網", f'"https://www.autohotkey.com"'],
                ["AHK積木網頁", f'"https://papple23g-ahkcompiler.herokuapp.com/ahkblockly"'],
            ],
        },
    }

    def ahkscr(self) -> str:
        return self.OBJ


class FilepathBlock(FilepathBlockBase):
    """ 檔案積木 """
    template = '檔案路徑{PATH}'
    colour = BlockBase.Colour.filepath
    arg_dicts = {
        'PATH': {
            'type': 'field_input',
        },
    }

    def ahkscr(self) -> str:
        return f'"{self.PATH.strip()}"' if self.PATH.strip() else ''


class DirpathBlock(DirpathBlockBase):
    """ 目錄積木 """
    template = '目錄路徑{PATH}'
    colour = BlockBase.Colour.dirpath
    arg_dicts = {
        'PATH': {
            'type': 'field_input',
        },
    }

    def ahkscr(self) -> str:
        return f'"{self.PATH.strip()}"' if self.PATH.strip() else ''


class LinkBlock(LinkBlockBase):
    """ 網頁連結積木 """
    template = '網頁{URL}'
    colour = BlockBase.Colour.link
    arg_dicts = {
        'URL': {
            'type': 'field_input',
        },
    }

    def ahkscr(self) -> str:
        return f'"{self.URL.strip()}"' if self.URL.strip() else ''


class PathCombinedBlock(DirpathBlockBase, InputsInlineBlockBase):
    """ 路徑組合積木 """
    template = '路徑{PATH_A}底下的{PATH_B}'
    colour = BlockBase.Colour.dirpath
    arg_dicts = {
        'PATH_A': {
            'type': 'input_value',
            'check': 'dirpath',
        },
        'PATH_B': {
            'type': 'input_value',
            'check': ['dirpath', 'filepath'],
        },
    }

    def ahkscr(self) -> str:
        path_a_ahkscr = self.PATH_A.ahkscr()
        path_b_ahkscr = self.PATH_B.ahkscr()
        if path_a_ahkscr == "" or path_b_ahkscr == "":
            return ""

        return f'{path_a_ahkscr} . "/" . {path_b_ahkscr}'


class RunBlock(ActionBlockBase):
    """ 執行/開啟 檔案/目錄/網頁 積木 """
    template = '開啟{OBJ}'
    colour = BlockBase.Colour.action
    arg_dicts = {
        'OBJ': {
            'type': 'input_value',
            'check': ["dirpath", "filepath", "link", "String"]
        },
    }

    def ahkscr(self) -> str:
        return ";"*(self.OBJ.ahkscr().strip() == "") + f"Run % {self.OBJ.ahkscr()}"


class ClipboardBlock(StringBlockBase):
    """ 剪貼簿積木 """
    template = '剪貼簿內容'
    colour = BlockBase.Colour.String

    def ahkscr(self) -> str:
        return f'Clipboard'


class OptionTimeBlock(NumberBlockBase):
    """ 現年/月/日/星期/時/分/秒 時間積木 """
    template = '{TIME}'
    colour = BlockBase.Colour.Number
    arg_dicts = {
        'TIME': {
            'type': 'field_dropdown',
            "options": [
                ["現年(YYYY)", "A_YYYY"],
                ["現月(01-12)", "A_MM"],
                ["現日(01-31)", "A_DD"],
                ["現星期(1-7)", "(A_WDay=1 ? 7 : A_WDay-1)"],
                ["現時(00-23)", "A_Hour"],
                ["現分(00-59)", "A_Min"],
                ["現秒(00-59)", "A_Sec"],
            ],
        },
    }

    def ahkscr(self) -> str:
        return f"{self.TIME}"


class TrayTipBlock(ActionBlockBase):
    """ 執行/開啟 檔案/目錄/網頁 積木 """
    template = '桌面通知{TEXT}'
    colour = BlockBase.Colour.String
    arg_dicts = {
        'TEXT': {
            'type': 'input_value',
        },
    }

    def ahkscr(self) -> str:
        text_ahkscr = self.TEXT.ahkscr()
        return ";"*(text_ahkscr == "") + f"TrayTip,,% {text_ahkscr}"


class OptionalSendKeyBlock(ActionBlockBase):
    """ 送出按鍵積木(可選擇模式) """
    template = '送出按鍵{KEY}(使用{SEND_MODE})'
    colour = BlockBase.Colour.action
    arg_dicts = {
        'SEND_MODE': {
            'type': 'field_dropdown',
            "options": [
                ["SendInput", "SendInput"],
                ["Send", "Send"],
                ["SendPlay", "SendPlay"],
            ],
        },
        'KEY': {
            'type': 'input_value',
            'check': ['hot_key', 'normal_key']
        },
    }

    def ahkscr(self) -> str:
        key_ahksrc = self.KEY.ahkscr(to_be_send=True)
        return ";"*(key_ahksrc == "") + f"{self.SEND_MODE}, {key_ahksrc}"


class SendInputKeyBlock(ActionBlockBase):
    """ 送出按鍵積木 """
    template = '送出按鍵{KEY}'
    colour = BlockBase.Colour.action
    arg_dicts = {
        'KEY': {
            'type': 'input_value',
            'check': ['hot_key', 'normal_key']
        },
    }

    def ahkscr(self) -> str:
        key_ahksrc = self.KEY.ahkscr(to_be_send=True)
        return ";"*(key_ahksrc == "") + f"SendInput, {key_ahksrc}"


class SendInputTextBlock(ActionBlockBase):
    """ 送出文字積木 """
    template = '送出文字{TEXT}'
    colour = BlockBase.Colour.String
    arg_dicts = {
        'TEXT': {
            'type': 'input_value',
        },
    }

    def ahkscr(self) -> str:
        text_ahksrc = self.TEXT.ahkscr()
        return ";"*(text_ahksrc == "") + f'SendInput % "{{TEXT}}" . {text_ahksrc}'


class FileRecycleEmptyBlock(ActionBlockBase):
    """ 清空資源回收桶積木 """
    template = '清空資源回收桶'
    colour = BlockBase.Colour.action

    def ahkscr(self) -> str:
        return "FileRecycleEmpty"


class ReloadBlock(ActionBlockBase):
    """ 刷新AHK腳本積木 """
    template = '刷新AHK腳本'
    colour = BlockBase.Colour.action

    def ahkscr(self) -> str:
        return "Reload"


class RunFileByProgramBlock(ActionBlockBase, InputsInlineBlockBase):
    """ 使用特定程式執行檔案 積木 """
    template = '用{PROGRAM}程式來開啟{FILE}'
    colour = BlockBase.Colour.action
    arg_dicts = {
        'PROGRAM': {
            'type': 'input_value',
            'check': "filepath"
        },
        'FILE': {
            'type': 'input_value',
        },
    }

    def ahkscr(self) -> str:
        program_ahkscr = self.PROGRAM.ahkscr().strip()
        file_ahkscr = self.FILE.ahkscr().strip()
        return ";"*(
            program_ahkscr == "" or file_ahkscr == ""
        ) + f'Run % {program_ahkscr} . " " . {file_ahkscr}'


class ProcessCloseBlock(ActionBlockBase):
    """ 執行終止程式積木 """
    template = '終止程式{PROCESS}'
    colour = BlockBase.Colour.action
    arg_dicts = {
        'PROCESS': {
            'type': 'input_value',
            'check': 'String',
        },
    }

    def ahkscr(self) -> str:
        process_ahkscr = self.PROCESS.ahkscr().strip()
        return ";"*(process_ahkscr == "") + f'Process, Close, % {process_ahkscr}'


class WinActivateBlock(ActionBlockBase):
    """ 置頂視窗積木 """
    template = '置頂視窗, 標題含:{WIN_TITLE}'
    colour = BlockBase.Colour.action
    arg_dicts = {
        'WIN_TITLE': {
            'type': 'input_value',
            'check': 'String',
        },
    }

    def ahkscr(self) -> str:
        win_title_ahkscr = self.WIN_TITLE.ahkscr().strip()
        return "\n".join([
            "SetTitleMatchMode, 2",
            ";"*(win_title_ahkscr == "") + f'WinActivate % {win_title_ahkscr}',
        ])


class SleepBlock(ActionBlockBase):
    """ 等待毫秒時間積木 """
    template = '等待{TIME_MS}毫秒'
    colour = "#80ADC4"
    arg_dicts = {
        'TIME_MS': {
            'type': 'input_value',
            'check': 'Number',
        },
    }

    def ahkscr(self) -> str:
        time_ms_ahkscr = self.TIME_MS.ahkscr()
        return ";"*(time_ms_ahkscr == "") + f'Sleep % {time_ms_ahkscr}'


class SetClipboardBlock(ActionBlockBase):
    """ 設定剪貼簿內容積木 """
    template = '設定剪貼簿內容為{TEXT}'
    colour = BlockBase.Colour.String
    arg_dicts = {
        'TEXT': {
            'type': 'input_value',
        },
    }

    def ahkscr(self) -> str:
        text_ahksrc = self.TEXT.ahkscr()
        return ";"*(text_ahksrc == "") + f'Clipboard := {text_ahksrc}'


class HotStringBlock(InputsInlineBlockBase, BlockBase):
    """ 熱字串積木 """
    template = '輸入{ABBR}Enter展開為{TEXT}'
    colour = BlockBase.Colour.hot_string
    arg_dicts = {
        'ABBR': {
            'type': 'input_value',
            'check': 'String',
        },
        'TEXT': {
            'type': 'input_value',
            'check': 'String',
        },
    }

    def ahkscr(self) -> str:
        abbr_ahksrc = self.ABBR.ahkscr(with_quotes=False)
        text_ahksrc = self.TEXT.ahkscr(with_quotes=False)
        return ";"*(not all([abbr_ahksrc, text_ahksrc])) + f'::{abbr_ahksrc}::{text_ahksrc}'
