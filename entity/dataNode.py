def get_sharding_list(string):
    """
    从string中提取出节点数组
    :param string: 包含$的字符串, eg: ${1..6} 或 ${['01', '02', ... '06']}
    :return: 节点后缀数组
    """

    result_list = []
    if string[2] == '[':
        # 拆取数组
        end = string.rindex("]")
        temp = string[3:end]
        for data in temp.split(","):
            result_list.append(data.strip())
    elif string[1] == "{":
        index = string.index("..")
        begin = int(string[index - 1])
        end = int(string[index + 2])
        result_list = list(map(lambda x: x, range(begin, end + 1)))
    else:
        raise BaseException("语法错误")
    return result_list


class DataNode(object):
    def __init__(self, data_obj, table_logic_name, sharding_column):
        """
        :param data_obj: table_name_base所对应的dict
        :param table_logic_name: 逻辑表名
        """

        data_nodes = str(data_obj["dataNodes"])
        temp_list = data_nodes.split(table_logic_name)
        if len(temp_list) != 2:
            if len(temp_list) > 2:
                raise BaseException("%s table's dataNodes table_name use error: %s has too many "
                                    "'%s' in the string" % (table_logic_name, data_nodes, table_logic_name))
            elif len(temp_list) < 2:
                raise BaseException("%s table's dataNodes table_name use error: %s has too little "
                                    "'%s' in the string" % (table_logic_name, data_nodes, table_logic_name))
        # 截取数据库的节点情况
        temp = temp_list[0].split("$")
        database_basename = temp[0].replace(".", "")
        if len(temp) > 1:
            database_suffix_list = get_sharding_list('$%s' % temp[1])
        else:
            database_suffix_list = ['']

        # 提取表的节点情况
        temp = temp_list[1].split("$")
        if len(temp) > 1:
            table_suffix_list = get_sharding_list('$%s' % temp[1])
        else:
            table_suffix_list = []
        self.table_basename = "%s%s" % (table_logic_name, temp[0])
        self.database_basename = database_basename
        self.table_suffix_list = table_suffix_list
        self.database_suffix_list = database_suffix_list
        self.sharding_column = sharding_column

    def get_database_list(self):
        temp_list = []
        for database_suffix in self.database_suffix_list:
            temp_list.append("%s%s" % (self.database_basename, database_suffix))
        return temp_list

    def get_table_list(self):
        temp_list = []
        for table_suffix in self.table_suffix_list:
            temp_list.append('%s%s' % (self.table_basename, table_suffix))
        return temp_list

    def get_column_list(self):
        return self.column_list

    def set_column_list(self, column_list):
        self.column_list = column_list


if __name__ == '__main__':
    data_list = map(lambda x: x+2, [1, 2, 3, 4])

    print(list(data_list))