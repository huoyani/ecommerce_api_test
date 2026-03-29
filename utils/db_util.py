import pymysql

class DBUtil:
    def __init__(self):
        self.conn=pymysql.connect(
            host="127.0.0.1",
            user="root",
            password="huoyani2004",
            database="test_db",
            charset="utf8mb4"
        )
        self.cursor=self.conn.cursor(pymysql.cursors.DictCursor)

    def query_one(self,sql):
        self.cursor.execute(sql)
        return self.cursor.fetchone()
    def execute(self,sql):
        self.cursor.execute(sql)
    def close(self):
        self.cursor.close()
        self.conn.close()