# RunBot

基于 pytest 的接口自动化测试框架。

声明式接口建模 · API 代码生成 · AI 辅助生成用例 · 多环境动态切换 · SQLite 状态管理 · 流式中间件 · 多任务并发执行

---

## 特色亮点

| 特性 | 说明 |
|---|---|
| 声明式接口建模 | 用 `attrs` 类定义接口，字段自带 metadata（描述、示例、枚举），代码即文档，IDE 全程提示 |
| 三种参数化驱动 | 内联数据、JSON/YAML 文件、工厂类，统一 `@parametrize` 入口，一行切换 |
| SQLite 状态管理 | host/headers/token 等运行时状态存入 SQLite，接口调用自动读取，无需手动传参 |
| 多环境动态切换 | `config.yaml` 定义多套环境，CLI/环境变量/配置文件三级优先级，一键切换 |
| 模块级独立登录 | 每个业务模块有自己的 `login.py`，不同模块可用不同账号体系，互不干扰 |
| JSON Schema 自动校验 | 首次请求自动采集响应 Schema 存入 SQLite，后续用例直接 `assert_schema` 校验 |
| OpenAPI 代码生成 | 从 Swagger 文档一键生成 `apis.py` + `models.py`，支持按 tag/路径过滤 |
| AI 辅助生成用例 | 接口 metadata 结构化后，AI 可直接读取生成测试用例和数据工厂 |
| 可插拔中间件 | 日志、重试、自定义逻辑按需插拔，链式执行（待优化） |
| 一键环境初始化 | `source setup.sh` 自动检测 Python、创建虚拟环境、安装依赖、注册 `rbot` 命令 |

---

## 目录

