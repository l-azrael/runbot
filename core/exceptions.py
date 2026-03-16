# --coding:utf-8--

class RunBotException(Exception):
    pass


class FileNotFound(FileNotFoundError, RunBotException):
    def __init__(self, path):
        self.path = path

    def __str__(self):
        return f'文件未找到：{self.path}'


class SchemaNotFound(RunBotException):
    def __init__(self, api_name):
        self.api_name = api_name

    def __str__(self):
        return f'jsonschema未找到：{self.api_name}'


class ConfKeyError(RunBotException):
    def __init__(self, key_name):
        self.key_name = key_name

    def __str__(self):
        return f'config.yaml 中未找到 key：{self.key_name}'


class YamlKeyError(RunBotException):
    def __init__(self, file_path, key_name):
        self.file_path = file_path
        self.key_name = key_name

    def __str__(self):
        return f'数据文件（{self.file_path}）中未找到 key：{self.key_name}'


class HttpRequestError(RunBotException):
    def __init__(self, status_code):
        self.status_code = status_code

    def __str__(self):
        return f'请求失败，状态码：{self.status_code}'


class JsonPathExtractFailed(RunBotException):
    def __init__(self, res, jsonpath_expr):
        self.res = res
        self.jsonpath_expr = jsonpath_expr

    def __str__(self):
        return f'JSONPath 提取失败\n表达式：{self.jsonpath_expr}\n数据源：{self.res}'


class LoginError(RunBotException):
    def __str__(self):
        return "run() 未传入 Login 对象"
