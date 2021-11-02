from browser import (
    window,
)
import browser
import re

Blockly = window.Blockly


def to_snake_case(camel_case_str: str) -> str:
    return re.sub(r'(?<!^)(?=[A-Z])', '_', camel_case_str).lower()


def to_camel_case(snake_str: str) -> str:
    if '_' in snake_str:
        components = snake_str.split('_')
        return components[0].title() + ''.join(x.title() for x in components[1:])
    return snake_str.title()


def xml_to_str(xml: browser.DOMNode) -> str:
    if hasattr(xml, 'ActiveXObject'):
        com_xml = xml.xml
    com_xml = window.XMLSerializer.new().serializeToString(xml)
    # return window.prettify_xml(com_xml)
    return com_xml


def xml_str_to_xml(xml_str: str) -> browser.DOMNode:
    return window.DOMParser.new().parseFromString(xml_str, 'text/xml')
