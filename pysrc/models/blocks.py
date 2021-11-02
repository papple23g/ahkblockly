import string

from pysrc.models.block_bases import *


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
    template = '跳出訊息 {NAME}'
    colour = BlockBase.Colour.String
    arg_dicts = {
        'NAME': {
            'type': 'input_value',
        },
    }

    def ahkscr(self) -> str:
        return f"Msgbox % {self.NAME.ahkscr()}"


class NormalKeyBlock(ObjectBlockBase):
    """ 普通按鍵積木 """
    template = '{normal_key}'
    colour = BlockBase.Colour.hotkey
    arg_dicts = {
        'normal_key': {
            'type': 'field_dropdown',
            "options": [
                [option_name, option_value]
                for (option_name, option_value) in zip(
                    string.ascii_uppercase,
                    string.ascii_lowercase,
                )
            ]
        },
    }
    register_dict = {
        "output": "normal_key",
    }

    def ahkscr(self) -> str:
        return f"{self.normal_key}"


class HotkeyExecuteBlock(BlockBase):
    """ 快捷鍵執行積木 """
    template = '當按下{NAME}執行{DO}'
    colour = BlockBase.Colour.hotkey
    arg_dicts = {
        'NAME': {
            'type': 'input_value',
            'check': ["normal_key", "function_key", "special_key"],
        },
        'DO': {
            'type': 'input_statement',
        }
    }
