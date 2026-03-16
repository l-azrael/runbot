#!/usr/bin/env python
# --coding:utf-8--
"""
RunBot AI 用例生成脚本

用法：
    rbot ai --api apis/member/apis.py --output testcases/member/
    rbot ai --api apis/member/apis.py --output testcases/member/ --type data

环境变量：
    OPENAI_API_KEY   使用 OpenAI（默认）
    ANTHROPIC_API_KEY 使用 Claude
    AI_BASE_URL      自定义 API 地址（兼容 OpenAI 协议的本地模型）
    AI_MODEL         指定模型名称，默认 gpt-4o
"""
import os
import ast
from pathlib import Path

import click

_PROMPT_DIR = Path(__file__).parent / "prompts"


# ------------------------------------------------------------------ LLM 调用
def _call_llm(prompt: str) -> str:
    api_key = os.environ.get("OPENAI_API_KEY") or os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise RuntimeError(
            "未找到 LLM API Key，请设置环境变量 OPENAI_API_KEY 或 ANTHROPIC_API_KEY"
        )

    base_url = os.environ.get("AI_BASE_URL", "https://api.openai.com/v1")
    model = os.environ.get("AI_MODEL", "gpt-4o")

    try:
        from openai import OpenAI
    except ImportError:
        raise RuntimeError("请先安装 openai 包：pip install openai")

    client = OpenAI(api_key=api_key, base_url=base_url)
    resp = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
    )
    return resp.choices[0].message.content.strip()


# ------------------------------------------------------------------ 接口定义提取
def _extract_api_definition(api_file: str) -> str:
    """读取 apis.py + 同目录 models.py，拼成 AI 可理解的接口定义文本"""
    api_path = Path(api_file)
    models_path = api_path.parent / "models.py"

    parts = []
    if models_path.exists():
        parts.append(f"# models.py\n{models_path.read_text(encoding='utf-8')}")
    parts.append(f"# apis.py\n{api_path.read_text(encoding='utf-8')}")
    return "\n\n".join(parts)


def _infer_module_name(api_file: str) -> str:
    """apis/member/apis.py -> member"""
    p = Path(api_file)
    # 取 apis 目录下的模块名（倒数第二段）
    parts = list(p.parts)
    if len(parts) >= 2:
        return parts[-2]
    return parts[0]


def _infer_module_path(api_file: str) -> str:
    """apis/member/apis.py -> apis.member"""
    p = Path(api_file)
    parts = list(p.parts[:-1])
    return ".".join(parts)


# ------------------------------------------------------------------ 代码清洗
def _clean_code(raw: str) -> str:
    """去掉 LLM 返回的 markdown 代码块标记"""
    lines = raw.splitlines()
    cleaned = []
    in_block = False
    for line in lines:
        if line.strip().startswith("```"):
            in_block = not in_block
            continue
        cleaned.append(line)
    return "\n".join(cleaned).strip()


def _validate_syntax(code: str, label: str):
    try:
        ast.parse(code)
    except SyntaxError as e:
        click.echo(f"[警告] {label} 语法错误：{e}，请人工检查后再使用", err=True)


# ------------------------------------------------------------------ 写文件
def _write_output(output_dir: str, filename: str, code: str):
    os.makedirs(output_dir, exist_ok=True)
    # 确保 __init__.py 存在
    init_path = os.path.join(output_dir, "__init__.py")
    if not os.path.exists(init_path):
        with open(init_path, "w", encoding="utf-8") as f:
            f.write("")
    out_path = os.path.join(output_dir, filename)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(code)
    click.echo(f"  写入：{out_path}")


# ------------------------------------------------------------------ CLI
@click.command()
@click.option("--api", required=True, help="接口定义文件路径，如 apis/member/apis.py")
@click.option("--output", required=True, help="输出模块目录，如 testcases/member/")
@click.option(
    "--type", "gen_type",
    default="both",
    type=click.Choice(["testcase", "data", "both"]),
    show_default=True,
    help="生成类型：testcase=用例文件，data=数据工厂，both=两者都生成",
)
@click.option("--dry-run", is_flag=True, default=False, help="只打印 prompt，不调用 LLM")
def main(api, output, gen_type, dry_run):
    """RunBot AI — 根据接口定义自动生成测试用例

    生成结果按新目录结构输出：
      testcases/<module>/cases/    — 测试用例
      testcases/<module>/factory/  — 数据工厂
    """
    if not os.path.exists(api):
        raise click.BadParameter(f"文件不存在：{api}", param_hint="--api")

    api_def = _extract_api_definition(api)
    module_name = _infer_module_name(api)
    module_path = _infer_module_path(api)

    # 规范化输出目录（确保是 testcases/<module>/ 格式）
    output = output.rstrip("/")

    click.echo(f"[RunBot AI] 接口文件：{api}")
    click.echo(f"[RunBot AI] 输出目录：{output}")
    click.echo(f"[RunBot AI] 生成类型：{gen_type}")

    if gen_type in ("testcase", "both"):
        _gen_testcase(api_def, module_name, module_path, output, dry_run)

    if gen_type in ("data", "both"):
        _gen_data(api_def, module_name, output, dry_run)


def _gen_testcase(api_def: str, module_name: str, module_path: str,
                  output: str, dry_run: bool):
    tpl = (_PROMPT_DIR / "gen_testcase.md").read_text(encoding="utf-8")
    prompt = tpl.replace("{api_definition}", api_def).replace("{module}", module_path)

    if dry_run:
        click.echo("\n--- [dry-run] testcase prompt ---")
        click.echo(prompt[:800] + "...\n")
        return

    click.echo("[RunBot AI] 正在生成测试用例...")
    raw = _call_llm(prompt)
    code = _clean_code(raw)
    _validate_syntax(code, "testcase")

    # 输出到 <output>/cases/ 目录
    cases_dir = os.path.join(output, "cases")
    _write_output(cases_dir, f"test_{module_name}_ai.py", code)


def _gen_data(api_def: str, module_name: str, output: str, dry_run: bool):
    tpl = (_PROMPT_DIR / "gen_data.md").read_text(encoding="utf-8")
    prompt = tpl.replace("{api_definition}", api_def)

    if dry_run:
        click.echo("\n--- [dry-run] data prompt ---")
        click.echo(prompt[:800] + "...\n")
        return

    click.echo("[RunBot AI] 正在生成数据工厂...")
    raw = _call_llm(prompt)
    code = _clean_code(raw)
    _validate_syntax(code, "data_factory")

    # 输出到 <output>/factory/ 目录
    factory_dir = os.path.join(output, "factory")
    _write_output(factory_dir, f"{module_name}_factory_ai.py", code)


if __name__ == "__main__":
    main()
