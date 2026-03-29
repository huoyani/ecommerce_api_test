from utils.db_util import DBUtil

db = DBUtil()
result=db.query_one("SELECT 1")
print(result)
db.close()