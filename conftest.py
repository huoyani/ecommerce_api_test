import pytest
import os
import sys

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.request_util import RequestUtil
from common.context import Context
from common.exceptions import RequestFailedError

# 全局配置
BASE_URL = "http://127.0.0.1:8080"


@pytest.fixture(scope="session", autouse=True)
def clear_context():
    """会话级夹具：测试开始前清空上下文"""
    Context.clear()
    yield
    Context.clear()


@pytest.fixture(scope="session",autouse=True)
def login_valid_token():
    """会话级夹具：获取有效登录token"""
    # 调用登录接口
    login_url = f"{BASE_URL}/api/login"
    login_data = {"username": "test01", "password": "123456"}
    res = RequestUtil.send_request("POST", login_url, json=login_data)

    # 校验登录成功
    assert res.status_code == 200, "登录失败，无法获取token"
    assert res.json()["code"] == 200, f"登录响应错误：{res.json()['msg']}"

    # 提取token并存入上下文
    token = res.json()["data"]["token"]
    user_id = res.json()["data"]["user_id"]
    Context.set("token", token)
    Context.set("user_id", user_id)
    return token


# pytest-html报告配置
def pytest_configure(config):
    config.option.htmlpath = os.path.join(os.path.dirname(__file__), "reports", "test_report.html")
    config.option.self_contained_html = True
