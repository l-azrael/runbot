# RunBot 框架设计文档

> 版本：2.0  
> 状态：设计阶段  
> 目标：基于 pytest 的企业级接口自动化测试框架，支持声明式接口建模、OpenAPI 按需生成、AI 辅助生成用例、多环境管理

---

## 一、设计目标

| 目标 
| 说明 |
|---|---|
| 自研框架核心 | 所有能力自研，不依赖外部测试框架包 |
| 声明式接口建模 | 用 attrs 定义接口，代码即文档，IDE 全程提示 |
| OpenAPI 按需生成 | 按 tag/路径前缀过滤，简单命令生成接口模型代码 |
| AI 生成用例 | 接口模型结构化后，AI 可直接读取并生成测试用例 |
| 保留 V2 核心能力 | 存储管理、依赖装饰器、重试、日志、多任务执行全部保留 |
| 可插拔中间件 | 日志、重试、Mock、性能统计按需插拔 |
| 多环境管理 | 一键切换 test/staging/release，支持环境变量覆盖 |
| 参数驱动统一 | 文件驱动、类驱动、内联驱动统一入口 |

---

## 二、整体目录结构

```
project-root/
├── apis/                        # 接口定义层（按业务模块划分）
│   ├── member/
│   │   ├── apis.py              # 接口对象定义
│   │   └── models.py            # 请求/响应模型定义
│   ├── live/
│   │   ├── apis.py
│   │   └── models.py
│   └── eshop/
│       ├── apis.py
│       └── models.py
│
├── testcases/                   # 测试用例层
│   ├── member/
│   │   ├── test_member_tag.py
│   │   └── data/                # 静态测试数据文件（JSON/YAML）
│   ├── live/
│   │   └── test_live_list.py
│   └── data_factory/            # 测试数据工厂（动态构造/AI生成数据）
│       ├── base_factory.py      # 工厂基类
│       ├── member/
│       │   └── member_tag_factory.py
│       └── live/
│           └── live_factory.py
│
├── core/                        # 框架核心（不含业务逻辑）
│   ├── api_object.py            # BaseAPIObject 基类
│   ├── router.py                # 路由装饰器（@router.get/post/...）
│   ├── middlewares/             # 中间件系统
│   │   ├── base.py
│   │   ├── logging_mw.py
│   │   └── retry_mw.py
│   ├── storage/                 # 存储管理（SQLite）
│   │   ├── db.py
│   │   ├── config.py
│   │   ├── cache.py
│   │   ├── schema.py
│   │   └── statistics.py
│   ├── decorators/              # 装饰器
│   │   ├── dependence.py
│   │   ├── async_api.py
│   │   └── update.py
│   ├── parametrize/             # 统一参数化
│   │   ├── parametrize.py       # @parametrize 统一入口
│   │   └── loaders.py           # 文件/类/内联加载器
│   ├── base_testcase.py
│   ├── fixture.py
│   ├── runner.py
│   ├── log.py
│   ├── retry.py
│   ├── exceptions.py
│   └── path.py
│
├── maker/                       # 代码生成工具
│   ├── openapi_parser.py        # 解析 OpenAPI/Swagger 文档
│   ├── code_generator.py        # 生成 apis.py + models.py
│   ├── naming.py                # 命名策略
│   └── templates/
│       ├── apis_template.j2
│       └── models_template.j2
│
├── ai/                          # AI 辅助生成用例
│   ├── prompts/                 # prompt 模板
│   │   ├── gen_testcase.md      # 生成用例的 prompt 模板
│   │   └── gen_data.md          # 生成测试数据的 prompt 模板
│   └── gen_cases.py             # AI 生成用例脚本入口
│
├── tools/                       # 数据工具（预留）
│   ├── data_builder/            # 根据接口定义构建测试数据
│   └── data_validator/          # 数据校验工具
│
├── cli/                         # CLI 工具
│   ├── main.py
│   ├── run.py
│   └── gen.py
│
├── database/
│   └── runbot.db
│
├── conf/
│   ├── config.yaml              # 多环境配置
│   └── dist_strategy.yaml       # 多任务分配策略
│
├── logs/
├── reports/
├── login.py
├── hooks.py
├── conftest.py
├── pytest.ini
└── requirements.txt
```

