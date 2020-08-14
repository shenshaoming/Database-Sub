import jpype
import yaml

from entity.dataNode import DataNode
from exceptions.database import TableNotFoundException
from utils.mysql_util import MyConn

j_class = None
# 数据库连接池
database_pool_dict = {}


def parse_yaml(sharding_yaml):
    """
    解析yaml文件
    :param sharding_yaml: 读取出的dict对象
    :return: 一个字典对象， key为不加后缀的表名, value为old 和 new, 分别指向一个DataNode
    """

    result_dict = {}

    for table_name_base in sharding_yaml["shardingRule"]:
        temp = sharding_yaml["shardingRule"][table_name_base]
        result_dict[table_name_base] = {
            "old": DataNode(temp["old"], table_name_base,
                            temp["old"]["shardingColumn"], temp["keyGeneratorColumn"]),
            "new": DataNode(temp["new"], table_name_base,
                            temp["new"]["shardingColumn"], temp["keyGeneratorColumn"])
        }

    return result_dict


def get_sharding_index(key, num):
    """
    计算分片index
    :param key: 分片值
    :param num: 分片数量
    :return: 0~num - 1
    """

    global j_class
    if j_class is None:
        j_class = jpype.JClass("com.zqlh.main.JumpConsistentHash")
    return int(j_class.jumpConsistentHash(key, num))


def init_conn_pool(sources):
    for database_name in sources.keys():
        temp = sources[database_name]
        database_pool_dict[database_name] = MyConn(temp["idAddress"], temp["username"], temp["password"],
                                                   database_name, temp["port"])


def parse_obj(row, column_list):
    """
    将数据库中的数据由元组改为字典对象
    :param row: 单行数据
    :param column_list: 数据库中的列描述(列名, 数据类型, 数据长度....)
    :return:
    """

    data = {}
    for i in range(len(row)):
        data["%s" % column_list[i][0]] = row[i]
    return data


def check_table_exist(database_name, table_name, table_sql):
    """
    检查数据库#{database_name}中是否存在表#{table_name}
    如果不存在则根据#{table_sql}在#{database_name}对应的数据库中创建表
    :param database_name: 数据库名
    :param table_name: 表名
    :param table_sql: 创建表的sql语句
    :return: True 没有执行了生成表的sql; False 执行了生成新的表的sql
    """
    sql = """
    show tables like '%s'; 
    """

    rs = database_pool_dict[database_name].get_result(sql % table_name)
    if len(rs) > 0:
        print("表%s存在" % table_name)
        return True
    else:
        # 创建表
        database_pool_dict[database_name].exec_sql(table_sql % table_name)
        print("在数据库 %s 中创建表: %s" % (database_name, table_name))
        return False


def format_table_sql(create_table_sql, table_name):
    """
    将一条Create table语句中的#{table_name}替换为%s
    :param create_table_sql: 创建表的sql语句
    :param table_name: 表名
    :return: CREATE Table `%s` (...)
    """

    return str(create_table_sql).replace(table_name, "%s", 1)


def calculate_sharding(data, database_sharding_column, table_sharding_column, database_num, table_num):
    """
    计算分片键
    :param data: dict对象， key为列名，value为该列的值
    :param database_sharding_column: 数据库分片键
    :param table_sharding_column: 数据表分片键
    :param database_num: 数据库分片数量
    :param table_num: 表分片数量
    :return: 分库名称, 分表名称
    """

    return get_sharding_index(data[database_sharding_column],
                              database_num), get_sharding_index(data[table_sharding_column], table_num)


# 数据库插入操作的sql语句
insert_sql_cache = {}


def insert_new_data(database, table, data):
    """
    插入数据到{database}.{table}中
    :param database: 数据库名
    :param table: 表名
    :param data: 待插入的对象
    :return: None
    """

    conn = database_pool_dict[database]

    if table in insert_sql_cache.keys():
        sql = insert_sql_cache[table]
    else:
        sql = conn.generate_sql(table)
        insert_sql_cache[table] = sql
    conn.exec_sql_data(sql, data)


def delete_data_by_key(data, database, table, key_column):
    """
    通过#{key_column}删除数据
    :param data: data_dict对象
    :param database: 数据库
    :param table: 表名
    :param key_column: 逐渐列
    :return: None
    """

    sql = "delete from %s where %s = '%s'" % (table, key_column, data[key_column])
    database_pool_dict[database].exec_sql(sql)


