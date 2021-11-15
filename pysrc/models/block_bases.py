import abc
from typing import (
    List,
    Literal,
    Optional,
    Union,
)
import uuid
import re
import javascript
from browser import (
    doc,
)
from browser.html import (
    DIV,
)

from pysrc.utils import *


class BuildInBlockBase:
    """ 內建積木
    """
    pass


class BlockBase(metaclass=abc.ABCMeta):
    # 顯示訊息和變數的位置, 如: '調出訊息 {NAME} 的 {VALUE}'
    template: Union[str, List[str]] = None
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
            template = self.template if isinstance(
                self.template, str) else ''.join(self.template)
            template_arg_name_list = re.findall(R"\{(.+?)\}", template)
            assert len(template_arg_name_list) == len(set(template_arg_name_list)),\
                f"重複的參數名稱: [{', '.join(template_arg_name_list)}]"
            # 檢查是否有缺少的 arg
            assert set(template_arg_name_list) == self.arg_dicts.keys(),\
                f"缺少參數定義;"\
                f"template_arg_name_list: [{', '.join(template_arg_name_list)}];"\
                f"arg_dicts: [{', '.join(self.arg_dicts.keys())}]; "\

        # 將 arg 數值賦予至 self 的屬性

        v: Union[str, BlockBase, List[BlockBase]] = ""
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
        com_msg = cls.template if isinstance(
            cls.template, str) else '%n'.join(cls.template)
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
            "message0": cls._get_register_messages(),  # ex. '跳出訊息 %1',
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

        # 進行換行處理
        for breakline_arg_i in range(
                len(cls.arg_dicts)+1,
                len(cls.arg_dicts)+1 + str(com_dict['message0']).count('%n')):
            com_dict['message0'] = com_dict['message0'].replace(
                '%n', f"%{breakline_arg_i}", 1)
            com_dict['args0'].append({'type': 'input_dummy'})

        print('com_dict', com_dict)
        return com_dict

    @classmethod
    def register(cls) -> Optional['BlockBase']:
        """ 註冊積木至 window.Blockly.Blocks

        Returns:
            Optional['BlockBase']: 若積木可註冊則回傳該積木物件，否則回傳 None
        """
        # 若積木類的名稱不是以 Block 結尾就不進行註冊
        if not cls.__name__.endswith("Block"):
            return None

        # 若積木類為內建積木就不進行註冊
        if issubclass(cls, BuildInBlockBase):
            return None

        # 註冊 block
        Blockly.Blocks[cls._get_type_attr()] = {
            "init": lambda: javascript.this().jsonInit(cls._get_register_dict()),
        }
        return cls

    @classmethod
    def register_subclasses(cls) -> List['BlockBase']:
        """ 註冊所有子類積木至 window.Blockly.Blocks

        Returns:
            List['BlockBase']: 已註冊的積木類列表
        """
        com_registered_subclass_list = []
        for subclass in cls.__subclasses__():
            registered_subclass = subclass.register()
            registered_subclass_list = subclass.register_subclasses()

            for _registered_subclass in [registered_subclass] + registered_subclass_list:
                if _registered_subclass:
                    com_registered_subclass_list.append(_registered_subclass)

        # 動態引入所有積木類
        exec(f"from pysrc.models.blocks import *", globals())
        return com_registered_subclass_list

    def get_xml_str(self, formatting: bool = False) -> str:
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
        return xml_to_str(block_node, formatting)

    @staticmethod
    def create_from_block_node(
            block_node: browser.DOMNode,
            arg_name: str,
            find_all_next_block: bool = False) -> Union['BlockBase', List['BlockBase']]:
        """ 從 block node 建立積木實例

        Args:
            block_node(browser.DOMNode)
            arg_name(str): 參數名稱
            find_all_next_block(bool): 是否找出所有下一個 block, 若為 True 則會回傳積木串列. Defaults to False.

        Returns:
            Union[BlockBase, List[BlockBase]
        """

        input_node = next(
            (
                sub_block_node for sub_block_node in block_node.children
                if sub_block_node.attrs.get("name") == arg_name
            ), None
        )
        if input_node is None:
            return eval('EmptyBlock()') if not find_all_next_block else [eval('EmptyBlock()')]
        input_block_node = input_node.select_one('block')
        if input_block_node is None:
            return eval('EmptyBlock()') if not find_all_next_block else [eval('EmptyBlock()')]
        input_block_type: str = input_block_node.attrs['type']
        input_block_class_name = f"{to_camel_case(input_block_type)}Block"
        input_block_class: BlockBase = eval(input_block_class_name)
        input_block = input_block_class.create_blocks_from_xml_str(
            input_node.innerHTML
        )[0]

        if not find_all_next_block:
            return input_block

        input_block_list = [input_block]
        for statement_next_node in input_node.select('next'):
            statement_block_node = statement_next_node.select_one('block')  # nopep8
            if statement_block_node is None:
                continue
            statement_block_type: str = statement_block_node.attrs['type']
            statement_block_class_name = f"{to_camel_case(statement_block_type)}Block"
            statement_block_class: BlockBase = eval(
                statement_block_class_name
            )
            statement_block = statement_block_class.create_blocks_from_xml_str(
                statement_block_node.outerHTML
            )[0]
            input_block_list.append(statement_block)
        return input_block_list

    @staticmethod
    def create_blocks_from_xml_str(xml_str: str) -> List['BlockBase']:
        """ 從 xml 字串建立積木實例

        Raises:
            ValueError: 解析 xml 錯誤

        Returns:
            BlockBase: 積木實例
        """
        com_block_list = []

        # 遍歷所有獨立的 block 群
        xml_div = DIV(xml_str)
        _block_node_list = xml_div.select('xml>block') or [
            child_note for child_note in xml_div.children
            if child_note.tagName == 'BLOCK'
        ]
        block_node_list = []
        for block_node in _block_node_list:
            block_node_list.append(block_node)

            # 不斷取得下一個 block node (next>block)
            while True:
                next_node = next(
                    (
                        child_note for child_note in block_node.children
                        if child_note.tagName == 'NEXT'
                    ), None
                )
                if not next_node:
                    break
                block_node = next_node.select_one('block')
                block_node_list.append(block_node)

        for block_node in block_node_list:

            # 分析 block 的 type，並準備建立積木實例的參數字典
            block_type: str = block_node.attrs['type']
            block_class_name = f"{to_camel_case(block_type)}Block"
            block_class: BlockBase = eval(block_class_name)
            block_kwargs = {}

            # 遍歷 block 的 args: 將子層積木實例化 或者獲取 field 值
            for arg_name, arg_dict in block_class.arg_dicts.items():

                # 若 arg 類型為 input_value ，就賦值 [實例化子層積木] 至 block_kwargs
                if arg_dict['type'] == 'input_value':
                    value_block: BlockBase = BlockBase.create_from_block_node(
                        block_node, arg_name)
                    block_kwargs[arg_name] = value_block

                # 若 arg 類型為 input_statement，就賦值 [實例化子層積木列表] 至 block_kwargs
                elif arg_dict['type'] == 'input_statement':
                    statement_block_list: List[BlockBase] = BlockBase.create_from_block_node(
                        block_node, arg_name, find_all_next_block=True)
                    block_kwargs[arg_name] = statement_block_list

                # 若 arg 類型為 field 類，就獲取 field 值
                elif arg_dict['type'].startswith('field_'):
                    node_tag_name = "field"
                    field_node = next(
                        (
                            sub_block_node for sub_block_node in block_node.children
                            if sub_block_node.tagName == node_tag_name.upper() and sub_block_node.getAttribute('name') == arg_name
                        ), None
                    )
                    if field_node is None:
                        block_kwargs[arg_name] = eval('EmptyBlock()')
                        continue
                    block_kwargs[arg_name] = field_node.innerHTML

            com_block_list.append(block_class(**block_kwargs))
        return com_block_list

    class Colour:
        String = 160
        Number = hotkey = 230
        filepath = dirpath = link = 290
        action = 260
        hot_string = '#CD5C5C'


