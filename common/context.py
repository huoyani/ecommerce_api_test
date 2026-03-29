class Context:
    """全局上下文，存储跨用例共享的变量"""
    # 类变量：全局唯一
    data = {}

    @classmethod
    def set(cls, key, value):
        """存入变量"""
        cls.data[key] = value

    @classmethod
    def get(cls, key, default=None):
        """获取变量"""
        return cls.data.get(key, default)

    @classmethod
    def clear(cls):
        """清空上下文（避免数据污染）"""
        cls.data.clear()