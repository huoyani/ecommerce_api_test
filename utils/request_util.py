import re
import requests
from common.context import Context
from common.exceptions import RequestFailedError


class RequestUtil:
    """http请求工具类"""

    @staticmethod
    def replace_placeholder(data):
        """递归替换数据中的${变量名}占位符"""
        if isinstance(data, dict):
            new_data = {}
            for k, v in data.items():
                new_data[k] = RequestUtil.replace_placeholder(v)
            return new_data
        elif isinstance(data, str):
            # 正则匹配${}
            pattern = r"\$\{(.*?)\}"
            vars = re.findall(pattern, data)
            for var in vars:
                value = Context.get(var)
                if value is not None:
                    data = data.replace(f"${{{var}}}", str(value))
            return data
        else:
            return data

    @staticmethod
    def send_request(method,url,headers=None,params=None,json=None,timeout=10):
        """发送http请求"""
        #替换占位符
        headers=RequestUtil.replace_placeholder(headers or {})
        params=RequestUtil.replace_placeholder(params or {})
        json=RequestUtil.replace_placeholder(json or {})
        try:
            response=requests.request(
                method=method.upper(),
                url=url,
                headers=headers,
                params=params,
                json=json,
                timeout=timeout
            )
            #打印请求/响应日志
            print(f"\n====请求信息====")
            print(f"方法：{method.upper()},URL:{url}")
            print(f"请求头：{headers}")
            print(f"请求体：{json}")
            print(f"====响应信息====")
            print(f"状态码：{response.status_code}")
            print(f"响应体：{response.text}")
            return response
        except Exception as e:
            raise RequestFailedError(f"请求失败：{str(e)}")
