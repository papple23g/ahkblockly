from browser import (
    doc,
)

from pysrc.utils import *
from pysrc.models.block_bases import BlockBase
from pysrc.models.blockly_board import BlocklyBoard
from pysrc.models.blocks import *


# register all Blocks #.##
BlockBase.register_subclasses()


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
