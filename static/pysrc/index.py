from typing import List
from browser import (
    doc,
    alert,
    window,
)
from browser.html import (
    DIV,
)
import browser
import re

import javascript

Blockly = window.Blockly


def to_snake_case(name: str) -> str:
    return re.sub(r'(?<!^)(?=[A-Z])', '_', name).lower()


# print(TextBlock()._get_type_attr())

class ArgBase:

    @classmethod
    def _get_type_attr(cls) -> str:
        """ 獲取 type 屬性的值

        Returns:
            str: 類名稱的 snake case
        """
        assert cls.__name__.endswith("Arg")
        return to_snake_case(cls.__name__[:-len('Arg')])


class InputValueArg(ArgBase):
    def __init__(self, name: str, check: str = None):
        self.name = name
        self.type: str = self._get_type_attr()
        self.check: str = check  # String、Number、Boolean、Array、Object

    def dict(self):
        return {
            'type': self.type,
            'name': self.name,
            'check': self.check,
        }


class BlockBase:
    _message: str = None

    @classmethod
    def _get_arg_name_list(cls) -> List[str]:
        """ 自 cls._message 獲取 block 參數名稱列表

        Returns:
            List[str]: 參數名稱列表
        """
        #.###
        return ['NAME']

    @classmethod
    def _get_messages(cls) -> str:
        #.###
        return '跳出訊息 %1'

    @classmethod
    def _get_type_attr(cls) -> str:
        """ 獲取 type 屬性的值

        Returns:
            str: 類名稱的 snake case
        """
        assert cls.__name__.endswith("Block")
        return to_snake_case(cls.__name__[:-len('Block')])

    @classmethod
    def _get_register_dict(cls) -> dict:
        """
        產生註冊 block 用的 dict，如:
            msgbox_dict = {
                "type": "msgbox",
                "message0": '跳出訊息 %1',
                "args0": [
                    {
                        "type": "input_value",
                        "name": "NAME",
                        "check": "String"
                    }
                ],
                "previousStatement": "Action",
                "nextStatement": "Action",
                "colour": 160,
                # "tooltip": "Returns number of letters in the provided text.",
                # "helpUrl": "http://www.w3schools.com/jsref/jsref_length_string.asp"
            }
        """
        #.###
        return {
            'type': cls._get_type_attr(),
            "message0": cls._get_messages(),  # '跳出訊息 %1',
            'args0': [
                InputValueArg(arg_name).dict()
                for arg_name in cls._get_arg_name_list()
            ],
            "previousStatement": "Action",
            "nextStatement": "Action",
            "colour": 160,
        }

    @classmethod
    def register(cls):
        # print(cls._get_type_attr())
        Blockly.Blocks[cls._get_type_attr()] = {
            "init": lambda: javascript.this().jsonInit(cls._get_register_dict()),
        }


class MsgboxBlock(BlockBase):
    pass


# register all Blocks
for Block in BlockBase.__subclasses__():
    Block.register()


class BlocklyBoard:
    """ Blockly 白板 """

    _option: dict = {
        # 工具箱元素
        "toolbox": doc['toolbox'],
        "collapse": True,
        "comments": True,
        "disable": True,
        "maxBlocks": "Infinity",
        "trashcan": True,
        "horizontalLayout": False,
        "toolboxPosition": 'start',
        "css": True,
        "media": 'https://blockly-demo.appspot.com/static/media/',
        "rtl": False,
        "scrollbars": True,
        "sounds": True,
        "oneBasedIndex": True,
        "grid": {
            "spacing": 20,
            "length": 1,
            "colour": '#888',
            "snap": False
        },
        "zoom": {
            "controls": True,
            "wheel": False,
            "startScale": 1,
            "maxScale": 3,
            "minScale": 0.3,
            "scaleSpeed": 1.2
        }
    }

    def inject(self, blockly_id: str):
        return Blockly.inject(blockly_id, self._option)

# 建立白板
blocklyBoard = BlocklyBoard().inject('blocklyDiv')
# 填充白板內容
Blockly.Xml.domToWorkspace(doc["workspaceBlocks"], blocklyBoard)

# xml = doc.implementation.createDocument(None, None)
# xml.createElement("heyHo")
# # xmlString = window.XMLSerializer().new.serializeToString(books)
# print(window.XMLSerializer.new().serializeToString(books))
