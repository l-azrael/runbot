# --coding:utf-8--
import os
import click
import yaml

from core.path import RUNBOT_YAML_PATH


@click.command()
@click.option("-s", "--spec", default=None, help="OpenAPI 文档路径或 URL")
@click.option("-o", "--output", default=None, help="输出目录，如 apis/member")
@click.option("--tag", default=None, help="只生成指定 tag 的接口")
@click.option("--path", "path_prefix", default=None, help="只生成路径以此前缀开头的接口")
def gen_cmd(spec, output, tag, path_prefix):
    """从 OpenAPI/Swagger 文档生成接口模型代码"""
    # 未传参数时读取 conf/runbot.yaml
    if not spec or not output:
        cfg = _load_runbot_yaml()
        spec = spec or cfg.get("spec")
        output = output or cfg.get("output")
        tag = tag or cfg.get("tag")
        path_prefix = path_prefix or cfg.get("path_prefix")

    if not spec:
        raise click.UsageError("请通过 -s 指定 OpenAPI 文档路径/URL，或在 conf/runbot.yaml 中配置 spec")
    if not output:
        raise click.UsageError("请通过 -o 指定输出目录，或在 conf/runbot.yaml 中配置 output")

    click.echo(f"[RunBot] 开始生成代码")
    click.echo(f"  spec   : {spec}")
    click.echo(f"  output : {output}")
    if tag:
        click.echo(f"  tag    : {tag}")
    if path_prefix:
        click.echo(f"  path   : {path_prefix}")

    from core.maker.code_generator import generate
    generate(spec_source=spec, output_dir=output, tag_filter=tag, path_filter=path_prefix)


def _load_runbot_yaml() -> dict:
    if not os.path.exists(RUNBOT_YAML_PATH):
        return {}
    with open(RUNBOT_YAML_PATH, encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    return data.get("openapi", {})
