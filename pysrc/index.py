import abc
import string
import uuid
from typing import List, Union
import re
import javascript

from browser import (
    doc,
)

from pysrc.utils import *


class BuildInBlockBase:
    """ 內建積木
    """
    pass


class BlockBase(metaclass=abc.ABCMeta):
    # 顯示訊息和變數的位置, 如: '調出訊息 {NAME} 的 {VALUE}'
    template: str = None
    # 參數字典集: 註冊 block 時的 arg0 列表裡的對應 arg 設定字典
    arg_dicts: dict = dict()
    # 是否使用內嵌呈現? 否則為使用外嵌
    inputs_inline_bool: bool = None
    # 顏色
    colour: Union[str, int] = None
    # 其他註冊屬性
    register_dict: dict = dict()

    def __init__(self, **kwargs):
        """
        kwargs:
            積木的 arg 設定
            值可以是:
                - 字串
                - 布林值
                - 數字
                - 其他 BlockBase 物件
        """
        # 檢查 template 中是否有重複的參數
        if self.template:
            template_arg_name_list = re.findall(R"\{(.+?)\}", self.template)
            assert len(template_arg_name_list) == len(set(template_arg_name_list)),\
                f"重複的參數名稱: [{', '.join(template_arg_name_list)}]"
            # 檢查是否有缺少的 arg
            assert set(template_arg_name_list) == self.arg_dicts.keys(),\
                f"缺少參數定義;"\
                f"template_arg_name_list: [{', '.join(template_arg_name_list)}];"\
                f"arg_dicts: [{', '.join(self.arg_dicts.keys())}]; "\

        # 將 arg 數值賦予至 self 的屬性
        for k, v in kwargs.items():
            setattr(self, k, v)

    @classmethod
    def _get_register_messages(cls) -> str:
        """
        自 cls.template 替換成註冊 block 時使用的 message 格式
        如 cls.template = '調出訊息 {NAME} 的 {VALUE}'
        會得到 '調出訊息 %1 的 %2'

        Returns:
            str
        """
        com_msg = cls.template
        for arg_i, arg_name in enumerate(cls.arg_dicts.keys(), start=1):
            com_msg = com_msg.replace(
                f"{{{arg_name}}}", f"%{arg_i}")
        return com_msg

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
        com_dict = {
            'type': cls._get_type_attr(),
            "message0": cls._get_register_messages(),  # '跳出訊息 %1',
            'args0': [
                {
                    "name": arg_name,
                    **cls.arg_dicts.get(arg_name),
                }
                for arg_name in cls.arg_dicts.keys()
            ],
            "inputsInline": cls.inputs_inline_bool,
            "colour": cls.colour,
            **cls.register_dict,
        }
        # print(com_dict)
        return com_dict

    @classmethod
    def register(cls):
        # 若積木類的名稱不是以 Block 結尾就不進行註冊
        if not cls.__name__.endswith("Block"):
            return

        # 若積木類為內建積木就不進行註冊
        if issubclass(cls, BuildInBlockBase):
            return

        # 註冊 block
        Blockly.Blocks[cls._get_type_attr()] = {
            "init": lambda: javascript.this().jsonInit(cls._get_register_dict()),
        }
        # print(f'block class {cls.__name__} registered.')

    @classmethod
    def register_subclasses(cls):
        """
        註冊所有子類
        """
        for subclass in cls.__subclasses__():
            subclass.register()
            subclass.register_subclasses()

    def get_xml_str(self) -> str:
        xml = doc.implementation.createDocument("", "", None)
        block_node = xml.createElement("block")
        block_node.setAttribute("type", self.__class__._get_type_attr())
        block_node.setAttribute("id", uuid.uuid4().hex)

        for arg_name, arg_dict in self.arg_dicts.items():
            node_tag_name: str = "unknow"
            inner_html: str = ""
            if arg_dict['type'].startswith('input_'):
                _, node_tag_name = arg_dict['type'].split('_')
                inner_html = (
                    getattr(self, arg_name).get_xml_str()
                    if hasattr(self, arg_name) else " "
                )
            elif arg_dict['type'].startswith('field_'):
                node_tag_name = "field"
                inner_html = getattr(self, arg_name, " ")

            sub_block_node = xml.createElement(node_tag_name)
            sub_block_node.innerHTML = inner_html
            sub_block_node.setAttribute("name", arg_name)
            block_node.appendChild(sub_block_node)
        return xml_to_str(block_node)

    @staticmethod
    def create_from_xml_str(xml_str: str) -> 'BlockBase':
        """ 從 xml 字串建立積木實例 """
        xml = xml_str_to_xml(xml_str)
        block_node = xml.getElementsByTagName("block")[0]
        block_type: str = block_node.getAttribute("type")
        block_class: BlockBase = eval(f"{to_camel_case(block_type)}Block")
        block_kwargs = {}
        for arg_name, arg_dict in block_class.arg_dicts.items():

            if arg_dict['type'].startswith('input_'):
                _, node_tag_name = arg_dict['type'].split('_')
                sub_block_node = block_node.getElementsByTagName("block")[0]  # nopep8
                sub_block_type: str = sub_block_node.getAttribute("type")
                sub_block_class: BlockBase = eval(
                    f"{to_camel_case(sub_block_type)}Block"
                )
                block_kwargs[arg_name] = sub_block_class.create_from_xml_str(
                    xml_to_str(sub_block_node)
                )
            elif arg_dict['type'].startswith('field_'):
                node_tag_name = "field"
                sub_block_node = block_node.getElementsByTagName(node_tag_name)[0]  # nopep8
                block_kwargs[arg_name] = sub_block_node.innerHTML

        return block_class(**block_kwargs)

    class Colour:
        String = 160
        Number = hotkey = 230
        filepath = dirpath = link = 290


