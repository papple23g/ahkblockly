import json
import inspect

from browser import (
    doc,
    window,
    aio,
)
from browser.html import (
    DIV,
    BUTTON,
    TEXTAREA,
    INPUT,
)

from pysrc.models.block_bases import BlockBase
from pysrc.models.blockly_board import BlocklyBoard
from pysrc.models.blocks import *
from pysrc.models import blocks as Blocks


def compile_btn(blocklyBoard: BlocklyBoard):
    """ 編譯按鈕 """
    async def blockly_board_to_xml_str_and_ahkscr():
        doc['xml_textarea'].value = window.prettify_xml(
            blocklyBoard.get_xml_str())
        doc['ahkscr_textarea'].value = await blocklyBoard.get_ahkscr()

    compile_btn = BUTTON("Compile", id="compile_btn")
    compile_btn.bind(
        "click", lambda _: aio.run(blockly_board_to_xml_str_and_ahkscr())
    )
    return compile_btn


def run_ahk_btn(blocklyBoard: BlocklyBoard):
    """ 執行 AHK 按鈕 """
    async def run_ahkscr():
        doc['xml_textarea'].value = window.prettify_xml(
            blocklyBoard.get_xml_str())
        doc['ahkscr_textarea'].value = await blocklyBoard.get_ahkscr()

        # POST 請求: 送出 AHK 程式碼並執行
        await aio.post(
            '/api/run_ahkscr',
            data=json.dumps(dict(
                ahkscr=doc['ahkscr_textarea'].value,
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
    global registered_block_class_list
    registered_block_class_list = BlockBase.register_subclasses()

    # 建立白板實例與白板DIV元素，並注入內容
    blocklyBoard = BlocklyBoard(
        toolbox=BlocklyBoard.Toolbox(categories=[
            # 建立工具欄積木
            BlocklyBoard.Toolbox.Category(
                # 建立一個[測試]的積木類別，包含所有積木 (但不包含空白積木)
                name="ALL",
                colour="#0000CD",
                blocks=[
                    block_class() for block_class_name, block_class in inspect.getmembers(Blocks, inspect.isclass)
                    if block_class_name.endswith("Block")
                    and block_class_name != "EmptyBlock"
                ],
            ),
            BlocklyBoard.Toolbox.Category(
                # 建立一個[測試]的積木類別，包含所有積木 (但不包含空白積木)
                name="熱鍵",
                colour="#0000CD",
                blocks=[
                    ShortCutBlock(
                        KEY=HotKeyBlock(
                            KEY_A="Ctrl",
                            KEY_B=NormalKeyBlock(KEY="F8"),
                        ),
                        DO=[
                            MsgboxBlock(TEXT=TextBlock(TEXT="Hello World!")),
                            MsgboxBlock(TEXT=TextBlock(TEXT="Hello World!2")),
                            # TODO: 追加更多 DO 積木串列測試
                            MsgboxBlock(TEXT=TextBlock(TEXT="Hello World!3")),
                        ],
                    )
                ],
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
    doc <= run_ahk_btn(blocklyBoard)

    # 置入停止按鈕
    doc <= BUTTON("Stop").bind(
        "click", lambda _: aio.run(aio.get('/api/stop_ahkscr'))
    )

    # 置入腳本設定: 勾選是否要以管理員身分啟動
    doc <= INPUT(
        type="checkbox",
        id="run_as_admin_checkbox",
        checked=True,
    )

    # 置入編譯後的 xml 與 ahk 程式碼 DIV 區塊
    doc <= code_view_div()


if __name__ == "__main__":
    main()
