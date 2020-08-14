try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET


def get_xml_value(name):
    """
    读取xml
    :param name: 标签名
    :return:
    """

    xml_doc = ET.parse('file/conf.xml')
    value = xml_doc.find(name)
    if value is None or value.text is None:
        return None
    return value.text.strip()

