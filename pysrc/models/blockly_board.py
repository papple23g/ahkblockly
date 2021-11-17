from typing import List
import uuid

from browser import (
    doc,
)
from browser.html import (
    DIV,
)
from browser.local_storage import storage

from pysrc.utils import *
from pysrc.models.block_bases import BlockBase


class BlocklyBoard:
    """ Blockly 白板 """

    # 白板工作區實例
    workspace = None

    # AHK 置頂程式碼: 腳本設定
    header_ahkscr = "\n".join([
        "#SingleInstance, Force",
        "#NoEnv",
        "SendMode Input",
        "SetWorkingDir, %A_ScriptDir%\n\n",
    ])

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

        def _clear_xml_and_ahk_code_area(ev):
            """ 清除 XML 和 AHK 代碼區域 """
            doc['ahkscr_textarea'].value = ''
            doc['xml_textarea'].value = ''

        def _save_xml_to_local_storage(ev):
            """ 儲存 XML 字串至 local storage """
            if ev.type not in ['ui', 'finished_loading']:
                storage['xml'] = self.get_xml_str()

        # 檢驗是否 html 已有對應的白板 id 元素
        assert doc.select_one(f"#{self.blockly_id}") != None,\
            f"尚未將此白板(id={self.blockly_id})的 DIV 元素置入至網頁中"

        # 建立 Blockly 白板 workspace
        self.workspace = Blockly.inject(
            self.blockly_id,
            self._get_option_dict(),
        )

        # 建立 Blockly 白板裡的積木內容 (自 local_storage 或參數 block 取得)
        if storage.get('xml'):
            self.load_xml_str(storage['xml'])
        elif self.block:
            self.load_xml_str(self.block.get_xml_str())

        # 設定監聽事件: 積木更改時，清空 xml 與 ahk 代碼區塊
        self.workspace.addChangeListener(_clear_xml_and_ahk_code_area)

        # 設定監聽事件: 積木更改時，紀錄 xml 至 local_storage
        self.workspace.addChangeListener(_save_xml_to_local_storage)

    def get_xml_str(self) -> str:
        """ 取得 XML 字串 """
        xml = Blockly.Xml.workspaceToDom(self.workspace)
        return xml_to_str(xml)

    def get_ahkscr(self) -> str:
        """ 取得 AHK 代碼 """
        from pysrc.models.block_bases import ObjectBlockBase, SettingBlockBase

        # 自白板獲取 xml 字串
        xml_str = self.get_xml_str()
        # 將 xml 字串解析成多個積木元素，再逐一取得積木 AHK 字串
        block_ahkscr_list = [
            block.ahkscr()
            for block in BlockBase.create_blocks_from_xml_str(xml_str)
            # 排除不能單獨編譯的積木: 物件型積木、設定型積木
            if not issubclass(block.__class__, ObjectBlockBase) and not issubclass(block.__class__, SettingBlockBase)
            # 排除積木沒有 ahk 代碼的積木(如:空積木)
            if block.ahkscr()
        ]
        # 輸出結果: 將不同積木的 AHK 代碼之間隔一行空白
        return self.header_ahkscr + "\n\n".join(block_ahkscr_list)

    def load_xml_str(self, xml_str: str):
        """ 載入 XML 字串 """
        _xml_div = DIV(xml_str)
        block_node_list = _xml_div.select('xml>block') or [
            child_note for child_note in _xml_div.children
            if child_note.tagName == 'BLOCK'
        ]
        xml_div = DIV(block_node_list)
        Blockly.Xml.clearWorkspaceAndLoadFromXml(
            xml_div,
            self.workspace
        )

    def get_div(self) -> DIV:
        """ 取得 DIV 元素 """
        return DIV(id=self.blockly_id, style=dict(width="100%", height="600px"))
