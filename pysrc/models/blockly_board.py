from typing import List

from browser import (
    doc,
)

from pysrc.utils import *
from pysrc.models.block_bases import BlockBase

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
