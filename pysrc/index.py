import json
import inspect

from browser import (
    doc,
    alert,
    aio,
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
from pysrc.models import blocks as Blocks


def compile_btn(blocklyBoard: BlocklyBoard):
    """ 編譯按鈕 """
    def blockly_board_to_xml_str_and_ahkscr(ev):
        doc['xml_textarea'].value = window.prettify_xml(
            blocklyBoard.get_xml_str())
        doc['ahkscr_textarea'].value = blocklyBoard.get_ahkscr()

    compile_btn = BUTTON("Compile", id="compile_btn")
    compile_btn.bind(
        "click", blockly_board_to_xml_str_and_ahkscr
    )
    return compile_btn


def run_ahk_btn():
    """ 執行 AHK 按鈕 """
    async def run_ahkscr():

        # 獲取 AHK 程式碼 (若尚未產生就點一下編譯按鈕)
        if not doc['ahkscr_textarea'].value:
            doc['compile_btn'].click()
        ahkscr = doc['ahkscr_textarea'].value

        # POST 請求: 送出 AHK 程式碼並執行
        await aio.post(
            '/api/run_ahkscr',
            data=json.dumps(dict(
                ahkscr=ahkscr,
            )),
        )

    run_ahk_btn = BUTTON("Run")
    run_ahk_btn.bind(
        "click", lambda ev: aio.run(run_ahkscr())
    )
    return run_ahk_btn


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
                    id="ahkscr_textarea",
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
                    block_class() for block_class_name, block_class in inspect.getmembers(Blocks, inspect.isclass)
                    if block_class_name.endswith("Block")
                    and block_class_name != "EmptyBlock"
                ],
                # blocks=[
                #     TextBlock(
                #         name="Hello World!",
                #     ),
                #     MathNumberBlock(
                #         NUM=123,
                #     ),
                #     MsgboxBlock(
                #         NAME=TextBlock(
                #             TEXT="Hello World!",
                #         ),
                #     ),
                # ]
            ),
        ]),
        block=ShortCutBlock(
            KEY=NormalKeyBlock(
                KEY="A",
            ),
            DO=MsgboxBlock(
                TEXT=TextBlock(
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
    doc <= run_ahk_btn()

    # 置入編譯後的 xml 與 ahk 程式碼 DIV 區塊
    doc <= code_view_div()


if __name__ == "__main__":
    main()