def init_last_key(database, table, key_column, column_list):
    """
    初始化用于last_key
    :param database: 数据库
    :param table: 表名
    :param key_column: 主键列
    :param column_list: 数据库列描述的list
    :return: table中的数据不可为空
    """

    sql = "select * from %s order by %s" % (table, key_column)
    rs = database_pool_dict[database].get_result(sql)
    data = parse_obj(rs[0], column_list)
    return data[key_column]


def data_transform(tables_dict):
    """
    数据迁移
    :return:
    """

    # 按照主键排序搜索,
    select_sql = "select * from %s where %s > '%s' order by %s limit %d"
    # 分页条数
    size = 3000
    select_data = ["table_name", "key_column", "last_key", "key_column", size]

    for logic_table_name in tables_dict:

        old_dataNode = tables_dict[logic_table_name]["old"]
        new_dataNode = tables_dict[logic_table_name]["new"]

        old_database_list = old_dataNode.get_database_list()
        new_database_list = new_dataNode.get_database_list()
        old_table_list = old_dataNode.get_table_list()
        new_table_list = new_dataNode.get_table_list()
        # 数据库逻辑主键
        key_column = old_dataNode.key_column
        select_data[1] = select_data[3] = key_column

        rs = database_pool_dict[old_database_list[0]]\
            .get_result("show create table %s" % old_table_list[0])
        if len(rs) < 1:
            raise TableNotFoundException(old_database_list[0], old_table_list[0])
        else:
            # 获取创建表的sql语句
            table_sql = format_table_sql(rs[0][1], old_table_list[0])

        # 获取数据库中列的描述信息
        describe_sql = "select * from %s order by %s limit 1" % (old_table_list[0], key_column)
        # 获得表中所有列的描述信息
        rs, column_list = database_pool_dict[old_database_list[0]] \
            .get_rs_with_describe(describe_sql)

        for new_database in new_database_list:
            for new_table in new_table_list:
                check_table_exist(new_database, new_table, table_sql)

        for old_database in old_database_list:
            for old_table in old_table_list:

                total = database_pool_dict[old_database].get_result("select count(1) from %s" % old_table)[0][0]
                if total < 1:
                    print("%s.%s 中数据为空" % (old_database, old_table))
                    continue

                last_key = init_last_key(old_database, old_table, key_column, column_list)

                count = 0
                select_data[0] = old_table
                rs = database_pool_dict[old_database].get_result(select_sql % tuple(select_data))
                while len(rs) > 0:
                    select_data[2] = last_key
                    for row in rs:
                        data = parse_obj(row, column_list)
                        last_key = data[key_column]
                        # 计算分片index
                        target_database_index, target_table_index = \
                            calculate_sharding(data, old_dataNode.sharding_column, new_dataNode.sharding_column,
                                               len(new_database_list), len(new_table_list))
                        target_database = new_database_list[target_database_index]
                        target_table = new_table_list[target_table_index]
                        if old_database != target_database or old_table != target_table:
                            # 数据有移动, 插入数据到新表中,并且删除当前行
                            insert_new_data(target_database, target_table, data)
                            delete_data_by_key(data, old_database, old_table, old_dataNode.key_column)
                    count += len(rs)
                    print("已迁移完成 %s, 还剩 %s" % (count, total - count))
                    rs = database_pool_dict[old_database].get_result(select_sql % tuple(select_data))
                print("%s.%s 表的数据迁移完成" % (old_database, old_table))


def main():
    """
    负责完成主业务的流程
    :return:
    """

    # 1. 解析yml
    with open("file/sharding.yml") as f:
        sharding_yml = yaml.load(f, yaml.FullLoader)

    tables_dict = parse_yaml(sharding_yml)

    try:
        # 2. 初始化数据库连接对象集合
        init_conn_pool(sharding_yml["dataSources"])

        # 3. 数据迁移
        data_transform(tables_dict)
    finally:
        # 任务结束,关闭所有的连接
        for database_name in database_pool_dict:
            database_pool_dict[database_name].close()


if __name__ == '__main__':
    try:
        jpype.startJVM(jpype.getDefaultJVMPath(), "-ea", "-Djava.class.path=hash/snow.jar", convertStrings=False)
        main()
        # 程序正常运行结束,通知监控程序，运行结束了
    except BaseException as e:
        raise e
    finally:
        jpype.shutdownJVM()