class ActionBlockBase(BlockBase):
    """ 動作型積木: 接受任何上下文積木 """
    register_dict = {
        "previousStatement": None,
        "nextStatement": None,
    }


class ObjectBlockBase(BlockBase):
    """ 物件型積木: 有 output """
    register_dict = {
        "output": None,
    }


class StringBlockBase(ObjectBlockBase):
    """ 字串型積木 """
    register_dict = {
        "output": "String",
    }


class NumberBlockBase(ObjectBlockBase):
    """ 數字型積木 """
    register_dict = {
        "output": "Number",
    }


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


# register all Blocks #.##
BlockBase.register_subclasses()


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

    class Toolbox:
        """ Blockly 工具箱 """

        class Category:
            """ Blockly 工具箱類別 """

            def __init__(self, name: str, colour: str, blocks: List[BlockBase]):
                self.name = name
                self.colour = colour
                self.blocks = blocks

            def get_xml_str(self) -> str:
                """ 取得 XML 字串 """
                xml_str = f'<category name="{self.name}" colour="{self.colour}">'
                for block in self.blocks:
                    xml_str += block.get_xml_str()
                xml_str += '</category>'
                return xml_str

        def __init__(self, categories: List[Category]):
            self.categories = categories

        def get_xml_str(self) -> str:
            """ 取得 XML 字串 """
            return ''.join([category.get_xml_str() for category in self.categories])


doc['toolbox'].innerHTML = BlocklyBoard.Toolbox(
    categories=[
        BlocklyBoard.Toolbox.Category(
            name="基本",
            colour="#AFEEEE",
            blocks=[
                TextBlock(
                    name="Hello World!",
                ),
                MathNumberBlock(
                    NUM=123,
                ),
                MsgboxBlock(
                    NAME=TextBlock(
                        TEXT="Hello World!",
                    ),
                ),
            ]
        ),
    ]
).get_xml_str()

# 建立白板: 在積木白板 DIV 建立白板元素，並回傳白板實例
blocklyBoard = BlocklyBoard().inject('blocklyDiv')
# # 填充初始白板內容 (目前為空值)
# Blockly.Xml.domToWorkspace(doc["workspaceBlocks"], blocklyBoard)


xml_str = '''<block type="msgbox" id="09209eb0773947778ddb51c736967d3f"><value name="NAME"><block type="text" id="b8729cd37e3248ff8e3d9594b3a2f988"><field name="TEXT">你好</field></block></value></block>'''
# xml_str = '''<block type="text" id="b8729cd37e3248ff8e3d9594b3a2f988"><field name="TEXT">你好</field></block>'''

example_block = MsgboxBlock.create_from_xml_str(xml_str)
# example_block = TextBlock.create_from_xml_str(xml_str)


xml_str = example_block.get_xml_str()
print(xml_str)
print(example_block.ahkscr())

doc["workspaceBlocks"].innerHTML = xml_str
Blockly.Xml.clearWorkspaceAndLoadFromXml(doc["workspaceBlocks"], blocklyBoard)
