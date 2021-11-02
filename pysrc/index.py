from browser import (
    doc,
    alert
)
from browser.html import (
    DIV,
    BUTTON,
    TEXTAREA,
)

from pysrc.utils import *
from pysrc.models.block_bases import BlockBase
from pysrc.models.blockly_board import BlocklyBoard
from pysrc.models.blocks import *


def blockly_board_to_xml_str_and_ahksrc(blocklyBoard):
    xml = Blockly.Xml.workspaceToDom(blocklyBoard)
    xml_str = xml_to_str(xml)
    doc['xml_textarea'].value = window.prettify_xml(xml_str)
    doc['ahk_textarea'].value = BlockBase.create_from_xml_str(xml_str).ahkscr()


def layout():
    global blocklyBoard
    doc <= DIV(id="blocklyDiv", style=dict(width="100%", height="600px"))
    doc <= BUTTON("Compile", id="btn_compile").bind(
        "click", lambda ev: blockly_board_to_xml_str_and_ahksrc(blocklyBoard))
    doc <= BUTTON("Run", id="btn_run")
    doc <= DIV(
        [
            DIV(
                TEXTAREA(
                    id="xml_textarea",
                    style=dict(
                        width="100%",
                        height="300px",
                        whiteSpace="nowrap",
                    )
                ),
                style=dict(
                    float="left",
                    width="50%",
                    height="300px",
                ),
            ),
            DIV(
                TEXTAREA(
                    id="ahk_textarea",
                    style=dict(
                        width="100%",
                        height="300px",
                        whiteSpace="nowrap",
                    ),
                ),
                style=dict(
                    width="50%",
                    float="left",
                    height="300px",
                ),
            )
        ]
    )


def main():
    global blocklyBoard
    layout()

    # register all Blocks
    BlockBase.register_subclasses()

    # 準備 blockly 工具欄
    doc['toolbox'].innerHTML = BlocklyBoard.Toolbox(categories=[
        BlocklyBoard.Toolbox.Category(
            name="測試",
            colour="#0000CD",
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
    ]).get_xml_str()

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
    Blockly.Xml.clearWorkspaceAndLoadFromXml(
        doc["workspaceBlocks"], blocklyBoard)


if __name__ == "__main__":
    main()
