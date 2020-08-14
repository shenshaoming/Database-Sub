import MySQLdb

from utils.config import db_host, db_username, db_password, db_schema, db_port


class MyConn(object):
    def __init__(self, host, user, password,
                 schema, port=3306):
        """
        :param host 数据库ip地址
        :param user 数据库连接用户名
        :param password 数据库连接密码
        :param schema 操作数据库名称
        :param port 端口号
        """

        self.host = host
        self.user = user
        self.password = password
        self.schema = schema
        self.port = int(port)
        self.conn = self.open_conn()
        self.cursor = self.conn.cursor()

    def ping(self):
        """
        当conn连接ping不通时，开启一个新的连接
        """

        try:
            self.conn.ping()
        except MySQLdb.MySQLError:
            self.conn = self.open_conn()
            self.cursor = self.conn.cursor()
        return self.conn

    def exec_sql_data_many(self, sql, data_list, flag=False):
        """
        批量执行sql语句
        :param sql 要执行的sql语句
        :param data_list 可遍历的数据类型
        :param flag 是否已经尝试过了
        """

        conn = self.conn
        try:
            cursor = conn.cursor()
            cursor.executemany(sql, data_list)
            conn.commit()
        except MySQLdb.MySQLError as e:
            # 如果已经尝试过了
            if flag:
                raise e
            self.ping()
            self.exec_sql_data_many(sql, data_list, True)
            print("[ Exception: %s\n%s\n%s]" % (str(e), sql, data_list))

    def exec_sql_data(self, sql, data, flag=False):
        """
        执行data插入sql语句后的sql语句
        :param sql 要执行的sql语句
        :param data sql中要插入的data,可以为None
        :param flag 是否已经尝试过了
        :return: 返回表的自增id
        """

        conn = self.conn
        try:
            cursor = conn.cursor()
            cursor.execute(sql, data)
            item_id = conn.insert_id()
            conn.commit()
            return item_id
        except MySQLdb.MySQLError as e:
            if flag:
                raise e
            self.ping()
            return self.exec_sql_data(sql, data, True)

    def exec_sql(self, sql):
        """
        执行sql语句
        """
        return self.exec_sql_data(sql, None)

    def get_result(self, sql):
        """
        获取执行sql语句后的结果
        """
        return self.get_result_data(sql, None)

    def get_result_data(self, sql, data, flag=False):
        """
            执行sql语句并返回执行结果
            :param sql:要执行的sql语句
            :param data: sql语句中夹杂的data
            :param flag: 是否尝试过了
            :return: 二维数组
        """

        conn = self.conn
        try:
            cursor = conn.cursor()
            cursor.execute(sql, data)
            rows = cursor.fetchall()
            conn.commit()
            return rows
        except Exception as e:
            if flag:
                raise e
            else:
                self.ping()
            return self.get_result_data(sql, data, True)

    def get_rs_with_describe(self, sql, flag=False):
        """
        从执行sql语句并配上字段注释
        :param sql: 要执行的sql语句
        :param flag: 是否尝试过了
        :return: 带有注释的sql语句
        """
        conn = self.conn

        try:
            cursor = conn.cursor()
            cursor.execute(sql)
            rows = cursor.fetchall()
            description = cursor.description
            conn.commit()
            return rows, description
        except Exception as e:
            if flag:
                print(sql)
                raise e
            else:
                self.ping()
            return self.get_rs_with_describe(sql, True)

    def open_conn(self, count=0):
        """
        建立数据库连接,如果连接超过一定次数,则返回一个None,表示建立数据库连接失败
        推荐不再使用该方法,转而使用MyConn类
        :param count: 数据库连接尝试次数
        :return: None
        """

        if count >= 3:
            raise MySQLdb.MySQLError("database connect have tried over 3 times")
        try:
            conn = MySQLdb.connect(host='%s' % self.host, user='%s' % self.user, passwd='%s' % self.password,
                                   db='%s' % self.schema, port=self.port, charset="utf8", use_unicode="True")

            return conn
        except MySQLdb.MySQLError as conn_error:
            error_code = conn_error.args[0]
            # 如果是网路错误
            if error_code >= 1158 & error_code <= 1161:
                return self.open_conn(count + 1)
            elif error_code == 1081:
                raise conn_error

    def close(self):
        """
        断开数据库连接
        :return: None
        """
        self.conn.cursor().close()
        self.conn.close()

    def generate_sql(self, table_name, ignore_col_set=()):
        """
        根据数据库中的列名生成字典格式的insert sql语句
        :param table_name 表名称
        :param ignore_col_set 要忽略列集合
        :return: 生成的insert语句
        """

        sql = "show columns from %s" % table_name
        rs = self.get_result(sql)

        col_list = list()
        for row in rs:
            if row[0] in ignore_col_set:
                continue
            else:
                col_list.append(row[0])
        sql = "INSERT INTO %s (%s) \nVALUES (" % (table_name, ", ".join(map(str, col_list)))
        sql = "%s%s )" % (sql, ", ".join(map(lambda item: "%(" + item + ")s", col_list)))
        return sql
