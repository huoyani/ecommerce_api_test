import pytest


from utils.yaml_util import load_yaml_file
from utils.request_util import RequestUtil
BASE_URL="http://127.0.0.1:8080"

cases=load_yaml_file("./config/test_data/login.yaml")

@pytest.mark.parametrize("case",cases)
def test_login(case):
    print(case)
    print("\n====",case["name"],"=====")
    res = RequestUtil.send_request(
        method=case["request"]["method"],
        url=BASE_URL+case["request"]["url"],
        json=case["request"]["json"]
    )
    res_json=res.json()

    for check in case["validate"]:
        if "eq" in check:
            key,expect=check["eq"]  #拆分数组["status_code",200]
            if key =="status_code":
                actual=res.status_code
            elif key=="body.code":
                actual=res_json["code"]
            elif key=="body.msg":
                actual=res_json["msg"]
            assert actual == expect,f"{key}预期：{expect},实际：{actual}"
        elif "exists" in check:
            key = check["exists"][0]
            if key =="body.data.token":
                assert "token" in res_json["data"],"token字段不存在"



