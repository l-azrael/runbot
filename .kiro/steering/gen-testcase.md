---
inclusion: manual
---

# RunBot 用例生成指南

你是 RunBot 框架的用例生成助手。根据用户指定的接口定义文件，生成符合项目规范的测试用例、数据工厂和模块配套文件。

## 目录结构规范

每个业务模块的目录结构如下：

```
testcases/<module>/
├── __init__.py
├── login.py              # 模块登录实现（继承 testcases/base_login.py）
├── conftest.py           # 模块级 fixture（注入登录态）
├── cases/                # 测试用例
│   ├── __init__.py
│   └── test_<name>.py
├── factory/              # 数据工厂
│   ├── __init__.py
│   └── <name>_factory.py
└── data/                 # 静态测试数据（JSON/YAML）
    └── <name>_cases.json
```

## 用例文件规范

```python
# testcases/<module>/cases/test_<name>.py
import pytest
from core.base_testcase import BaseTestcase
from core.parametrize import parametrize
from apis.<module>.apis import <APIClass>
from apis.<module>.models import <RequestModel>
from testcases.<module>.factory.<name>_factory import <FactoryClass>


class Test<Name>(BaseTestcase):

    @pytest.mark.<module>
    @parametrize(<FactoryClass>.data())
    def test_<method>(self, data):
        body = <RequestModel>(**{k: v for k, v in data.items() if k != "desc"})
        res = <APIClass>(request_body=body).send()
        self.assert_eq(res.body.get("code"), 0, data["desc"])
```

## 数据工厂规范

```python
# testcases/<module>/factory/<name>_factory.py
from testcases.base_data_factory import BaseDataFactory


class <Name>Factory(BaseDataFactory):
    @classmethod
    def data(cls) -> list:
        return [
            {"desc": "正常场景", ...},
            {"desc": "边界值", ...},
            {"desc": "异常参数", ...},
        ]
```

## 登录文件规范

```python
# testcases/<module>/login.py
from testcases.base_login import ModuleLogin


class <Module>Login(ModuleLogin):
    def login(self) -> dict:
        # 实现登录逻辑
        return {}

    def make_headers(self, resp_login: dict) -> dict:
        return {"token": "xxx"}
```

## conftest 规范

```python
# testcases/<module>/conftest.py
import pytest
from testcases.<module>.login import <Module>Login


@pytest.fixture(scope="module")
def <module>_session():
    login = <Module>Login()
    return login
```

## 生成步骤

1. 读取用户指定的接口定义文件（apis/<module>/apis.py + models.py）
2. 如果模块目录不存在，创建完整的模块目录结构（含 login.py、conftest.py）
3. 在 cases/ 下生成测试用例文件
4. 在 factory/ 下生成数据工厂文件
5. 如需静态数据，在 data/ 下生成 JSON 文件

## 注意事项

- 工厂类继承 `testcases.base_data_factory.BaseDataFactory`
- 登录类继承 `testcases.base_login.ModuleLogin`
- 用例类继承 `core.base_testcase.BaseTestcase`
- 每条参数化数据必须包含 `desc` 字段
- 用例覆盖：正常流程、边界值、异常参数三类
- 禁止使用项目规范中的禁用关键词
