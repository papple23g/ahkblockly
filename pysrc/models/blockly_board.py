from typing import List
import uuid

from browser import (
    doc,
)
from browser.html import (
    DIV,
)

from pysrc.utils import *
from pysrc.models.block_bases import BlockBase


class BlocklyBoard:
    """ Blockly 白板 """
    workspace = None

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

    def _get_option_dict(self) -> dict:
        """ 取得建立 Blockly 白板的參數選項字典 """
        toolbox_div = DIV()
        toolbox_div.innerHTML = self.toolbox.get_xml_str()
        return {
            # 工具箱元素
            "toolbox": toolbox_div,
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

    def __init__(
            self,
            toolbox: Toolbox,
            block: BlockBase = None,):  # .## 之後要改為多個積木
        """ Blockly 白板

        Args:
            toolbox (Toolbox): 積木工具欄
            block (BlockBase, optional): 初始化後白板上的積木. Defaults to None.
        """
        self.blockly_id = f"_{uuid.uuid4().hex}"
        self.toolbox = toolbox
        self.block = block

    def inject(self):
        """ 注入白板、工具箱、積木至網頁中 """
        assert doc.select_one(f"#{self.blockly_id}") != None,\
            f"尚未將此白板(id={self.blockly_id})的 DIV 元素置入至網頁中"
        self.workspace = Blockly.inject(
            self.blockly_id,
            self._get_option_dict(),
        )
        if self.block:
            self.load_xml(self.block.get_xml_str())

    def get_xml_str(self) -> str:
        """ 取得 XML 字串 """
        xml = Blockly.Xml.workspaceToDom(self.workspace)
        return xml_to_str(xml)

    def get_ahksrc(self) -> str:
        """ 取得 AHK 代碼 """
        xml_str = self.get_xml_str()
        return BlockBase.create_from_xml_str(xml_str).ahkscr()

    def load_xml(self, xml_str: str):
        """ 載入 XML 字串 """
        div = DIV()
        div.innerHTML = xml_str
        Blockly.Xml.clearWorkspaceAndLoadFromXml(
            div,
            self.workspace
        )

    def get_div(self) -> DIV:
        """ 取得 DIV 元素 """
        return DIV(id=self.blockly_id, style=dict(width="100%", height="600px"))
