import os
import pytest

if __name__ == '__main__':
    # 1. 运行用例
    pytest.main([
        "./testcases/",
        "--alluredir=./report",
        "-v"
    ])

    # 2. 生成报告
    os.system("allure generate ./report -o ./report_html --clean")

    # 3. 打开报告
    os.system("allure open ./report_html")