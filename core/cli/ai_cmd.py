# --coding:utf-8--
import click


@click.command()
@click.option("--api", required=True, help="接口定义文件路径，如 apis/member/apis.py")
@click.option("--output", required=True, help="输出目录，如 testcases/member/")
@click.option(
    "--type", "gen_type",
    default="both",
    type=click.Choice(["testcase", "data", "both"]),
    show_default=True,
    help="生成类型",
)
@click.option("--dry-run", is_flag=True, default=False, help="只打印 prompt，不调用 LLM")
def ai_cmd(api, output, gen_type, dry_run):
    """使用 AI 根据接口定义生成测试用例"""
    from core.ai.gen_cases import _extract_api_definition, _infer_module_path, _gen_testcase, _gen_data
    import os

    if not os.path.exists(api):
        raise click.BadParameter(f"文件不存在：{api}", param_hint="--api")

    api_def = _extract_api_definition(api)
    module_path = _infer_module_path(api)

    click.echo(f"[RunBot AI] 接口文件：{api}")
    click.echo(f"[RunBot AI] 输出目录：{output}")

    if gen_type in ("testcase", "both"):
        _gen_testcase(api_def, module_path, output, dry_run)
    if gen_type in ("data", "both"):
        _gen_data(api_def, output, dry_run)
