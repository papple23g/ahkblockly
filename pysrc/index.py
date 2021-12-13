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
    SPAN,
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


def run_as_admin_span():
    """ 使用管理員模式執行 DIV 元素 """
    com_span = SPAN()
    com_span <= INPUT(
        type="checkbox",
        id="run_as_admin_checkbox",
        checked=True,
    )
    com_span <= SPAN(
        "使用管理員權限執行",
        style=dict(
            cursor="pointer",
            userSelect="none",
        )
    ).bind(
        "click", lambda ev: doc["run_as_admin_checkbox"].click()
    )
    return com_span


def operation_div(blocklyBoard):
    """ 操作 DIV 元素 """
    com_div = DIV()
    com_div <= compile_btn(blocklyBoard)
    com_div <= run_ahk_btn(blocklyBoard)
    com_div <= BUTTON("Stop").bind(
        "click", lambda _: aio.run(aio.get('/api/stop_ahkscr'))
    )
    com_div <= run_as_admin_span()
    return com_div  # + DIV(style=dict(float="clear"))


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
        # region 白板積木工具欄
        toolbox=BlocklyBoard.Toolbox(categories=[
            # 建立工具欄積木
            BlocklyBoard.Toolbox.Category(
                # 建立一個[ALL]的積木類別，包含所有積木 (但不包含空白積木)
                name="ALL",
                colour="#0000CD",
                blocks=[
                    block_class() for block_class_name, block_class in inspect.getmembers(Blocks, inspect.isclass)
                    if block_class_name.endswith("Block")
                    and block_class_name != "EmptyBlock"
                ],
            ),
            # region 基本
            BlocklyBoard.Toolbox.Category(
                name="🚩基本",
                colour="#0000CD",
                blocks=[
                    # 按下 F8 開啟記事本
                    ShortCutBlock(
                        KEY=NormalKeyBlock(KEY="F8"),
                        DO=[
                            RunBlock(
                                OBJ=OptionFileBlock(OBJ='記事本')
                            ),
                        ],
                    ),
                    # 按下 Ctrl+Shift+A 開啟 AHK 官網
                    ShortCutBlock(
                        KEY=HotKeyBlock(
                            KEY_A="Ctrl",
                            KEY_B=HotKeyBlock(
                                KEY_A="Shift",
                                KEY_B=NormalKeyBlock(KEY="A"),
                            )
                        ),
                        DO=[
                            RunBlock(
                                OBJ=LinkBlock(
                                    URL='https://www.autohotkey.com/')
                            ),
                        ],
                    ),
                    # 按下 Ctrl+Win+Delete 清空資源回收桶
                    ShortCutBlock(
                        KEY=HotKeyBlock(
                            KEY_A="Ctrl",
                            KEY_B=HotKeyBlock(
                                KEY_A="Shift",
                                KEY_B=NormalKeyBlock(KEY="Delete"),
                            )
                        ),
                        DO=[
                            TrayTipBlock(TEXT=TextBlock(TEXT="正在清空資源回收桶...")),
                            FileRecycleEmptyBlock(),
                            MsgboxBlock(TEXT=TextBlock(TEXT="資源回收桶已清除完畢!")),
                        ],
                    ),
                    # 開啟檔案路徑 C:\*.exe
                    RunBlock(OBJ=FilepathBlock(PATH="C:\*.exe")),
                    # 下拉式選單: 選擇檔案、資料夾、網址
                    OptionFileBlock(),
                    OptionDirBlock(),
                    OptionLinkBlock(),
                    # 跳出訊息
                    MsgboxBlock(TEXT=TextBlock(TEXT="Hello World!")),
                    # 輸入文字
                    SendInputTextBlock(TEXT=TextBlock(TEXT="xxx@gmail.com")),
                    # 熱字串: 輸入 btw, 展開為 by the way
                    HotStringBlock(
                        ABBR=TextBlock(TEXT="btw"), TEXT=TextBlock(TEXT="by the way")),

                ],
            ),
            # endregion 基本
            # region 熱鍵
            BlocklyBoard.Toolbox.Category(
                name="⚡熱鍵",
                colour="#0000CD",
                blocks=[
                    # F8 熱鍵
                    ShortCutBlock(
                        KEY=NormalKeyBlock(KEY="F8")
                    ),
                    # Ctrl+Q 熱鍵
                    ShortCutBlock(
                        KEY=HotKeyBlock(
                            KEY_A="Ctrl",
                            KEY_B=NormalKeyBlock(KEY="q"),
                        ),
                    ),
                    # 功能鍵
                    HotKeyBlock(KEY_A="Ctrl"),
                    # 一般鍵
                    NormalKeyBlock(KEY="a"),
                    # 禁用熱鍵
                    DisableShortCutBlock(),
                    # 含設定熱鍵積木
                    ShortCutWithSettingBlock(
                        KEY=NormalKeyBlock(KEY="F8"),
                        SETTING=ShortCutSettingBlock(
                            KEEP_ORIGIN="TRUE",
                            EXECUTE_AFTER_RELEASE="TRUE",
                        )
                    ),
                ],
            ),
            # endregion 熱鍵
            # region 熱字串
            BlocklyBoard.Toolbox.Category(
                name="🔥熱字串",
                colour="#0000CD",
                blocks=[
                    # 熱字串: 輸入 btw, 展開為 by the way
                    HotStringBlock(
                        ABBR=TextBlock(TEXT="btw"), TEXT=TextBlock(TEXT="by the way")
                    ),
                    # 熱字串(含設定積木): 輸入 btw, 展開為 by the way
                    HotStringWithSettingBlock(
                        ABBR=TextBlock(TEXT="btw"), TEXT=TextBlock(TEXT="by the way"),
                        SETTING=HotStringSettingBlock(
                            CASE_SENSITIVE="TRUE",
                            IN_WORDS="TRUE",
                        )
                    ),
                    HotStringActionWithSettingBlock(
                        ABBR=TextBlock(TEXT="!ahk"),
                        DO=[
                            RunBlock(OBJ=LinkBlock(
                                URL='https://www.autohotkey.com/')),
                        ],
                        SETTING=HotStringSettingBlock(
                            CASE_SENSITIVE="TRUE",
                            IN_WORDS="TRUE",
                        )
                    ),

                ]
            )
            # endregion 熱字串

        ]),
        # endregion 白板積木工具欄
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

    doc <= operation_div(blocklyBoard)

    # 置入編譯後的 xml 與 ahk 程式碼 DIV 區塊
    doc <= code_view_div()


if __name__ == "__main__":
    main()
