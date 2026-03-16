# 项目规范

## 项目名称
**RunBot** — 基于 pytest 的企业级接口自动化测试框架

## 关键字规范

| 禁止使用 | 替换为 |
|---|---|
| aomaker | RunBot / runbot |
| arun | rbot |
| FlowTest / flowtest | RunBot / runbot |
| AUTOATE_ENV | RUNBOT_ENV |
| autoate.db | runbot.db |
| aomaker.yaml | runbot.yaml |
| QG / qg | 不使用，示例路径用 /api/ 替代 |
| qianguolive.cn | example.com |

## CLI 命令
- 主命令：`rbot`
- 运行测试：`rbot -m <mark>`
- 切换环境：`rbot -m <mark> -e <env>`
- 生成代码：`rbot gen -s <spec> -o <output>`

## 数据库文件
- `database/runbot.db`

## 配置文件
- `conf/runbot.yaml`（代码生成持久化配置）
- `conf/config.yaml`（多环境配置）

---

## 开发进度

### Phase 1：框架骨架 ✅ 已完成

已完成文件：
- `core/_constants.py` — 常量（DB名改为 runbot.db）
- `core/exceptions.py` — 自定义异常（RunBotException）
- `core/path.py` — 路径常量（动态 BASEDIR）
- `core/storage/db.py` — SQLite 基类（自动建表）
- `core/storage/config.py` + `cache.py` + `schema.py` — 三张表
- `core/storage/__init__.py` — 统一导出
- `core/log/log.py` — 日志系统（RunBotLogger）
- `core/log/__init__.py`
- `core/retry/__init__.py` — 重试（make_retry / Retry）
- `core/router.py` — 路由装饰器（@router.get/post/...）
- `core/middlewares/base.py` — 中间件注册与链式执行
- `core/middlewares/logging_mw.py` — 日志中间件
- `core/middlewares/retry_mw.py` — 重试中间件
- `core/middlewares/__init__.py`
- `core/api_object.py` — BaseAPIObject + Response
- `core/decorators/dependence.py` — @dependence
- `core/decorators/update.py` — @update
- `core/decorators/async_api.py` — @async_api
- `core/decorators/__init__.py`
- `core/parametrize/parametrize.py` — 统一 @parametrize（文件/类/内联）
- `core/parametrize/__init__.py`
- `core/base_testcase.py` — 断言基类（含 assert_schema）
- `core/fixture.py` — 多环境配置读取 + Session 管理（支持 RUNBOT_ENV）
- `core/hook_manager.py` — SessionHook + @hook 装饰器
- `core/runner.py` — Runner / ThreadsRunner / ProcessesRunner
- `conftest.py` — pytest fixture（db 按需）

整体冒烟测试通过 ✅

### Phase 2：代码生成 + CLI ✅ 已完成

- `maker/openapi_parser.py` — 解析 OpenAPI，支持 --tag / --path 过滤
- `maker/code_generator.py` — 生成 apis.py + models.py
- `maker/templates/` — Jinja2 模板
- `cli/main.py` + `cli/run.py` + `cli/gen.py` — rbot 命令
- `setup.py` — rbot 入口点注册

`rbot gen / rbot run` 验证通过 ✅

### Phase 3：AI 生成用例 ✅ 已完成

- `runbot_ai/gen_cases.py` — AI 生成脚本（支持 OpenAI/Claude/本地模型）
- `runbot_ai/prompts/gen_testcase.md` — 用例生成 prompt 模板
- `runbot_ai/prompts/gen_data.md` — 数据工厂生成 prompt 模板
- `testcases/data_factory/base_factory.py` — 工厂基类
- `cli/ai_cmd.py` — `rbot ai` 命令
- `pyproject.toml` — 替换 setup.py，修复包发现问题

`rbot ai --dry-run` 验证通过 ✅

使用方式：
```bash
# 需要设置 LLM API Key
export OPENAI_API_KEY=sk-xxx
rbot ai --api apis/member/apis.py --output testcases/member/

# 本地模型（兼容 OpenAI 协议）
export AI_BASE_URL=http://localhost:11434/v1
export AI_MODEL=qwen2.5-coder
rbot ai --api apis/member/apis.py --output testcases/member/

# 只看 prompt 不调用 LLM
rbot ai --api apis/member/apis.py --output testcases/member/ --dry-run
```
