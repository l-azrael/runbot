# RunBot

基于 pytest 的企业级接口自动化测试框架。

声明式接口建模 · OpenAPI 代码生成 · AI 辅助生成用例 · 多环境管理 · 可插拔中间件 · 多任务并发执行

---

## 目录

- [框架简介](#框架简介)
- [项目结构](#项目结构)
- [快速开始](#快速开始)
- [核心概念](#核心概念)
  - [声明式接口建模](#声明式接口建模)
  - [路由装饰器](#路由装饰器)
  - [请求发送与响应](#请求发送与响应)
- [测试用例编写](#测试用例编写)
  - [模块目录结构](#模块目录结构)
  - [断言基类](#断言基类)
  - [参数化驱动](#参数化驱动)
  - [数据工厂](#数据工厂)
  - [模块登录](#模块登录)
- [装饰器体系](#装饰器体系)
  - [@dependence 前置依赖](#dependence-前置依赖)
  - [@update 后置刷新](#update-后置刷新)
  - [@async_api 异步轮询](#async_api-异步轮询)
- [中间件系统](#中间件系统)
- [重试机制](#重试机制)
- [多环境管理](#多环境管理)
- [存储管理](#存储管理)
- [Session Hook](#session-hook)
- [测试执行](#测试执行)
- [代码生成](#代码生成)
- [AI 生成用例](#ai-生成用例)
- [HTML 报告](#html-报告)
- [CLI 命令参考](#cli-命令参考)
- [依赖清单](#依赖清单)

---

## 框架简介

RunBot 是一个自研的接口自动化测试框架，核心设计理念：

- **声明式接口建模**：用 `attrs` 类 + `@router` 装饰器定义接口，代码即文档，IDE 全程提示
- **OpenAPI 按需生成**：从 Swagger/OpenAPI 文档一键生成接口模型代码，支持按 tag/路径过滤
- **AI 辅助生成用例**：接口模型结构化后，AI 可直接读取 metadata 生成测试用例和数据工厂
- **可插拔中间件**：日志、重试、自定义逻辑按需插拔，链式执行
- **多环境管理**：一键切换 test/staging/release，支持环境变量覆盖
- **多任务执行**：单进程、多线程、多进程三种模式，Session 生命周期自动管理


## 项目结构

```
runbot/
├── apis/                          # 接口定义层（按业务模块划分）
│   ├── member/
│   │   ├── apis.py                # 接口对象（BaseAPIObject 子类）
│   │   └── models.py              # 请求/响应模型（attrs 类）
│   └── live/
│       ├── apis.py
│       └── models.py
│
├── testcases/                     # 测试用例层
│   ├── base_data_factory.py       # 数据工厂基类（通用随机数据方法）
│   ├── base_login.py              # 模块登录基类
│   ├── conftest.py                # testcases 级公共 fixture
│   ├── member/                    # 业务模块（每个模块独立目录）
│   │   ├── login.py               # 模块登录实现
│   │   ├── conftest.py            # 模块级 fixture（注入登录态）
│   │   ├── cases/                 # 测试用例
│   │   │   └── test_member_tag.py
│   │   ├── factory/               # 数据工厂
│   │   │   └── member_tag_factory.py
│   │   └── data/                  # 静态测试数据（JSON/YAML）
│   │       └── member_tag_cases.json
│   ├── live/                      # 另一个业务模块
│   │   ├── login.py
│   │   ├── conftest.py
│   │   ├── cases/
│   │   ├── factory/
│   │   └── data/
│   └── _legacy/                   # 旧版用例（仅供参考）
│
├── core/                          # 框架核心（全部框架实现）
│   ├── api_object.py              # BaseAPIObject + Response
│   ├── router.py                  # 路由装饰器 @router.get/post/...
│   ├── base_testcase.py           # 断言基类
│   ├── fixture.py                 # 多环境配置 + Session 管理
│   ├── runner.py                  # 测试执行器（单/多线程/多进程）
│   ├── hook_manager.py            # Session Hook
│   ├── exceptions.py              # 自定义异常
│   ├── path.py                    # 路径常量
│   ├── _constants.py              # 全局常量
│   ├── public_method_api.py       # 公共方法统一导出
│   ├── cli/                       # CLI 命令
│   │   ├── main.py                # rbot 入口
│   │   ├── run.py                 # rbot run
│   │   ├── gen.py                 # rbot gen
│   │   └── ai_cmd.py              # rbot ai
│   ├── maker/                     # 代码生成器
│   │   ├── openapi_parser.py      # OpenAPI 文档解析
│   │   ├── code_generator.py      # 代码渲染
│   │   └── templates/             # Jinja2 模板
│   ├── ai/                        # AI 用例生成
│   │   ├── gen_cases.py           # 生成脚本
│   │   └── prompts/               # prompt 模板
│   ├── storage/                   # SQLite 存储管理
│   │   ├── db.py                  # 基类
│   │   ├── config.py              # config 表
│   │   ├── cache.py               # cache 表
│   │   └── schema.py              # schema 表
│   ├── middlewares/                # 中间件系统
│   │   ├── base.py                # 注册与链式执行
│   │   ├── logging_mw.py          # 日志中间件
│   │   └── retry_mw.py            # 重试中间件
│   ├── decorators/                # 装饰器
│   │   ├── dependence.py          # @dependence
│   │   ├── update.py              # @update
│   │   └── async_api.py           # @async_api
│   ├── parametrize/               # 统一参数化
│   │   └── parametrize.py         # @parametrize
│   ├── log/                       # 日志系统
│   │   └── log.py                 # loguru 封装
│   ├── retry/                     # 重试机制
│   │   └── retry.py               # tenacity 封装
│   ├── report/                    # HTML 报告
│   │   ├── html_report.py         # 报告生成器 + pytest 插件
│   │   └── _template.py           # HTML 模板
│   └── db/                        # 外部数据库
│       └── pg.py                  # PostgreSQL 工具类
│
├── app/                           # 应用扩展（预留）
├── conf/
│   ├── config.yaml                # 多环境配置
│   └── runbot.yaml                # 代码生成持久化配置
├── database/
│   └── runbot.db                  # SQLite 数据库
├── logs/                          # 日志文件
├── reports/                       # 测试报告输出
├── tools/                         # 数据工具（预留）
├── docs/                          # 设计文档
├── conftest.py                    # pytest fixture
├── hooks.py                       # Session Hook 注册
├── login.py                       # 全局默认登录逻辑
├── pyproject.toml                 # 包配置 + rbot 入口点
├── pytest.ini                     # pytest 配置
└── requirements.txt               # 依赖清单
```

---

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 安装 rbot 命令

```bash
pip install -e .
```

### 3. 配置环境

编辑 `conf/config.yaml`，填入你的测试环境信息：

```yaml
current_env: test

test:
  host: https://testapi.example.com
  account:
    user: test_user
    pwd: '123456'

staging:
  host: https://stagingapi.example.com
  account:
    user: staging_user
    pwd: '123456'
```

### 4. 编写登录逻辑

RunBot 支持两层登录设计：全局登录（`login.py`）和模块级登录（`testcases/<module>/login.py`）。

全局登录（`login.py`）用于 Runner 启动时的默认登录：

```python
from core.fixture import BaseLogin

class Login(BaseLogin):
    def login(self) -> dict:
        # 调用登录接口，返回响应
        return {}

    def make_headers(self, resp_login: dict) -> dict:
        # 从登录响应中提取 token，构造 headers
        return {"token": "your_token_here"}
```

模块级登录（`testcases/member/login.py`）用于不同模块使用不同账号体系：

```python
from testcases.base_login import ModuleLogin

class MemberLogin(ModuleLogin):
    def login(self) -> dict:
        return {"url": "/api/admin/login", "user": "admin", "pwd": "xxx"}

    def make_headers(self, resp_login: dict) -> dict:
        return {"Authorization": f"Bearer {resp_login['token']}"}
```

### 5. 运行测试

```bash
# 运行所有用例
rbot run

# 按 mark 运行
rbot run -m member

# 切换环境
rbot run -m member -e staging
```

---

## 核心概念

### 声明式接口建模

RunBot 使用 `attrs` 类定义接口模型，每个接口是一个 Python 类。模型的 `metadata` 字段携带业务语义信息，既是文档也是 AI 生成用例的输入。

**请求/响应模型**（`apis/member/models.py`）：

```python
from typing import Optional
from attrs import define, field

@define
class SaveMemberTagAPIRequest:
    name: str = field(
        default=None,
        metadata={
            "description": "标签名称",
            "example": "VIP001",
        },
    )
    type: int = field(
        default=None,
        metadata={
            "description": "标签类型",
            "example": 1,
            "enum": [0, 1],
        },
    )

@define
class SaveMemberTagAPIResponse:
    code: Optional[int] = field(default=None)
    message: Optional[str] = field(default=None)
    data: Optional[dict] = field(default=None)
```

### 路由装饰器

**接口对象**（`apis/member/apis.py`）：

```python
from attrs import define, field
from typing import Optional
from core.api_object import BaseAPIObject
from core.router import router
from apis.member.models import SaveMemberTagAPIRequest, SaveMemberTagAPIResponse

@define(kw_only=True)
@router.post("/api/member/tag/save")
class SaveMemberTagAPI(BaseAPIObject):
    """保存成员标签"""
    request_body: Optional[SaveMemberTagAPIRequest] = field(default=None)
    _response_model_cls = SaveMemberTagAPIResponse
```

`@router` 支持 `.get()` / `.post()` / `.put()` / `.delete()` / `.patch()` 五种 HTTP 方法。

### 请求发送与响应

调用 `.send()` 即可发送请求，返回类型化的 `Response` 对象：

```python
from apis.member.apis import SaveMemberTagAPI
from apis.member.models import SaveMemberTagAPIRequest

body = SaveMemberTagAPIRequest(name="VIP001", type=1)
res = SaveMemberTagAPI(request_body=body).send()

res.status_code      # HTTP 状态码
res.body             # 响应体（dict 或 str）
res.response_model   # 自动映射的响应模型实例
res.elapsed          # 耗时（秒）
```

`send()` 内部自动完成：
1. 从 `config` 表读取 `host`，从 `cache` 表读取 `headers`
2. 将 attrs 字段序列化为请求参数（`request_body` → json，`query_params` → params，`path_params` → URL 模板替换）
3. 经过中间件链（日志 → 重试 → 发送）
4. 自动采集响应 JSON Schema 存入 `schema` 表

---

## 测试用例编写

### 模块目录结构

每个业务模块在 `testcases/` 下有独立目录，内部按职责分为三个子目录：

```
testcases/<module>/
├── __init__.py
├── login.py              # 模块登录实现
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

- `cases/` — 测试用例，pytest 收集的 `test_*.py` 都在这
- `factory/` — 数据工厂，每个接口一个文件，继承 `base_data_factory.py`
- `data/` — 静态数据文件，给 `@parametrize` 文件驱动用

### 断言基类

继承 `BaseTestcase` 获得丰富的断言方法：

```python
from core.base_testcase import BaseTestcase

class TestMemberTag(BaseTestcase):
    def test_save_tag(self):
        res = SaveMemberTagAPI(request_body=body).send()

        self.assert_eq(res.body["code"], 0)              # 等于
        self.assert_neq(res.body["code"], 500)            # 不等于
        self.assert_gt(res.body["total"], 0)              # 大于
        self.assert_contains(res.body, "data")            # 包含
        self.assert_is_not_none(res.body)                 # 非空
        self.assert_http_code_success(res.status_code)    # HTTP 2xx
        self.assert_type(res.body["code"], int)           # 类型检查
        self.assert_schema("SaveMemberTagAPI", res.body)  # JSON Schema 校验
```

`assert_schema` 会从 `schema` 表中取出首次请求时自动采集的 JSON Schema 进行校验，无需手动维护。

### 参数化驱动

统一 `@parametrize` 入口，支持三种驱动方式：

```python
from core.parametrize import parametrize

# 1. 内联驱动 — 直接写数据
@parametrize([
    {"desc": "正常创建", "name": "VIP001", "type": 1},
    {"desc": "名称为空", "name": "", "type": 1},
])
def test_save_tag(self, data):
    ...

# 2. 文件驱动 — JSON/YAML 文件（相对项目根目录）
@parametrize("testcases/member/data/member_tag_cases.json")
def test_save_tag(self, data):
    ...

# 3. 类驱动 — 工厂类生成数据
@parametrize(MemberTagFactory.data())
def test_save_tag(self, data):
    ...
```

数据格式统一为 `list[dict]`，其中 `desc` 字段自动作为 pytest 用例 ID。

数据文件示例（`testcases/member/data/member_tag_cases.json`）：

```json
[
  {"desc": "正常创建VIP标签", "name": "VIP001", "type": 1, "expected_code": 0},
  {"desc": "名称含特殊字符", "name": "VIP@#$", "type": 1, "expected_code": 0},
  {"desc": "类型为0创建失败", "name": "BAD001", "type": 0, "expected_code": 1}
]
```

### 数据工厂

继承 `BaseDataFactory` 实现 `data()` 方法，返回参数化数据列表。每个模块的工厂文件放在 `testcases/<module>/factory/` 目录下：

```python
# testcases/member/factory/member_tag_factory.py
from testcases.base_data_factory import BaseDataFactory

class MemberTagFactory(BaseDataFactory):
    @classmethod
    def data(cls) -> list:
        return [
            {"desc": "正常创建标签", "name": cls.fake_name("VIP_"), "type": 1},
            {"desc": "边界值-名称最长50字符", "name": "x" * 50, "type": 1},
            {"desc": "非法类型值", "name": cls.fake_name("tag_"), "type": 99},
            {"desc": "名称为空字符串", "name": "", "type": 1},
        ]
```

`BaseDataFactory`（`testcases/base_data_factory.py`）提供常用随机数据方法：`fake_str()` / `fake_name()` / `fake_int()` / `fake_phone()`。

### 模块登录

不同业务模块可能使用不同的账号体系（管理后台 vs 用户端 vs 开放平台），甚至同一模块内不同用例需要不同角色。

每个模块在 `login.py` 中实现自己的登录类，继承 `testcases/base_login.py` 的 `ModuleLogin`：

```python
# testcases/member/login.py
from testcases.base_login import ModuleLogin

class MemberLogin(ModuleLogin):
    """管理后台登录"""
    def login(self) -> dict:
        return {"url": "/api/admin/login", "user": "admin", "pwd": "xxx"}

    def make_headers(self, resp_login: dict) -> dict:
        return {"Authorization": f"Bearer {resp_login['token']}"}

class MemberVipLogin(ModuleLogin):
    """VIP 用户登录（同模块不同角色）"""
    def login(self) -> dict:
        return {"url": "/api/user/login", "user": "vip_user", "pwd": "xxx"}

    def make_headers(self, resp_login: dict) -> dict:
        return {"Authorization": f"Bearer {resp_login['token']}", "X-Role": "vip"}
```

在模块的 `conftest.py` 中通过 fixture 注入登录态：

```python
# testcases/member/conftest.py
import pytest
from testcases.member.login import MemberLogin, MemberVipLogin

@pytest.fixture(scope="module")
def member_session():
    login = MemberLogin()
    return login

@pytest.fixture(scope="module")
def vip_session():
    login = MemberVipLogin()
    return login
```

用例中按需使用：

```python
class TestMemberTag(BaseTestcase):
    def test_save_tag(self, member_session):
        # 用管理后台身份
        res = SaveMemberTagAPI(request_body=body).send()
        ...

    def test_vip_view_tag(self, vip_session):
        # 用 VIP 用户身份
        res = GetMemberTagAPI().send()
        ...
```

---

## 装饰器体系

### @dependence 前置依赖

在目标接口调用前，先调用依赖接口，结果自动存入 cache。若 cache 中已存在则跳过。

```python
from core.decorators import dependence

# 方式一：传入可调用对象
@dependence(get_cluster_list, "cluster_id", cluster_type="hpc")
def create_instance(self, test_data):
    cluster_id = cache.get_by_jsonpath("cluster_id", "$..cluster_id")
    ...

# 方式二：传入字符串（同类方法）
@dependence("ClassName.method_name", "var_name", imp_module="apis.member.apis")
def my_api(self, data):
    ...
```

### @update 后置刷新

目标接口调用后，自动重新调用原依赖接口刷新 cache 中的值：

```python
from core.decorators import update

@update("cluster_nodes")
def add_cluster_nodes(self, test_data):
    ...
```

### @async_api 异步轮询

接口调用后，从响应中提取任务 ID，传给轮询函数等待完成：

```python
from core.decorators import async_api

@async_api(wait_job, "$.job_id")
def submit_job(self, test_data):
    ...

# 带条件执行
@async_api(wait_job, "$.job_id",
           condition={"expr": "$.ret_code", "expected_value": 0})
def submit_job(self, test_data):
    ...
```

---

## 中间件系统

请求/响应链路可插拔，通过 `@middleware` 装饰器注册，按 `priority` 从高到低执行。

```
请求 → [logging_mw(900)] → [retry_mw(800)] → [自定义(700)] → HTTP 发送 → 响应
```

内置中间件：
- `logging_mw`（priority=900）：自动记录请求/响应日志，附加到 allure 报告
- `retry_mw`（priority=800）：对 5xx 状态码自动重试（默认 3 次，间隔 2s）

自定义中间件示例：

```python
from core.middlewares.base import middleware

@middleware(name="perf", priority=700)
def perf_mw(request, call_next):
    import time
    start = time.time()
    response = call_next(request)
    elapsed = time.time() - start
    if elapsed > 2.0:
        print(f"慢接口告警: {request['url']} 耗时 {elapsed:.2f}s")
    return response
```

---

## 重试机制

三个层次，基于 tenacity：

```python
# 1. HTTP 请求级 — 类属性控制（通过 retry_mw 中间件）
class MyAPI(BaseAPIObject):
    IS_HTTP_RETRY = True
    HTTP_RETRY_COUNTS = 3
    HTTP_RETRY_INTERVAL = 2

# 2. 业务级 — 装饰器
from core.retry.retry import retry

@retry(counts=3, interval=2, retry_condition=lambda r: r.get("code") != 0)
def my_api_method():
    ...

# 3. 代码片段级 — 上下文管理器
from core.retry import Retry

for attempt in Retry(counts=3, interval=2, exception_type=TimeoutError):
    with attempt:
        result = some_operation()
```

---

## 多环境管理

### 配置文件

`conf/config.yaml` 支持多环境，结构如下：

```yaml
current_env: test          # 当前激活环境

test:
  host: https://testapi.example.com
  account:
    user: test_user
    pwd: '123456'

staging:
  host: https://stagingapi.example.com
  account:
    user: staging_user
    pwd: '123456'

release:
  host: https://api.example.com
  account:
    user: release_user
    pwd: '123456'
```

### 切换方式（优先级从高到低）

```bash
# 1. 环境变量（最高优先级，适合 CI/CD）
RUNBOT_ENV=release rbot run -m member

# 2. CLI 参数
rbot run -m member -e release

# 3. 修改 config.yaml 中的 current_env（默认）
```

### 代码中读取

```python
from core.fixture import EnvVars, ReadConfig

env = EnvVars()
env.current_env           # "test"
env.current_env_conf      # {"host": "...", "account": {...}}

conf = ReadConfig()
conf.get("test", "host")  # "https://testapi.example.com"
```

---

## 存储管理

基于 SQLite（`database/runbot.db`），三张表，线程安全，全局单例。

| 表名 | 生命周期 | 用途 |
|---|---|---|
| `config` | 持久化 | 全局配置（host、账号、当前环境等） |
| `cache` | 会话级 | 临时变量、接口依赖数据、headers |
| `schema` | 持久化 | 接口响应 JSON Schema（自动采集） |

```python
from core.storage import config, cache, schema

# config 表
config.set("host", "https://testapi.example.com")
config.get("host")
config.get_all()

# cache 表
cache.set("auth_token", "Bearer xxx")
cache.get("auth_token")
cache.get_by_jsonpath("cluster_list", "$..cluster_id")

# schema 表（通常由框架自动写入）
schema.get("SaveMemberTagAPI")
```

---

## Session Hook

在 `hooks.py` 中注册 Session 级别的前置/后置逻辑：

```python
from core.hook_manager import hook

@hook
def setup_test_data():
    """普通函数：作为 pre-hook 执行"""
    print("准备测试数据...")

@hook
def db_cleanup():
    """生成器函数：yield 前为 pre-hook，yield 后为 post-hook"""
    print("Session 开始，初始化数据库...")
    yield
    print("Session 结束，清理数据库...")
```

执行顺序：`登录 → 配置加载 → pre-hooks → pytest 执行 → post-hooks → 清理`

---

## 测试执行

### 三种模式

```python
from core.runner import Runner, ThreadsRunner, ProcessesRunner

# 单进程
Runner().run(["-m", "member"], login=Login())

# 多线程（按 mark 分配线程）
ThreadsRunner().run(["-m member", "-m live"], login=Login())

# 多进程
ProcessesRunner().run(["-m member", "-m live"], login=Login(), process_count=4)
```

### Session 生命周期

```
登录 → 加载配置到 config 表 → 执行 pre-hooks
    → pytest.main() 执行用例
    → 执行 post-hooks → 生成报告 → 清空 cache 表
```

---

## 代码生成

从 OpenAPI/Swagger 文档自动生成接口模型代码。

### 命令行

```bash
# 从 URL 生成
rbot gen -s http://api.example.com/openapi.json -o apis/member

# 从本地文件生成
rbot gen -s docs/api.json -o apis/member

# 按 tag 过滤
rbot gen -s docs/api.json -o apis/member --tag member

# 按路径前缀过滤
rbot gen -s docs/api.json -o apis/live --path /api/live
```

### 持久化配置

在 `conf/runbot.yaml` 中配置默认参数，之后直接 `rbot gen` 即可：

```yaml
openapi:
  spec: http://api.example.com/openapi.json
  output: apis/member
  tag: member
  path_prefix: /api
```

### 生成结果

```
apis/member/
├── __init__.py
├── apis.py      # BaseAPIObject 子类
└── models.py    # attrs 请求/响应模型
```

---

## AI 生成用例

根据接口定义自动生成测试用例和数据工厂。支持三种方式。

### 方式一：Kiro Steering（推荐）

在 Kiro 聊天中使用 `#gen-testcase` 上下文，直接对话生成。无需 API Key，零成本：

```
#gen-testcase 帮我给 member 模块生成用例
```

Kiro 会按照项目规范自动生成到正确的目录结构（cases/factory/data）。

### 方式二：rbot ai 命令

适合 CI 环境或批量生成。支持 OpenAI、Claude、本地模型（兼容 OpenAI 协议）。

```bash
# 设置 API Key
export OPENAI_API_KEY=sk-xxx

# 生成用例 + 数据工厂
rbot ai --api apis/member/apis.py --output testcases/member/

# 只生成用例
rbot ai --api apis/member/apis.py --output testcases/member/ --type testcase

# 只生成数据工厂
rbot ai --api apis/member/apis.py --output testcases/member/ --type data

# 只看 prompt 不调用 LLM（调试用）
rbot ai --api apis/member/apis.py --output testcases/member/ --dry-run
```

生成结果自动按目录结构输出：

```
testcases/member/
├── cases/test_member_ai.py        # 用例文件
└── factory/member_factory_ai.py   # 数据工厂
```

### 本地模型

```bash
export AI_BASE_URL=http://localhost:11434/v1
export AI_MODEL=qwen2.5-coder
rbot ai --api apis/member/apis.py --output testcases/member/
```

### 生成质量提升

接口模型的 `metadata` 越完整，AI 生成质量越高。建议填写：

```python
@define
class SaveMemberTagRequest:
    name: str = field(metadata={
        "description": "标签名称",
        "example": "VIP001",
        "constraints": "长度 1-50，不能为空"
    })
    type: int = field(metadata={
        "description": "标签类型",
        "enum": [0, 1],
        "enum_desc": {"0": "创建失败", "1": "正常创建"},
        "business_rules": "type=1 为正常标签，type=0 为失败标签"
    })
```

---

## HTML 报告

RunBot 内置自包含 HTML 报告生成器，测试执行后自动生成 `reports/runbot.html`。

报告功能：
- 概述面板：开始/结束时间、运行时长、通过/失败/错误/跳过统计
- 进度条可视化各项比率
- 按状态筛选用例（通过/失败/错误/跳过/所有）
- 点击「查看详情」弹窗显示用例日志和错误堆栈

同时保留 allure 报告支持，allure 数据输出到 `reports/json/`，可通过 `allure generate` 生成。

---

## CLI 命令参考

```bash
# 查看版本
rbot --version

# 运行测试
rbot run                           # 运行全部用例
rbot run -m member                 # 按 mark 运行
rbot run -m member -m live         # 多个 mark
rbot run -e staging                # 切换环境
rbot run --mt                      # 多线程模式
rbot run --mp                      # 多进程模式
rbot run -l debug                  # 设置日志级别
rbot run --no-allure               # 不生成 allure 报告

# 代码生成
rbot gen -s <spec> -o <output>     # 从 OpenAPI 生成
rbot gen -s <spec> -o <output> --tag member
rbot gen -s <spec> -o <output> --path /api/live
rbot gen                           # 读取 conf/runbot.yaml 配置

# AI 生成用例
rbot ai --api <file> --output <dir>
rbot ai --api <file> --output <dir> --type testcase
rbot ai --api <file> --output <dir> --dry-run
```

---

## 依赖清单

| 包名 | 用途 |
|---|---|
| pytest | 测试框架 |
| attrs | 声明式接口建模 |
| requests | HTTP 客户端 |
| pyyaml | YAML 配置解析 |
| loguru | 日志系统 |
| tenacity | 重试机制 |
| jinja2 | 代码生成模板 |
| click | CLI 框架 |
| emoji | 日志美化 |
| allure-pytest | Allure 报告 |
| jsonpath | JSONPath 数据提取 |
| jsonschema | JSON Schema 校验 |
| genson | JSON Schema 自动生成 |
| psycopg2-binary | PostgreSQL 连接 |
| pandas / openpyxl | 数据处理 |
| openai | AI 用例生成（可选） |