---

## 三、核心模块设计

### 3.1 接口建模（`core/api_object.py` + `core/router.py`）

用 `attrs` + `@router` 装饰器声明接口，每个接口是一个 Python 类。

```python
# apis/member/models.py
from attrs import define, field
from typing import Optional

@define
class SaveMemberTagRequest:
    name: str = field(metadata={"description": "标签名称", "example": "VIP001"})
    type: int = field(metadata={
        "description": "标签类型",
        "enum": [0, 1],
        "enum_desc": {"0": "创建失败", "1": "正常创建"},
        "business_rules": "type=1 为正常标签，type=0 为失败标签"
    })

@define
class MemberTagResponse:
    code: int = field(default=0)
    message: str = field(default="success")
    data: Optional[dict] = field(default=None)
```

```python
# apis/member/apis.py
from attrs import define, field
from typing import Optional
from core.api_object import BaseAPIObject
from core.router import router
from apis.member.models import SaveMemberTagRequest, MemberTagResponse

@define(kw_only=True)
@router.post("/api/member/tag/save")
class SaveMemberTagAPI(BaseAPIObject[MemberTagResponse]):
    """保存成员标签"""
    request_body: SaveMemberTagRequest
    response: Optional[MemberTagResponse] = field(default=MemberTagResponse)
```

```python
# 用例层调用
def test_save_member_tag():
    body = SaveMemberTagRequest(name="VIP001", type=1)
    res = SaveMemberTagAPI(request_body=body).send()
    assert res.response_model.code == 0
```

---

### 3.2 存储管理（`core/storage/`）

基于 SQLite，四张表，线程安全，全局单例。

| 表名 | 生命周期 | 存储内容 |
|---|---|---|
| `config` | 持久化 | 全局配置（host、账号等） |
| `cache` | 会话级 | 临时变量、接口依赖数据、headers |
| `schema` | 持久化 | 接口响应 JSON Schema |
| `statistics` | 持久化 | 接口调用元数据统计 |

```python
from core.storage import config, cache, schema

host = config.get("host")
cache.set("auth_token", "Bearer xxx")
token = cache.get("auth_token")
cluster_id = cache.get_by_jsonpath("cluster_list", "$..cluster_id")
```

---

### 3.3 中间件系统（`core/middlewares/`）

请求/响应链路可插拔，通过 YAML 配置启停和优先级。

```
请求 → [logging_mw] → [retry_mw] → [custom_mw] → HTTP 发送 → 响应
```

```python
# 自定义中间件示例
@middleware(name="perf", priority=700, enabled=True)
def perf_mw(request, call_next):
    start = time.time()
    response = call_next(request)
    elapsed = time.time() - start
    if elapsed > 2.0:
        logger.warning(f"慢接口告警: {request.url} 耗时 {elapsed:.2f}s")
    return response
```

```yaml
# conf/middleware.yaml
logging_middleware:
  enabled: true
  priority: 900
retry_middleware:
  enabled: true
  priority: 800
  options:
    max_retries: 3
    retry_on_codes: [500, 502, 503]
```

---

### 3.4 依赖装饰器（`core/decorators/`）

保留 V2 全部能力，接口不变，内部适配新的存储层。

```python
# @dependence：前置依赖
@dependence(cluster.get_cluster_list, "cluster_id", cluster_type="hpc")
def create_instance(self, test_data):
    cluster_id = self.cache.get_by_jsonpath("cluster_id", "$..cluster_id")

# @update：后置刷新 cache
@update("cluster_nodes")
def add_cluster_nodes(self, test_data):
    ...

# @async_api：异步轮询
@async_api(wait_job, "job_id")
def submit_job(self, test_data):
    ...
```

---

### 3.5 重试机制（`core/retry.py`）

三个层次，基于 tenacity。