- [快速开始](#快速开始)
- [项目结构](#项目结构)
- [环境配置与动态切换](#环境配置与动态切换)
- [声明式接口建模（attrs）](#声明式接口建模attrs)
- [三种参数化驱动](#三种参数化驱动)
- [SQLite 状态管理](#sqlite-状态管理)
- [模块级登录设计](#模块级登录设计)
- [测试用例编写](#测试用例编写)
- [装饰器体系](#装饰器体系)
- [中间件系统](#中间件系统)
- [重试机制](#重试机制)
- [代码生成](#代码生成)
- [AI 生成用例](#ai-生成用例)
- [测试执行](#测试执行)
- [HTML 报告](#html-报告)
- [CLI 命令参考](#cli-命令参考)

---

## 快速开始

### 一键初始化（推荐）

```bash
source setup.sh
```

`setup.sh` 会自动完成以下步骤：

1. 检测 Python >= 3.10（扫描 PATH + macOS 常见安装路径）
2. 创建 `.venv` 虚拟环境（已存在则跳过）
3. 激活虚拟环境
4. 升级 pip + 安装 `requirements.txt` 依赖
5. `pip install -e .` 注册 `rbot` 命令
6. 验证 `rbot` 命令可用
7. 检查 `conf/config.yaml`（不存在则创建示例）
8. 提示 allure 安装（可选）

所有步骤幂等，可重复执行。脚本不会关闭终端。

### 手动安装

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -e .
```

### 验证安装

```bash
rbot --version
# rbot, version 1.0.0
```

### 运行 Demo

```bash
rbot run -m demo
# 或直接 pytest
pytest testcases/demo/cases/test_httpbin.py -v -s
```

Demo 使用 httpbin.org 公开 API，无需任何配置即可运行，6 条用例覆盖框架核心用法。

---

## 项目结构

```
runbot/
├── apis/                          # 接口定义层（按业务模块划分）
│   ├── demo/                      # Demo 模块（httpbin）
│   │   ├── apis.py                # 接口对象
│   │   └── models.py              # 请求/响应模型
│   ├── member/                    # 业务模块示例
│   │   ├── apis.py
│   │   └── models.py
│   └── live/
│       ├── apis.py
│       └── models.py
│
├── testcases/                     # 测试用例层
│   ├── base_data_factory.py       # 数据工厂基类
│   ├── base_login.py              # 模块登录基类
│   ├── conftest.py                # testcases 级公共 fixture
│   ├── demo/                      # Demo 模块
│   │   ├── conftest.py            # 模块 fixture（初始化环境）
│   │   ├── cases/test_httpbin.py  # 测试用例
│   │   ├── factory/post_factory.py
│   │   └── data/post_data.json    # JSON 文件驱动数据
│   ├── member/                    # 业务模块
│   │   ├── login.py               # 模块登录实现
│   │   ├── conftest.py            # 模块 fixture（注入登录态）
│   │   ├── cases/
│   │   ├── factory/
│   │   └── data/
│   └── _legacy/                   # 旧版用例（仅供参考）
│
├── core/                          # 框架核心
│   ├── api_object.py              # BaseAPIObject + Response
│   ├── router.py                  # @router.get/post/put/delete/patch
│   ├── base_testcase.py           # 断言基类
│   ├── fixture.py                 # 多环境配置 + Session 管理
│   ├── runner.py                  # 执行器（单/多线程/多进程）
│   ├── hook_manager.py            # Session Hook
│   ├── storage/                   # SQLite 存储（config/cache/schema）
│   ├── middlewares/               # 中间件（日志/重试/自定义）
│   ├── decorators/                # @dependence/@update/@async_api
│   ├── parametrize/               # 统一 @parametrize
│   ├── cli/                       # rbot 命令
│   ├── maker/                     # OpenAPI 代码生成
│   ├── ai/                        # AI 用例生成
│   ├── log/                       # 日志系统
│   ├── retry/                     # 重试机制
│   └── report/                    # HTML 报告
│
├── conf/config.yaml               # 多环境配置
├── database/runbot.db             # SQLite 数据库
├── login.py                       # 全局默认登录
├── hooks.py                       # Session Hook 注册
├── conftest.py                    # pytest 根 fixture
├── setup.sh                       # 一键环境初始化
├── pyproject.toml                 # 包配置 + rbot 入口点
└── requirements.txt               # 依赖清单
```

---

## 环境配置与动态切换

### 配置文件

`conf/config.yaml` 定义多套环境，每套环境包含 host、账号等信息：

```yaml
current_env: test          # 当前激活环境

test:
  host: https://httpbin.org
  account:
    user: test_user
    pwd: '123456'
  login:
    web_token: your_token_here

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

### 三级优先级切换

```bash
# 1. 环境变量（最高优先级，适合 CI/CD）
RUNBOT_ENV=release rbot run -m member

# 2. CLI 参数
rbot run -m member -e staging

# 3. config.yaml 中的 current_env（默认）
```

### 运行时自动注入 SQLite

框架启动时，`SetUpSession` 会把当前环境的配置写入 SQLite：

```
config.yaml → SetUpSession → SQLite config 表
                                ├── host = "https://httpbin.org"
                                ├── current_env = "test"
                                └── account = {"user": "test_user", ...}
```

之后所有接口调用自动从 SQLite 读取 host 和 headers，无需手动传参：

```python
# 接口调用时，BaseAPIObject.send() 内部自动执行：
host = config.get("host")           # 从 SQLite config 表读取
headers = cache.get("headers")       # 从 SQLite cache 表读取
url = host + route["path"]           # 拼接完整 URL
```

切换环境只需改一个地方，所有接口自动生效。

---

## 声明式接口建模（attrs）

### 为什么用 attrs

| 优势 | 说明 |
|---|---|
| 类型安全 | 字段有明确类型，IDE 自动补全和类型检查 |
| metadata 元数据 | 每个字段可携带 description、example、enum 等业务语义 |
| 自动序列化 | `attr.asdict()` 一行转 dict，直接作为请求体 |
| AI 友好 | metadata 结构化后，AI 可直接读取生成测试数据 |
| 代码即文档 | 接口定义本身就是最准确的文档 |

### 请求/响应模型

```python
# apis/member/models.py
from typing import Optional
from attrs import define, field

@define
class SaveMemberTagAPIRequest:
    name: str = field(
        default=None,
        metadata={
            "description": "标签名称",
            "example": "VIP001",
            "constraints": "长度 1-50，不能为空",
        },
    )
    type: int = field(
        default=None,
        metadata={
            "description": "标签类型",
            "example": 1,
            "enum": [0, 1],
            "enum_desc": {"0": "失败", "1": "正常"},
        },
    )

@define
class SaveMemberTagAPIResponse:
    code: Optional[int] = field(default=None)
    message: Optional[str] = field(default=None)
    data: Optional[dict] = field(default=None)
```

### 接口对象

```python
# apis/member/apis.py
from attrs import define, field
from typing import Optional
from core.api_object import BaseAPIObject
from core.router import router

@define(kw_only=True)
@router.post("/api/member/tag/save")
class SaveMemberTagAPI(BaseAPIObject):
    """保存成员标签"""
    request_body: Optional[SaveMemberTagAPIRequest] = field(default=None)
    _response_model_cls = SaveMemberTagAPIResponse
```

### 调用方式

```python
body = SaveMemberTagAPIRequest(name="VIP001", type=1)
res = SaveMemberTagAPI(request_body=body).send()

res.status_code      # HTTP 状态码
res.body             # 响应体（dict）
res.response_model   # 自动映射的响应模型实例
res.elapsed          # 耗时（秒）
```

`send()` 内部自动完成：host 拼接 → headers 注入 → attrs 序列化 → 中间件链 → Schema 采集。

---

## 三种参数化驱动

统一 `@parametrize` 入口，数据格式统一为 `list[dict]`，`desc` 字段自动作为 pytest 用例 ID。

### 1. 内联驱动 — 直接写数据

适合数据量少、逻辑简单的场景：

```python
@parametrize([
    {"desc": "正常创建", "name": "VIP001", "type": 1},
    {"desc": "名称为空", "name": "", "type": 1},
])
def test_save_tag(self, data):
    body = SaveMemberTagAPIRequest(name=data["name"], type=data["type"])
    res = SaveMemberTagAPI(request_body=body).send()
    self.assert_http_code_success(res.status_code)
```

### 2. JSON 文件驱动 — 数据与代码分离

适合数据量大、需要非开发人员维护数据的场景：

```python
# 传入相对项目根目录的文件路径
@parametrize("testcases/member/data/member_tag_cases.json")
def test_save_tag(self, data):
    ...
```

JSON 文件示例（`testcases/member/data/member_tag_cases.json`）：

```json
[
  {"desc": "正常创建VIP标签", "name": "VIP001", "type": 1},
  {"desc": "名称含特殊字符", "name": "VIP@#$", "type": 1},
  {"desc": "类型为0", "name": "BAD001", "type": 0}
]
```

也支持 YAML 格式（`.yaml` / `.yml`）。

### 3. 工厂类驱动 — 动态生成数据

适合需要随机数据、边界值组合、复杂逻辑的场景：

```python
@parametrize(MemberTagFactory.data())
def test_save_tag(self, data):
    ...
```

工厂类示例：

```python
# testcases/member/factory/member_tag_factory.py
from testcases.base_data_factory import BaseDataFactory

class MemberTagFactory(BaseDataFactory):
    @classmethod
    def data(cls) -> list:
        return [
            {"desc": "正常创建", "name": cls.fake_name("VIP_"), "type": 1},
            {"desc": "边界值-50字符", "name": "x" * 50, "type": 1},
            {"desc": "非法类型", "name": cls.fake_name("tag_"), "type": 99},
        ]
```

`BaseDataFactory` 提供 `fake_str()` / `fake_name()` / `fake_int()` / `fake_phone()` 等随机数据方法。

---

## SQLite 状态管理

框架使用 SQLite（`database/runbot.db`）管理运行时状态，三张表各司其职：

| 表名 | 生命周期 | 用途 | 典型数据 |
|---|---|---|---|
| `config` | 持久化 | 全局配置 | host、current_env、account |
| `cache` | 会话级（结束清空） | 临时变量 | headers、token、接口依赖数据 |
| `schema` | 持久化 | 响应 Schema | 接口首次请求时自动采集 |

### 工作流程

```
启动 → 读取 config.yaml → 写入 config 表（host/env/account）
     → 执行登录 → 写入 cache 表（headers/token）
     → 用例执行 → 接口自动从 config/cache 读取 host/headers
     → 首次请求 → 自动采集 Schema 写入 schema 表
     → 结束 → 清空 cache 表
```

### 代码中使用

```python
from core.storage import config, cache, schema

# config 表 — 读写全局配置
config.set("host", "https://httpbin.org")
config.get("host")                    # "https://httpbin.org"
config.get_all()                      # {"host": "...", "current_env": "test", ...}

# cache 表 — 读写临时变量
cache.set("headers", {"token": "xxx"})
cache.get("headers")                  # {"token": "xxx"}
cache.get_by_jsonpath("cluster_list", "$..cluster_id")  # JSONPath 提取

# schema 表 — 自动采集，通常不需要手动操作
schema.get("SaveMemberTagAPI")        # 返回 JSON Schema dict
```

### 接口调用自动读取

接口对象调用 `send()` 时，内部自动从 SQLite 读取配置：

```python
# 你只需要写这些
res = SaveMemberTagAPI(request_body=body).send()

# 框架内部自动完成：
# 1. config.get("host") → "https://httpbin.org"
# 2. cache.get("headers") → {"token": "xxx"}
# 3. 拼接 URL + 注入 headers → 发送请求
# 4. 首次请求自动采集 Schema → schema.set(...)
```

这意味着切换环境后，所有接口自动使用新的 host 和 headers，零改动。

---

## 模块级登录设计

不同业务模块可能使用不同的账号体系（管理后台 vs 用户端 vs 开放平台）。RunBot 支持两层登录：

### 全局登录

`login.py`（项目根目录）用于 `rbot run` 启动时的默认登录，登录结果写入 SQLite cache 表：

```python
# login.py
from core.fixture import BaseLogin

class Login(BaseLogin):
    def login(self) -> dict:
        # 调用登录接口
        return {}

    def make_headers(self, resp_login: dict) -> dict:
        # 从响应中提取 token，构造 headers
        return {"token": "your_token_here"}
```

### 模块级登录

每个模块在 `testcases/<module>/login.py` 中实现自己的登录类：

```python
# testcases/member/login.py
from testcases.base_login import ModuleLogin

class MemberLogin(ModuleLogin):
    """管理后台登录"""
    def login(self) -> dict:
        url = f"{self.host}/api/admin/login"
        payload = {"user": self.account["user"], "pwd": self.account["pwd"]}
        # self.host 和 self.account 自动从 config.yaml 当前环境读取
        return self._request_token(url, payload)

    def make_headers(self, resp_login: dict) -> dict:
        return self._build_bearer_headers(resp_login)

class MemberVipLogin(ModuleLogin):
    """VIP 用户登录（同模块不同角色）"""
    def login(self) -> dict:
        return {"url": "/api/user/login", "user": "vip_user"}

    def make_headers(self, resp_login: dict) -> dict:
        return {"Authorization": f"Bearer {resp_login['token']}", "X-Role": "vip"}
```

注意：`ModuleLogin` 继承自 `BaseLogin`，自动从 `config.yaml` 当前环境读取 `host` 和 `account`，切换环境后登录地址和账号自动变化。

### 在 conftest 中注入

```python
# testcases/member/conftest.py
import pytest
from testcases.member.login import MemberLogin

@pytest.fixture(scope="module")
def member_session():
    return MemberLogin()
```

### 用例中使用

```python
class TestMemberTag(BaseTestcase):
    def test_save_tag(self, member_session):
        # member_session 已经带了管理后台的登录态
        res = SaveMemberTagAPI(request_body=body).send()
        ...
```

### 登录与 SQLite 的关系

```
config.yaml (test 环境)
  ├── host → config 表 → BaseLogin.host → 登录 URL
  ├── account → config 表 → BaseLogin.account → 登录凭证
  └── 登录成功 → headers → cache 表 → 所有接口自动携带
```

切换到 staging 环境后，host/account 自动变化，登录逻辑不需要改任何代码。

---

## 测试用例编写

### 模块目录结构

```
testcases/<module>/
├── login.py              # 模块登录实现
├── conftest.py           # 模块级 fixture
├── cases/                # 测试用例
│   └── test_<name>.py
├── factory/              # 数据工厂
│   └── <name>_factory.py
└── data/                 # 静态数据文件（JSON/YAML）
    └── <name>_cases.json
```

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
        self.assert_schema("SaveMemberTagAPI", res.body)  # JSON Schema 自动校验
```

`assert_schema` 从 SQLite schema 表中取出首次请求时自动采集的 JSON Schema 进行校验，无需手动维护 Schema 文件。

---

## 装饰器体系

### @dependence — 前置依赖

在目标接口调用前，先调用依赖接口，结果自动存入 cache。若 cache 中已存在则跳过。

```python
from core.decorators import dependence

@dependence(get_cluster_list, "cluster_id", cluster_type="hpc")
def create_instance(self, test_data):
    cluster_id = cache.get_by_jsonpath("cluster_id", "$..cluster_id")
    ...
```

### @update — 后置刷新

目标接口调用后，自动重新调用依赖接口刷新 cache 中的值：

```python
from core.decorators import update

@update("cluster_nodes")
def add_cluster_nodes(self, test_data):
    ...
```

### @async_api — 异步轮询

接口调用后，从响应中提取任务 ID，传给轮询函数等待完成：

```python
from core.decorators import async_api

@async_api(wait_job, "$.job_id")
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

自定义中间件：

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
# 1. HTTP 请求级 — 类属性控制
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

## 代码生成

从 OpenAPI/Swagger 文档自动生成接口模型代码：

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

生成结果：

```
apis/member/
├── __init__.py
├── apis.py      # BaseAPIObject 子类 + @router 装饰器
└── models.py    # attrs 请求/响应模型（含 metadata）
```

---

## AI 生成用例

根据接口定义自动生成测试用例和数据工厂，支持三种方式：

### 方式一：Kiro Steering（推荐，零成本）

在 Kiro 聊天中使用 `#gen-testcase` 上下文，直接对话生成：

```
#gen-testcase 帮我给 member 模块生成用例
```

### 方式二：rbot ai 命令

```bash
export OPENAI_API_KEY=sk-xxx
rbot ai --api apis/member/apis.py --output testcases/member/

# 本地模型
export AI_BASE_URL=http://localhost:11434/v1
export AI_MODEL=qwen2.5-coder
rbot ai --api apis/member/apis.py --output testcases/member/

# 只看 prompt 不调用 LLM
rbot ai --api apis/member/apis.py --output testcases/member/ --dry-run
```

### 提升生成质量

接口模型的 `metadata` 越完整，AI 生成质量越高：

```python
name: str = field(metadata={
    "description": "标签名称",
    "example": "VIP001",
    "constraints": "长度 1-50，不能为空",
    "business_rules": "同一商户下名称不能重复"
})
```

---

## 测试执行

### 三种模式

| 模式 | 命令 | 适用场景 |
|---|---|---|
| 单进程 | `rbot run -m member` | 日常开发调试 |
| 多线程 | `rbot run --mt` | IO 密集型接口测试 |
| 多进程 | `rbot run --mp` | 大规模回归测试 |

### Session 生命周期

```
登录 → 配置写入 config 表 → headers 写入 cache 表 → 执行 pre-hooks
    → pytest.main() 执行用例
    → 执行 post-hooks → 生成报告 → 清空 cache 表
```

### PyCharm 调试

1. Settings → Tools → Python Integrated Tools → Default test runner 选 `pytest`
2. Settings → Project → Python Interpreter 选 `.venv` 里的 Python
3. 打开测试文件，方法名左侧点绿色三角 ▶ 选 Debug，可打断点查看变量

> 每个模块的 `conftest.py` 会自动初始化环境，直接点绿色三角就能跑，不需要先启动 `rbot run`。

---

## HTML 报告

测试执行后自动生成 `reports/runbot.html`，自包含单文件，直接浏览器打开。

功能：
- 概述面板：时间、时长、通过/失败/错误/跳过统计
- 进度条可视化
- 按状态筛选用例
- 点击「查看详情」弹窗显示日志和错误堆栈

同时保留 allure 报告支持（需安装 `brew install allure`），数据输出到 `reports/json/`。
![alt text](image.png)

---

## CLI 命令参考

```bash
# 版本
rbot --version

# 运行测试
rbot run                           # 全部用例
rbot run -m member                 # 按 mark
rbot run -m member -m live         # 多个 mark
rbot run -e staging                # 切换环境
rbot run --mt                      # 多线程
rbot run --mp                      # 多进程
rbot run -l debug                  # 日志级别
rbot run --no-allure               # 不生成 allure

# 代码生成
rbot gen -s <spec> -o <output>
rbot gen -s <spec> -o <output> --tag member
rbot gen -s <spec> -o <output> --path /api/live

# AI 生成用例
rbot ai --api <file> --output <dir>
rbot ai --api <file> --output <dir> --dry-run
```
