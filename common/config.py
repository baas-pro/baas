import json
import os
import sys


def load_ba_config(con):
    with open(config_filepath(con), 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data


def save_ba_config(con, data):
    with open(config_filepath(con), 'w', encoding='utf-8') as f:
        f.write(json.dumps(data, indent=4, ensure_ascii=False, sort_keys=False))


def get_froze_path(fp):
    base_path = ''
    # 如果我们是在 PyInstaller 打包后的版本中运行，那么改变 base_path 到正确的目录
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    return os.path.join(base_path, fp)


def resource_path(relative_path):
    if hasattr(sys, 'frozen'):
        # 当使用 PyInstaller 打包后
        if sys.platform == 'darwin':
            # 对于 macOS, 'sys.executable' 将指向 '.app' 中的 'MacOS' 目录内的可执行文件
            # 所以我们需要往上跳转三层目录找到 '.app' 包的根目录
            base = os.path.abspath(os.path.join(os.path.dirname(sys.executable), '..', '..', '..'))
        else:
            # 其他平台，或者其他情况下保守处理，默认与Windows相同处理
            base = os.path.dirname(sys.executable)
    else:
        # 在开发环境中，直接返回脚本所在目录
        base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, relative_path)


def config_filepath(con):
    return os.path.join(resource_path("configs"), '{0}.json'.format(con))


def config_dir():
    return resource_path("configs")


def get_runtime_path():
    return resource_path("runtime")


def get_debug_dir():
    return os.path.join(get_runtime_path(), 'debug')


def get_debug_file(name):
    return os.path.join(get_debug_dir(), '{0}.png'.format(name))


def get_ss_path(self):
    return os.path.join(get_runtime_path(), 'ss_{0}.png'.format(self.con))


def config_deep_update(source, destination):
    """
    递归地更新嵌套字典和列表结构。

    Parameters:
    source (dict): 源数据，包含要更新或添加到目标数据中的键值对。
    destination (dict): 目标数据，将被源数据更新。

    Returns:
    dict: 更新后的目标数据。
    """
    for key, value in source.items():
        if isinstance(value, dict):
            # 如果当前值是一个字典，进行递归更新。如果目标字典中没有相应的key，
            # 则自动创建一个新的空字典，并开始递归更新。
            node = destination.setdefault(key, {})
            config_deep_update(value, node)
        elif isinstance(value, list) and all(isinstance(item, dict) for item in value):
            # 如果当前值是一个列表，并且列表中的所有元素都是字典，
            # 则对列表中的每个字典进行处理。
            if not destination.get(key):
                # 如果目标数据中不存在该key，或者key对应的值为空列表，
                # 那么直接将源数据中的列表复制到目标数据中。
                destination[key] = value.copy()
            else:
                # 如果目标数据中存在该key，并且不是空列表，
                # 则逐个更新目标列表中每个已有的字典元素。
                # 注意：不会在目标列表中添加任何新的字典元素。
                for i, dest_item in enumerate(destination[key]):
                    if i < len(value):
                        # 如果源列表长度大于等于目标列表，更新对应位置的字典。
                        source_item = value[i]
                        config_deep_update(source_item, dest_item)
        else:
            # 对于普通键值对，如果目标数据中不存在该键，则设置它的值为源数据中的值。
            destination.setdefault(key, value)
    return destination


def config_migrate(self, file_path1):
    """
    比较两个 JSON 文件的键，如果文件1有而文件2没有的键，用文件1的内容更新文件2。

    参数:
        file_path1 (str): 第一个JSON文件路径。
        file_path2 (str): 第二个JSON文件路径。

    返回:
        None: 直接修改文件2中的内容并保存
    """

    with open(file_path1, 'r', encoding='utf-8') as f:
        src_data = json.load(f)
    dst_data = load_ba_config(self.con)
    updated_dst_data = config_deep_update(src_data, dst_data)
    save_ba_config(self.con, updated_dst_data)