```python
# 1. HTTP 请求级（类属性控制）
class MyAPI(BaseAPIObject):
    IS_HTTP_RETRY = True
    HTTP_RETRY_COUNTS = 3

# 2. 业务级（装饰器）
@retry(counts=3, interval=2, retry_condition=lambda r: r.get("code") != 0)
def my_api_method(self): ...

# 3. 代码片段级
for attempt in Retry(counts=3, interval=2, exception_type=TimeoutError):
    with attempt:
        result = some_operation()
```

---

### 3.6 日志系统（`core/log.py`）

基于 loguru，三路输出（控制台/文件/allure），多进程/线程 worker 标识。

```
2026-03-15 10:00:00 [MainProcess]-[MainThread]-[module.function:line]-[INFO]: 消息
```

---

### 3.7 测试执行器（`core/runner.py`）

三种模式，Session 生命周期管理。

```python
from core.runner import Runner, ThreadsRunner, ProcessesRunner

Runner().run(["-m member"], login=Login())
ThreadsRunner().run(["-m member", "-m live"], login=Login())
ProcessesRunner().run(["-m member", "-m live"], login=Login())
```

Session 生命周期：
```
登录 → 加载配置到 config 表 → 执行 pre-hooks
    → pytest.main() 执行用例
    → 执行 post-hooks → 生成 allure 报告 → 清空 cache 表
```

---

### 3.8 代码生成器（`maker/`）

从 OpenAPI/Swagger 文档按需生成接口模型代码，支持按 tag 或路径前缀过滤，保持命令简单。

#### 生成命令

```bash
# 生成全部接口
rbot gen -s http://yapi.xxx.com/api/openapi.json -o apis/member

# 按 tag 过滤（只生成 member 相关接口）
rbot gen -s docs/api.json -o apis/member --tag member

# 按路径前缀过滤
rbot gen -s docs/api.json -o apis/live --path /api/live

# 从本地文件生成
rbot gen -s docs/member-api.json -o apis/member --tag member

# 读取 conf/runbot.yaml 中的默认配置
rbot gen
```

#### 生成结果

```
apis/member/
├── apis.py      # 接口对象定义（BaseAPIObject 子类）
└── models.py    # 请求/响应模型定义（attrs 类）
```

#### runbot.yaml 持久化配置

```yaml
# conf/runbot.yaml
openapi:
  spec: http://yapi.xxx.com/api/openapi.json
  output: apis/
  # 可选过滤
  tag: member
  path_prefix: /api
```

---

### 3.9 统一参数化（`core/parametrize/`）

统一 `@parametrize` 入口，同时支持三种驱动方式，自动提取 `desc` 作为用例 ID。

```python
from core.parametrize import parametrize

# 1. 类驱动（工厂类生成数据）
@parametrize(MemberTagFactory.data())
def test_save_tag(self, data):
    ...

# 2. 文件驱动（JSON/YAML 文件）
@parametrize("testcases/member/data/member_tag.json")
def test_save_tag(self, data):
    ...

# 3. 内联驱动（直接写数据）
@parametrize([
    {"desc": "正常标签", "name": "VIP", "type": 1},
    {"desc": "失败标签", "name": "BAD", "type": 0},
])
def test_save_tag(self, data):
    ...
```

数据格式规范（统一包含 `desc` 字段作为用例 ID）：

```json
[
  {"desc": "正常创建标签", "name": "VIP001", "type": 1},
  {"desc": "标签名为空", "name": "", "type": 1},
  {"desc": "非法类型", "name": "VIP002", "type": 99}
]
```

工厂类示例：

```python
# testcases/data_factory/member/member_tag_factory.py
from testcases.data_factory.base_factory import BaseFactory

class MemberTagFactory(BaseFactory):
    @classmethod
    def data(cls) -> list:
        return [
            {"desc": "正常创建", "name": cls.fake_name(), "type": 1},
            {"desc": "边界值-名称最长", "name": "x" * 50, "type": 1},
        ]
```

---

### 3.10 环境管理（`conf/config.yaml`）

支持多环境配置，一键切换，支持环境变量覆盖。

#### 配置文件结构