class ActionBlockBase(BlockBase):
    """ 動作型積木: 接受任何上下文積木 """
    @classmethod
    def _get_register_dict(cls):
        return {
            **super()._get_register_dict(),
            "previousStatement": None,
            "nextStatement": None,
        }


class InputsInlineBlockBase(BlockBase):
    """ 單行型積木 """
    @classmethod
    def _get_register_dict(cls):
        return {
            **super()._get_register_dict(),
            "inputsInline": True,
        }


class InputsExternalBlockBase(BlockBase):
    """ 多行型積木 """
    @classmethod
    def _get_register_dict(cls):
        return {
            **super()._get_register_dict(),
            "inputsInline": False,
        }


class ObjectBlockBase(BlockBase):
    """ 物件型積木: 有 output """
    @classmethod
    def _get_register_dict(cls):
        return {
            **super()._get_register_dict(),
            "output": None,
        }


class StringBlockBase(ObjectBlockBase):
    """ 字串型積木 """
    @classmethod
    def _get_register_dict(cls):
        return {
            **super()._get_register_dict(),
            "output": "String",
        }


class NumberBlockBase(ObjectBlockBase):
    """ 數字型積木 """
    @classmethod
    def _get_register_dict(cls):
        return {
            **super()._get_register_dict(),
            "output": "Number",
        }


class NormalKeyBlockBase(ObjectBlockBase):
    """ 按鍵型積木 """
    @classmethod
    def _get_register_dict(cls):
        return {
            **super()._get_register_dict(),
            "output": "normal_key",
        }


class HotKeyBlockBase(ObjectBlockBase):
    """ 熱鍵型積木 """
    @classmethod
    def _get_register_dict(cls):
        return {
            **super()._get_register_dict(),
            "output": "hot_key",
        }


class FilepathBlockBase(ObjectBlockBase):
    """ 檔案型積木 """
    @classmethod
    def _get_register_dict(cls):
        return {
            **super()._get_register_dict(),
            "output": "filepath",
        }


class DirpathBlockBase(ObjectBlockBase):
    """ 檔案型積木 """
    @classmethod
    def _get_register_dict(cls):
        return {
            **super()._get_register_dict(),
            "output": "dirpath",
        }


class LinkBlockBase(ObjectBlockBase):
    """ 檔案型積木 """
    @classmethod
    def _get_register_dict(cls):
        return {
            **super()._get_register_dict(),
            "output": "link",
        }
