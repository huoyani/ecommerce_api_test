class RequestFailedError(Exception):
    """请求失败异常"""
    pass

class AssertFailedError(Exception):
    """断言失败异常"""
    pass

class DataExtractError(Exception):
    """数据提取失败异常"""
    pass