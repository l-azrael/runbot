# --coding:utf-8--
"""
RunBot HTML 报告生成器
参照旧版 HTML 报告风格，生成自包含的单文件 HTML 测试报告。
支持：概述统计、通过/失败/错误/跳过筛选、用例详情弹窗。
"""
import os
import json
import datetime
from typing import List, Dict, Optional
from pathlib import Path

from core.path import REPORT_DIR
from core.log.log import logger
from core.report._template import HTML_TEMPLATE as _HTML_TEMPLATE

_REPORT_PATH = os.path.join(REPORT_DIR, "runbot.html")


class TestResult:
    """单条用例结果"""
    __slots__ = ("class_name", "case_name", "description", "duration",
                 "start_time", "status", "log")

    def __init__(self, class_name: str, case_name: str, description: str,
                 duration: float, start_time: str, status: str, log: str = ""):
        self.class_name = class_name
        self.case_name = case_name
        self.description = description
        self.duration = duration
        self.start_time = start_time
        self.status = status  # passed / failed / error / skipped
        self.log = log


class ReportCollector:
    """pytest 插件：收集用例结果"""

    def __init__(self):
        self.results: List[TestResult] = []
        self._start_time: Optional[datetime.datetime] = None
        self._end_time: Optional[datetime.datetime] = None

    def pytest_sessionstart(self, session):
        self._start_time = datetime.datetime.now()

    def pytest_runtest_logreport(self, report):
        if report.when != "call" and not (report.when == "setup" and report.skipped):
            return

        status_map = {True: "passed", False: "failed"}
        if report.skipped:
            status = "skipped"
        elif report.passed:
            status = "passed"
        elif report.failed:
            status = "error" if report.when == "setup" else "failed"
        else:
            status = "error"

        # 提取类名和方法名
        node_parts = report.nodeid.split("::")
        class_name = ".".join(node_parts[:-1]) if len(node_parts) > 1 else node_parts[0]
        case_name = node_parts[-1] if len(node_parts) > 1 else report.nodeid

        # 提取 docstring 作为描述
        description = ""
        if hasattr(report, "head_line"):
            description = report.head_line or ""

        log_text = ""
        if report.longreprtext:
            log_text = report.longreprtext
        elif hasattr(report, "caplog") and report.caplog:
            log_text = report.caplog

        self.results.append(TestResult(
            class_name=class_name,
            case_name=case_name,
            description=description,
            duration=round(report.duration, 2),
            start_time=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            status=status,
            log=log_text,
        ))

    def pytest_sessionfinish(self, session, exitstatus):
        self._end_time = datetime.datetime.now()
        try:
            generate_html_report(self.results, self._start_time, self._end_time)
        except Exception as e:
            logger.error(f"[RunBot] 生成 HTML 报告失败：{e}")


def _escape_html(text: str) -> str:
    return (text.replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


def _stats(results: List[TestResult]) -> Dict:
    total = len(results)
    passed = sum(1 for r in results if r.status == "passed")
    failed = sum(1 for r in results if r.status == "failed")
    error = sum(1 for r in results if r.status == "error")
    skipped = sum(1 for r in results if r.status == "skipped")
    pass_rate = f"{passed / total * 100:.2f}" if total else "0.00"
    fail_rate = f"{failed / total * 100:.2f}" if total else "0.00"
    error_rate = f"{error / total * 100:.2f}" if total else "0.00"
    return {
        "total": total, "passed": passed, "failed": failed,
        "error": error, "skipped": skipped,
        "pass_rate": pass_rate, "fail_rate": fail_rate, "error_rate": error_rate,
    }


def generate_html_report(results: List[TestResult],
                         start_time: datetime.datetime,
                         end_time: datetime.datetime,
                         output_path: str = _REPORT_PATH):
    """生成自包含 HTML 报告"""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    s = _stats(results)
    elapsed = end_time - start_time
    hours, remainder = divmod(int(elapsed.total_seconds()), 3600)
    minutes, seconds = divmod(remainder, 60)
    duration_str = f"{hours:02d}h:{minutes:02d}m:{seconds:02d}s"

    rows_html = _build_rows(results)

    html = _HTML_TEMPLATE.format(
        start_time=start_time.strftime("%Y-%m-%d %H:%M:%S"),
        end_time=end_time.strftime("%Y-%m-%d %H:%M:%S"),
        duration=duration_str,
        total=s["total"],
        passed=s["passed"],
        failed=s["failed"],
        error=s["error"],
        skipped=s["skipped"],
        pass_rate=s["pass_rate"],
        fail_rate=s["fail_rate"],
        error_rate=s["error_rate"],
        rows=rows_html,
    )

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)
    logger.info(f"[RunBot] HTML 报告已生成：{output_path}")


def _build_rows(results: List[TestResult]) -> str:
    rows = []
    for i, r in enumerate(results):
        css_class = {
            "passed": "passedClass", "failed": "failedClass",
            "error": "brokenClass", "skipped": "skippedClass",
        }.get(r.status, "")
        log_id = f"log_{i}"
        log_escaped = _escape_html(r.log) if r.log else ""
        desc_escaped = _escape_html(r.description)
        row = f"""
            <tr class="{css_class}">
                <td>{_escape_html(r.class_name)}</td>
                <td>{_escape_html(r.case_name)}</td>
                <td>{desc_escaped}</td>
                <td>{r.duration}s</td>
                <td>{r.start_time}</td>
                <td>{r.status}</td>
                <td>
                    <a href="javascript:void(0)" onclick="showLog('{log_id}')">查看详情</a>
                    <div id="{log_id}" class="modal-overlay" style="display:none;">
                        <div class="modal-box">
                            <div class="modal-header">
                                <h5>日志详情</h5>
                                <button onclick="hideLog('{log_id}')">X</button>
                            </div>
                            <div class="modal-body"><pre>{log_escaped}</pre></div>
                        </div>
                    </div>
                </td>
            </tr>"""
        rows.append(row)
    return "\n".join(rows)
