# --coding:utf-8--
import os
import click


@click.command()
@click.option("-m", "--mark", multiple=True, help="pytest mark，可多次指定")
@click.option("-e", "--env", default=None, help="运行环境（覆盖 config.yaml 中的 current_env）")
@click.option("--mt", is_flag=True, default=False, help="多线程模式")
@click.option("--mp", is_flag=True, default=False, help="多进程模式")
@click.option("-l", "--log-level", default="info", show_default=True,
              type=click.Choice(["debug", "info", "warning", "error"], case_sensitive=False),
              help="日志级别")
@click.option("--no-allure", is_flag=True, default=False, help="不生成 allure 报告")
def run_cmd(mark, env, mt, mp, log_level, no_allure):
    """运行测试用例"""
    # 环境变量注入（最高优先级）
    if env:
        os.environ["RUNBOT_ENV"] = env

    # 构建 pytest args
    args = []
    for m in mark:
        args.extend(["-m", m])
    if not args:
        args = ["."]  # 默认跑全部

    _run(args, mt=mt, mp=mp, gen_allure=not no_allure)


def _run(args: list, mt: bool, mp: bool, gen_allure: bool):
    # 延迟导入，避免循环依赖
    from core.runner import Runner, ThreadsRunner, ProcessesRunner

    try:
        login = _load_login()
    except Exception:
        login = None

    if mt:
        ThreadsRunner().run(args, login=login, gen_allure=gen_allure)
    elif mp:
        ProcessesRunner().run(args, login=login, gen_allure=gen_allure)
    else:
        Runner().run(args, login=login, gen_allure=gen_allure)


def _load_login():
    """尝试从项目根目录加载 login.py 中的 Login 类"""
    import importlib
    module = importlib.import_module("login")
    login_cls = getattr(module, "Login", None)
    if login_cls:
        return login_cls()
    return None
