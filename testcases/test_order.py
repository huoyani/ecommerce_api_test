import pytest

from conftest import BASE_URL
from utils.yaml_util import load_yaml_file
from utils.request_util import RequestUtil
from common.context import Context
from utils.db_util import DBUtil

cases=load_yaml_file("./config/test_data/order.yaml")

def handle_extract(extract_config,response):
    """
       处理extract：从响应中提取数据，存入Context
       :param extract_config: YAML里的extract节点（比如{"order_id": "body.data.order_id"}）
       :param response: 接口响应对象
       """
    if not extract_config:
        return
    res_json=response.json()
    for var,field in extract_config.items():  #order_id: body.data.order_id
        # 拆分字段路径：body.data.order_id → ["body", "data", "order_id"]
        parts=field.split(".")
        value=res_json
        for part in parts[1:]: #跳过第一个body
            if isinstance(value,dict) and part in value:
                value=value[part]
            else:
                value=None
                break
        Context.set(var,value)
        print(f"提取到{var} = {value}，已存入上下文")

@pytest.mark.parametrize("case",cases)
def test_order(case):
    print(case)
    print("\n====", case["name"], "=====")
    headers = case["request"].get("headers", {})
    json = case["request"].get("json", None)
    params = case["request"].get("params", None)
    res=RequestUtil.send_request(
        method=case["request"]["method"],
        url=BASE_URL+case["request"]["url"],
        headers=headers,
        json=json,
        params=params
    )
    res_json=res.json()

    #处理extract
    extract_config=case.get("extract",{}) #取yaml里的extract节点
    handle_extract(extract_config,res)

    #数据库断言
    if case["name"].startswith("创建订单-正向"):
        order_id=Context.get("order_id")
        print("数据库校验order_id=",order_id)
        #连接数据库
        db= DBUtil()
        sql=f"SELECT * FROM orders WHERE order_id='{order_id}'"
        db_data=db.query_one(sql)
        print("查询结果:",db_data)

        assert db_data is not None,"数据库没有插入订单！"
        request_json=case["request"].get("json",{})
        if "goods_id" in request_json:
            assert db_data["goods_id"]==request_json["goods_id"],"goods_id不一致"
        if "num" in request_json:
            assert db_data["num"]==request_json["num"],"num不一致"

        db.close()


    for check in case["validate"]:
        if "eq" in check:
            key,expect=check["eq"]
            actual=None
            if key=="status_code":
                actual=res.status_code
            elif key.startswith("body."):#body.data.goods_id,body.code
                field=key.split(".",1)[1]  #data.goods_id,code
                if "." in field:#data.goods_id
                    nested_fields=field.split(".") #["data","goods_id"]
                    actual=res_json
                    for f in nested_fields:
                        actual=actual.get(f) if actual else None
                else: #code
                    actual=res_json.get(field)
            assert actual == expect, f"{key}预期：{expect},实际：{actual}"

        elif "exists" in check:
            key=check["exists"][0]
            if key.startswith("body."):  #body.data.order_id
                field=key.split(".",1)[1] #data.order_id
                nested_fields=field.split(".")
                value=res_json
                for f in nested_fields:
                    if isinstance(value,dict) and f in value:
                        value=value[f]
                    else:
                        value=None
                        break
                assert value is not None,f"{key}字段不存在"
