class TableNotFoundException(Exception):
    def __init__(self, database, table):
        self.database = database
        self.table = table
        Exception.__init__(self, "table not find %s.%s" % (database, table))