```yaml
# conf/config.yaml
current_env: test          # 当前激活环境，可被 CLI -e 或环境变量覆盖

test:
  host: https://testapi.example.com
  account:
    username: test_user
    password: test_pass
  db:
    host: 127.0.0.1
    port: 5432
    name: test_db

staging:
  host: https://stagingapi.example.com
  account:
    username: staging_user
    password: staging_pass
  db:
    host: staging-db.internal
    port: 5432
    name: staging_db

release:
  host: https://api.example.com
  account:
    username: release_user
    password: release_pass
  db:
    host: prod-db.internal
    port: 5432
    name: prod_db
```

#### 切换方式（三种，优先级从高到低）

```bash
# 1. 环境变量（最高优先级，适合 CI/CD）
RUNBOT_ENV=release pytest -m member

# 2. CLI 参数
rbot -m member -e release

# 3. 修改 config.yaml 中的 current_env（默认）
```

#### 代码中读取

```python
from core.fixture import EnvVars

env = EnvVars()
host = env.current_env_conf.get("host")
db_conf = env.current_env_conf.get("db")
```

---

### 3.11 AI 辅助生成用例（`ai/`）

#### 设计思路

接口模型的 `metadata` 是 AI 理解接口的核心信息源，设计时需要规范化填写。

#### 接口模型 metadata 规范

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
        "business_rules": "type=1 为正常标签，type=0 为失败标签，不允许其他值"
    })
```

#### AI 生成链路

```
1. 读取 apis/xxx/apis.py + models.py（接口结构 + metadata）
2. 读取 ai/prompts/gen_testcase.md（prompt 模板）
3. 调用 LLM API（OpenAI/Claude/本地模型）
4. 生成 testcases/xxx/test_xxx.py + data_factory/xxx/xxx_factory.py
5. 人工 review 后合入
```

#### prompt 模板示例（`ai/prompts/gen_testcase.md`）

```markdown
你是一个接口自动化测试专家。根据以下接口定义，生成完整的测试用例。

## 接口定义
{api_definition}

## 要求
- 覆盖正常流程、边界值、异常参数三类场景
- 每个用例包含 desc 字段说明测试意图
- 使用 @parametrize 数据驱动
- 断言包含 code、message 字段校验
```

#### 目录结构

```
ai/
├── prompts/
│   ├── gen_testcase.md    # 生成用例 prompt
│   └── gen_data.md        # 生成测试数据 prompt
└── gen_cases.py           # 入口脚本
```

```bash
# 使用示例
python ai/gen_cases.py --api apis/member/apis.py --output testcases/member/
```

---

### 3.12 CLI 工具（`cli/`）

```bash
# 运行测试
rbot -m member                          # 按 mark 运行
rbot -m member -e release               # 切换环境
rbot --mt --dist-mark member live       # 多线程
rbot --mp --dist-suite testcases/       # 多进程
rbot -l debug                           # 设置日志级别

# 生成接口模型
rbot gen -s <spec> -o <output>
rbot gen -s <spec> -o <output> --tag member
rbot gen -s <spec> -o <output> --path /api/live

# 脚手架
rbot create <project-name>
```

---

### 3.13 BaseTestcase 断言库（`core/base_testcase.py`）

```python
class BaseTestcase:
    def assert_eq(self, actual, expected, msg=""): ...
    def assert_neq(self, actual, expected, msg=""): ...
    def assert_contains(self, actual, expected, msg=""): ...
    def assert_is_not_none(self, actual): ...
    def assert_http_code_success(self, code): ...
    def assert_schema(self, api_name: str, response: dict): ...  # 从 schema 表校验
