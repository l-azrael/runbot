# --coding:utf-8--
import click
from core.cli.run import run_cmd
from core.cli.gen import gen_cmd
from core.cli.ai_cmd import ai_cmd


@click.group()
@click.version_option("1.0.0", prog_name="rbot")
def cli():
    """RunBot — API 自动化测试框架"""
    pass


cli.add_command(run_cmd, name="run")
cli.add_command(gen_cmd, name="gen")
cli.add_command(ai_cmd, name="ai")


def main():
    cli()


if __name__ == "__main__":
    main()
