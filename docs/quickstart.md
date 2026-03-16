# RunBot 快速上手 Demo

一个可以直接复制执行的完整示例，使用免费公开 API（httpbin.org）演示框架核心用法。

---

## 1. 前置准备

```bash
# 一键初始化环境
source setup.sh
```

## 2. 修改配置

编辑 `conf/config.yaml`，把 host 改为 httpbin：

```yaml
current_env: test

test:
  host: https://httpbin.org
  account:
    user: demo_user
    pwd: '123456'
```

## 3. 创建接口定义

### 3.1 请求/响应模型

文件：`apis/demo/models.py`

```python
# --coding:utf-8--
from typing import Optional
from attrs import define, field


@define
class PostDataRequest:
    """httpbin /post 接口请求体"""
    name: str = field(
        default=None,
        metadata={"description": "用户名", "example": "test_user"},
    )
    age: int = field(
        default=None,
        metadata={"description": "年龄", "example": 25},
    )


@define
class PostDataResponse:
    """httpbin /post 接口响应"""
    json: Optional[dict] = field(default=None)
    url: Optional[str] = field(default=None)
    headers: Optional[dict] = field(default=None)
```

### 3.2 接口对象

文件：`apis/demo/apis.py`

```python
# --coding:utf-8--
from typing import Optional
from attrs import define, field
from core.api_object import BaseAPIObject
from core.router import router
from apis.demo.models import PostDataRequest, PostDataResponse


@define(kw_only=True)
@router.get("/get")
class GetAPI(BaseAPIObject):
    """httpbin GET 接口"""
    pass


@define(kw_only=True)
@router.post("/post")
class PostAPI(BaseAPIObject):
    """httpbin POST 接口"""
    request_body: Optional[PostDataRequest] = field(default=None)
    _response_model_cls = PostDataResponse
```

别忘了创建 `apis/demo/__init__.py`（空文件即可）。

### 3.3 模块 conftest（初始化环境）

文件：`testcases/demo/conftest.py`

直接用 pytest 运行时（不走 `rbot run`），需要在 conftest 里初始化 host 和 headers：

```python
# --coding:utf-8--
import pytest
from core.fixture import EnvVars
from core.storage.config import config
from core.storage.cache import cache


@pytest.fixture(scope="session", autouse=True)
def demo_setup():
    """自动初始化 host 和 headers 到 storage"""
    env = EnvVars()
    conf = env.current_env_conf
    config.set("host", conf.get("host", ""))
    config.set("current_env", env.current_env)
    cache.set("headers", {"Content-Type": "application/json"})
    yield
    cache.clear()
```

> 如果通过 `rbot run` 运行，Runner 会自动完成这些初始化，不需要这个 fixture。
> 但为了支持 PyCharm 直接点绿色三角运行/调试，建议每个模块都加上。

### 3.4 数据工厂

文件：`testcases/demo/factory/post_factory.py`

```python
# --coding:utf-8--
from testcases.base_data_factory import BaseDataFactory


class PostFactory(BaseDataFactory):
    @classmethod
    def data(cls) -> list:
        return [
            {"desc": "正常请求", "name": "test_user", "age": 25},
            {"desc": "名称为空", "name": "", "age": 30},
            {"desc": "年龄边界值", "name": cls.fake_name("user_"), "age": 0},
        ]
```

### 3.5 测试用例

文件：`testcases/demo/cases/test_httpbin.py`

```python
# --coding:utf-8--
"""
RunBot 快速上手 Demo
使用 httpbin.org 公开 API 演示框架核心用法
"""
import pytest
from core.base_testcase import BaseTestcase
from core.parametrize import parametrize
from apis.demo.apis import GetAPI, PostAPI
from apis.demo.models import PostDataRequest
from testcases.demo.factory.post_factory import PostFactory


class TestHttpbinDemo(BaseTestcase):

    @pytest.mark.demo
    def test_simple_get(self):
        """最简单的 GET 请求"""
        res = GetAPI().send()
        self.assert_http_code_success(res.status_code)
        self.assert_is_not_none(res.body)

    @pytest.mark.demo
    @parametrize(PostFactory.data())
    def test_post_with_factory(self, data):
        """POST 请求 — 工厂类驱动参数化"""
        body = PostDataRequest(name=data["name"], age=data["age"])
        res = PostAPI(request_body=body).send()
        self.assert_http_code_success(res.status_code)
        # httpbin 会把请求体原样返回在 json 字段里
        self.assert_eq(res.body["json"]["name"], data["name"])
        self.assert_eq(res.body["json"]["age"], data["age"])

    @pytest.mark.demo
    @parametrize([
        {"desc": "内联数据-正常", "name": "inline_user", "age": 18},
        {"desc": "内联数据-大龄", "name": "old_user", "age": 99},
    ])
    def test_post_inline(self, data):
        """POST 请求 — 内联数据驱动"""
        body = PostDataRequest(name=data["name"], age=data["age"])
        res = PostAPI(request_body=body).send()
        self.assert_http_code_success(res.status_code)
        self.assert_contains(res.body["url"], "/post")
```

## 4. 运行

```bash
# 激活虚拟环境（如果还没激活）
source .venv/bin/activate

# 方式一：rbot 命令运行
rbot run -m demo

# 方式二：直接 pytest 运行（更适合调试）
pytest testcases/demo/cases/test_httpbin.py -v -s

# 方式三：只运行某个用例
pytest testcases/demo/cases/test_httpbin.py::TestHttpbinDemo::test_simple_get -v -s
```

## 5. PyCharm 调试

### 5.1 配置 pytest

1. `Settings` → `Tools` → `Python Integrated Tools` → `Default test runner` 选 `pytest`
2. `Settings` → `Project` → `Python Interpreter` 选 `.venv` 里的 Python

### 5.2 运行/调试单个用例

- 打开 `testcases/demo/cases/test_httpbin.py`
- 方法名左侧有绿色三角 ▶，点击选 `Run` 或 `Debug`
- Debug 模式下可以在任意行打断点，查看 `res.body`、`res.status_code` 等变量

### 5.3 运行整个测试类

- 点击 `class TestHttpbinDemo` 左侧的绿色三角 ▶

### 5.4 命令行调试（带详细输出）

```bash
# -v 显示每条用例名，-s 打印 print 输出，--tb=short 简化错误堆栈
pytest testcases/demo/cases/test_httpbin.py -v -s --tb=short
```

## 6. 预期输出

```
testcases/demo/cases/test_httpbin.py::TestHttpbinDemo::test_simple_get PASSED
testcases/demo/cases/test_httpbin.py::TestHttpbinDemo::test_post_with_factory[正常请求] PASSED
testcases/demo/cases/test_httpbin.py::TestHttpbinDemo::test_post_with_factory[名称为空] PASSED
testcases/demo/cases/test_httpbin.py::TestHttpbinDemo::test_post_with_factory[年龄边界值] PASSED
testcases/demo/cases/test_httpbin.py::TestHttpbinDemo::test_post_inline[内联数据-正常] PASSED
testcases/demo/cases/test_httpbin.py::TestHttpbinDemo::test_post_inline[内联数据-大龄] PASSED
```
