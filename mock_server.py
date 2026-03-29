from flask import Flask, jsonify, request
import time
import pymysql

app = Flask(__name__)

#数据库连接（全局）
conn=pymysql.connect(
    host="127.0.0.1",
    user="root",
    password="huoyani2004",
    database="test_db",
    charset="utf8mb4"
)
cursor = conn.cursor()

# 模拟数据库：存储用户、订单数据
mock_db = {
    "users": {
        "test01": {"password": "123456", "token": "valid_token_123", "user_id": 1001, "username": "test01",
                   "role": "user","nickname":"默认名称","gender":"男","avatar":"http://pic.png"},
        "admin": {"password": "admin123", "token": "admin_token_456", "user_id": 1002, "username": "admin",
                  "role": "admin","nickname":"管理员","gender":"女","avatar":"http://admin.png"}
    },
    "orders": {}
}


# 1.登录接口（支持成功/失败场景）
@app.route('/api/login', methods=['POST'])
def login():
    req_data = request.get_json() or {}
    username = req_data.get("username")
    password = req_data.get("password")

    # 场景1：参数缺失
    if not username or not password:
        return jsonify({"code": 400, "msg": "用户名/密码不能为空"}), 400

    # 场景2：用户不存在/密码错误
    if username not in mock_db["users"] or mock_db["users"][username]["password"] != password:
        return jsonify({"code": 401, "msg": "用户名/密码错误"}), 401

    # 场景3:登录成功
    user = mock_db["users"][username]
    return jsonify({
        "code": 200,
        "msg": "登录成功",
        "data": {
            "token": user["token"],
            "user_id": user["user_id"],
            "username": user["username"]
        }
    }), 200


# 2.获取用户信息接口（依赖token）
@app.route('/api/userinfo', methods=['GET'])
def userinfo():
    token = request.headers.get("token")

    # 场景1：token缺失
    if not token:
        return jsonify({"code": 403, "msg": "token不能为空"}), 403

    # 场景2：token失效
    valid_tokens = [user["token"] for user in mock_db["users"].values()]
    if token not in valid_tokens:
        return jsonify({"code": 401, "msg": "token已失效"}), 401

    # 场景3：获取成功
    user = next(u for u in mock_db["users"].values() if u["token"] == token)
    return jsonify({"code": 200,
                    "msg": "success",
                    "data": {
                        "user_id": user["user_id"],
                        "username":user["username"],
                        "password": user["password"],
                        "role": user["role"]
                    }}), 200


# 创建订单接口（依赖token+用户权限）
@app.route('/api/order/create', methods=['POST'])
def create_order():
    token = request.headers.get("token")
    req_data = request.get_json() or {}
    goods_id = req_data.get("goods_id")
    num = req_data.get("num", 1)

    # 校验token
    if not token or token not in [u["token"] for u in mock_db["users"].values()]:
        return jsonify({"code": 401, "msg": "无效token"}), 401
    # 校验参数
    if not goods_id:
        return jsonify({"code": 400, "msg": "商品ID不能为空"}), 400
    # 生成订单
    user = next(u for u in mock_db["users"].values() if u["token"] == token)
    order_id = f"ORD{int(time.time() * 1000)}{user['user_id']}"  # f-string拼接ORD{}{}，time.time()时间戳，保证订单号不重复
    #写入数据库
    sql=f"""
    INSERT INTO orders(order_id,user_id,goods_id,num,status)
    VALUES ('{order_id}',{user['user_id']},{goods_id},{num},'created')
    """
    print("执行SQL:",sql)
    cursor.execute(sql)
    conn.commit()
    return jsonify({
        "code": 200,
        "msg": "订单创建成功",
        "data": {"order_id": order_id}
    }), 200


# 4.查询订单接口（依赖token+order_id）
@app.route('/api/order/query', methods=['GET'])
def query_order():
    token = request.headers.get("token")
    order_id = request.args.get("order_id")

    # 校验token
    if not token or token not in [u["token"] for u in mock_db["users"].values()]:
        return jsonify({"code": 401, "msg": "无效token"}), 401

    #从数据库查询订单
    sql=f"SELECT * FROM orders WHERE order_id='{order_id}'"
    print("查询SQL:",sql)
    cursor.execute(sql)
    result=cursor.fetchone()
    print("查询结果:",result)
    if not result:
        return jsonify({"code":404,"msg":"订单不存在"}),404
    order={
        "order_id":result[1],
        "user_id":result[2],
        "goods_id":result[3],
        "num":result[4],
        "status":result[5]
    }
    # 成功查询
    return jsonify({
        "code": 200,
        "msg": "success",
        "data": order
    }), 200





if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080, debug=True)
