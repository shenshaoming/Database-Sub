import redis
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


redis_db = get_xml_value("redis_db")
redis_host = get_xml_value("redis_host")
redis_password = get_xml_value("redis_password")
redis_port = get_xml_value("redis_port")

tableSchema = get_xml_value("db_schema")
db_host = get_xml_value("db_host")
db_username = get_xml_value("db_user")
db_password = get_xml_value("db_password")
db_schema = get_xml_value("db_schema")
db_port = get_xml_value("db_port")

username = get_xml_value("username")
password = get_xml_value("password")

# 全局redis连接对象
global_redis_client = None


def open_redis_client():
    """
    打开一个redis连接
    :return:
    """

    return redis.Redis(host=redis_host, port=redis_port, db=redis_db, password=redis_password, decode_responses=True)


def get_redis_client():
    """
    获取一个redis连接,后续所有的redis操作获取的结果
    都会进行decode,无需手动decode
    :return:
    """

    global global_redis_client

    if global_redis_client is None:
        global_redis_client = open_redis_client()
    else:
        try:
            global_redis_client.ping()
        except redis.ConnectionError as e:
            global_redis_client = open_redis_client()
    return global_redis_client
