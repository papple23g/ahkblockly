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


def compile_btn(blocklyBoard: BlocklyBoard):
    """ 編譯按鈕 """
    def blockly_board_to_xml_str_and_ahksrc(ev):
        doc['xml_textarea'].value = window.prettify_xml(
            blocklyBoard.get_xml_str())
        doc['ahk_textarea'].value = blocklyBoard.get_ahksrc()

    compile_btn = BUTTON("Compile")
    compile_btn.bind(
        "click", blockly_board_to_xml_str_and_ahksrc
    )
    return compile_btn


def code_view_div():
    """ 瀏覽編譯後的 xml 與 ahk 程式碼 DIV 元素 """
    return DIV(
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

    # register all Blocks
    BlockBase.register_subclasses()

    # 白板: 建立白板實例、DIV元素並注入內容
    blocklyBoard = BlocklyBoard(
        toolbox=BlocklyBoard.Toolbox(categories=[
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
        ]),
        block=HotkeyExecuteBlock(
            NAME=NormalKeyBlock(
                normal_key="A",
            ),
            DO=MsgboxBlock(
                NAME=TextBlock(
                    TEXT="Hello World!",
                ),
            ),
        ),
    )
    doc <= blocklyBoard.get_div()
    blocklyBoard.inject()

    # 置入編譯按鈕
    doc <= compile_btn(blocklyBoard)

    # 置入執行按鈕
    doc <= BUTTON("Run", id="btn_run")

    # 置入編譯後的 xml 與 ahk 程式碼 DIV 區塊
    doc <= code_view_div()


if __name__ == "__main__":
    main()
