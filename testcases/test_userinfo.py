import pytest

from conftest import BASE_URL
from utils.yaml_util import load_yaml_file
from utils.request_util import RequestUtil
from common.context import Context

cases=load_yaml_file("./config/test_data/userinfo.yaml")

@pytest.mark.parametrize("case",cases)
def test_userinfo(case):
    print(case)
    print("\n====", case["name"], "=====")
    headers = case["request"].get("headers", {})
    res = RequestUtil.send_request(
        method=case["request"]["method"],
        url=BASE_URL+case["request"]["url"],
        headers=headers
    )
    res_json=res.json()

    for check in case["validate"]:
        if "eq" in check:
            key,expect=check["eq"]
            actual=None
            # 1. 处理状态码
            if key=="status_code":
                actual=res.status_code
            # 2. 处理响应体一级字段（code/msg）
            elif key.startswith("body."):
                # 拆分body.xxx → 取xxx部分（比如body.code → code）
                field=key.split(".")[1]
                # 处理二级嵌套字段（比如body.data.username）
                if "." in field:
                    # 拆分data.username → ["data", "username"]
                    nested_fields=field.split(".")  #["data", "username"]（列表）
                    # 逐层取值（res_json["data"]["username"]）
                    actual=res_json  # res_json = {"code":200, "data":{"username":"test01", "role":"user"}}
                    for f in nested_fields:
                        actual=actual.get(f) if actual else None

                        # 第一次循环：f="data" → actual = res_json.get("data") → {"username":"test01", "role":"user"}
                       # 第二次循环：f="username" → actual = {"username":"test01"}.get("username") → "test01"
                else:
                    # 处理一级字段（body.code/body.msg）
                    actual=res_json.get(field)

            assert actual == expect, f"{key}预期：{expect},实际：{actual}"