```

---

## 四、关键设计决策

### 4.1 为什么用 attrs 而不是 dataclass 或 pydantic

| | dataclass | pydantic | attrs |
|---|---|---|---|
| 样板代码 | 少 | 少 | 最少 |
| 类型校验 | 无 | 强（运行时） | 可选 |
| 性能 | 好 | 一般 | 最好 |
| metadata 支持 | 无 | 有限 | 原生支持 |
| AI 可读性 | 一般 | 好 | 最好（metadata 结构化） |

attrs 的 `metadata` 字段天然适合存储 AI 需要的业务语义信息（description/example/enum/business_rules）。

### 4.2 AI 接入的核心设计原则

- 接口模型是 AI 的"输入规格"，metadata 越完整，生成质量越高
- 生成的用例必须经过人工 review，AI 负责覆盖度，人工负责准确性
- `data_factory/` 和 `testcases/data/` 分离：工厂类负责动态构造，data/ 存静态固定数据
- AI 生成的用例落到 `testcases/`，生成的数据落到 `data_factory/`，两者解耦

### 4.3 环境管理原则

- 所有环境相关配置集中在 `conf/config.yaml`，不散落在代码里
- 环境变量 `RUNBOT_ENV` 优先级最高，方便 CI/CD 注入
- token/host/db 全部按环境隔离，不同环境不共享任何凭证

---

## 五、开发阶段划分

### Phase 1：框架骨架（核心可运行）

- [ ] `core/storage/` — SQLite 四表，线程安全
- [ ] `core/log.py` — 日志系统
- [ ] `core/path.py` — 路径常量
- [ ] `core/router.py` — 路由装饰器
- [ ] `core/api_object.py` — BaseAPIObject 基类
- [ ] `core/middlewares/` — 中间件系统
- [ ] `core/retry.py` — 重试机制
- [ ] `core/decorators/` — @dependence / @update / @async_api
- [ ] `core/parametrize/` — 统一参数化
- [ ] `core/base_testcase.py` — 断言基类
- [ ] `core/fixture.py` — Session 管理（含多环境支持）
- [ ] `core/runner.py` — 测试执行器
- [ ] `login.py` / `conftest.py`

### Phase 2：代码生成 + CLI

- [ ] `maker/openapi_parser.py` — 解析 OpenAPI，支持 tag/path 过滤
- [ ] `maker/code_generator.py` — 生成 apis.py + models.py
- [ ] `maker/templates/` — Jinja2 模板
- [ ] `cli/` — rbot 命令（含 -e 环境切换）

### Phase 3：AI 生成用例

- [ ] 接口模型 metadata 规范完善
- [ ] `ai/prompts/` — prompt 模板
- [ ] `ai/gen_cases.py` — 生成脚本
- [ ] `testcases/data_factory/` — 工厂类体系
- [ ] `tools/` — 数据工具（预留）

---

## 六、依赖清单

```
# 核心依赖
pytest>=7.2.0
attrs>=23.0.0
requests>=2.28.0
pyyaml>=6.0
loguru>=0.6.0
tenacity>=8.0.0
jinja2>=3.1.0
click>=8.1.0
allure-pytest>=2.8.0

# 接口建模
jsonpath>=0.82
jsonschema>=4.17.0
genson>=1.2.0

# 数据库
psycopg2-binary>=2.9.0

# 数据处理
pandas>=2.0.0
openpyxl>=3.1.0

# 参数化
parametrize-from-file>=0.20.0
nestedtext>=3.7
toml>=0.10.0
```

---

## 七、与现有项目的迁移路径

| 现有代码 | 迁移方式 |
|---|---|
| `core/cache/cache.py` | 迁移到 `core/storage/`，接口不变 |
| `core/base/base_api.py` | 重构为 `core/api_object.py`，支持 attrs 模型 |
| `core/retry/retry.py` | 迁移到 `core/retry.py`，修复 旧框架依赖 |
| `core/log/log.py` | 迁移到 `core/log.py`，接口不变 |
| `core/runner.py` | 修复旧框架依赖，替换 gen_reports 和 HandleIni |
| `core/decorators/` | 旧装饰器集合拆分到各文件 |
| `core/parametrize/` | 重构为统一 `@parametrize` 入口 |
| `apis/xxx/xxx_api_path.py` | 逐步迁移为 attrs 声明式定义 |
| `apis/xxx/xxx_api.py` | 逐步迁移为 BaseAPIObject 子类 |
| `app/generateapiscode/` | 重构为 `maker/`，支持 OpenAPI tag/path 过滤 |
| `conf/config.yaml` | 扩展为多环境结构，增加 staging/release 节点 |

旧的 `apis/` 接口定义可以继续工作（BaseApi 兼容层保留），新接口用新方式定义，两种方式可以共存。
