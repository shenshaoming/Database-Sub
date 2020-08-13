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


tableSchema = get_xml_value("db_schema")
db_host = get_xml_value("db_host")
db_username = get_xml_value("db_user")
db_password = get_xml_value("db_password")
db_schema = get_xml_value("db_schema")
db_port = get_xml_value("db_port")

username = get_xml_value("username")
password = get_xml_value("password")

