import os
import yaml


def load_yaml_file(file_path):
    """读取单个yaml文件"""
    if not os.path.exists(file_path):
        raise FileExistsError(f"yaml文件不存在：{file_path}")
    with open(file_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_yaml_dir(dir_path):
    """读取目录下所以yaml文件，合并数据"""
    all_data = []
    for file in os.listdir(dir_path):
        if file.endswith(".yaml") or file.endswith(".yml"):
            file_path = os.path.join(dir_path, file)
            data = load_yaml_file(file_path)
            if isinstance(data, list):
                all_data.extend(data)
            else:
                all_data.append(data)
    return all_data
