from browser import (
    window,
)
import browser
import re

log = window.console.log
Blockly = window.Blockly


def to_snake_case(camel_case_str: str) -> str:
    return re.sub(r'(?<!^)(?=[A-Z])', '_', camel_case_str).lower()


def to_camel_case(snake_str: str) -> str:
    if '_' in snake_str:
        components = snake_str.split('_')
        return components[0].title() + ''.join(x.title() for x in components[1:])
    return snake_str.title()


def xml_to_str(xml: browser.DOMNode, formatting: bool = False) -> str:
    """ XML 元素轉換成字串

    Args:
        xml (browser.DOMNode)
        formatting (bool, optional): 使否要格式化(通常便於檢視用). Defaults to False.

    Returns:
        str
    """
    if hasattr(xml, 'ActiveXObject'):
        com_xml = xml.xml
    com_xml = window.XMLSerializer.new().serializeToString(xml)
    # 若要美化輸出，則改用下面的方式
    if formatting:
        return window.prettify_xml(com_xml)

    # 替換掉 /> 符號避免空的 block node 載入異常
    return com_xml.replace("/>", "></block>")


def xml_str_to_xml(xml_str: str) -> browser.DOMNode:
    return window.DOMParser.new().parseFromString(xml_str, 'text/xml')
