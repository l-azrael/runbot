# --coding:utf-8--
"""RunBot HTML 报告模板"""

HTML_TEMPLATE = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<title>RunBot 测试报告</title>
<style>
body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; font-size: 14px; background: #f5f9fc; margin: 0; padding: 20px; }}
.container {{ max-width: 1200px; margin: 0 auto; }}
h1 {{ color: #333; font-size: 22px; }}
.summary {{ display: flex; gap: 16px; margin-bottom: 24px; flex-wrap: wrap; }}
.card {{ background: #fff; border-radius: 8px; padding: 20px; box-shadow: 0 1px 4px rgba(0,0,0,0.08); flex: 1; min-width: 180px; }}
.card .label {{ font-size: 12px; color: #888; margin-bottom: 4px; }}
.card .value {{ font-size: 28px; font-weight: bold; }}
.card .rate {{ font-size: 12px; margin-top: 4px; }}
.progress {{ height: 6px; background: #eee; border-radius: 3px; margin-top: 6px; }}
.progress-bar {{ height: 100%; border-radius: 3px; }}
.bg-success {{ background: #5fc27e; }}
.bg-warning {{ background: #fcc100; }}
.bg-danger {{ background: #f44455; }}
.bg-secondary {{ background: #6c757d; }}
.text-success {{ color: #5fc27e; }}
.text-warning {{ color: #fcc100; }}
.text-danger {{ color: #f44455; }}
.text-secondary {{ color: #6c757d; }}
.info-card {{ background: #fff; border-radius: 8px; padding: 20px; box-shadow: 0 1px 4px rgba(0,0,0,0.08); margin-bottom: 24px; }}
.info-item {{ padding: 8px 0; border-bottom: 1px solid #f0f0f0; }}
.info-item:last-child {{ border-bottom: none; }}
.filter-bar {{ margin-bottom: 16px; }}
.filter-bar a {{ display: inline-block; padding: 6px 16px; border-radius: 4px; color: #fff; text-decoration: none; margin-right: 6px; font-size: 13px; }}
.btn-pass {{ background: #5fc27e; }}
.btn-fail {{ background: #fcc100; }}
.btn-error {{ background: #f44455; }}
.btn-skip {{ background: #6c757d; }}
.btn-all {{ background: #17a2b8; }}
table {{ width: 100%; border-collapse: collapse; background: #fff; border-radius: 8px; overflow: hidden; box-shadow: 0 1px 4px rgba(0,0,0,0.08); }}
th {{ background: #f8f9fa; padding: 12px; text-align: left; font-weight: 600; color: #555; border-bottom: 2px solid #dee2e6; }}
td {{ padding: 10px 12px; border-bottom: 1px solid #f0f0f0; }}
.passedClass {{ background: #f0faf4; }}
.failedClass {{ background: #fff8e6; }}
.brokenClass {{ background: #fef0f2; }}
.skippedClass {{ background: #f5f5f5; }}
</style>
</head>
<body>
<div class="container">
<h1>RunBot 测试报告</h1>
"""

HTML_TEMPLATE += """
<div class="info-card">
<div class="info-item"><strong>开始时间 - 结束时间：</strong>{start_time} - {end_time}</div>
<div class="info-item"><strong>运行时长：</strong>{duration}</div>
<div class="info-item"><strong>统计：</strong>
  <span class="text-success">通过:{passed}</span> &nbsp;
  <span class="text-warning">失败:{failed}</span> &nbsp;
  <span class="text-danger">错误:{error}</span> &nbsp;
  <span class="text-secondary">跳过:{skipped}</span>
</div>
</div>

<div class="summary">
  <div class="card">
    <div class="label">通过</div>
    <div class="value text-success">{passed}</div>
    <div class="rate">{pass_rate}% 通过率</div>
    <div class="progress"><div class="progress-bar bg-success" style="width:{pass_rate}%"></div></div>
  </div>
  <div class="card">
    <div class="label">失败</div>
    <div class="value text-warning">{failed}</div>
    <div class="rate">{fail_rate}% 失败率</div>
    <div class="progress"><div class="progress-bar bg-warning" style="width:{fail_rate}%"></div></div>
  </div>
  <div class="card">
    <div class="label">错误</div>
    <div class="value text-danger">{error}</div>
    <div class="rate">{error_rate}% 错误率</div>
    <div class="progress"><div class="progress-bar bg-danger" style="width:{error_rate}%"></div></div>
  </div>
  <div class="card">
    <div class="label">跳过</div>
    <div class="value text-secondary">{skipped}</div>
    <div class="rate">-</div>
    <div class="progress"><div class="progress-bar bg-secondary" style="width:0"></div></div>
  </div>
</div>

<div class="filter-bar">
  <a href="javascript:showCase('passed')" class="btn-pass">通过</a>
  <a href="javascript:showCase('failed')" class="btn-fail">失败</a>
  <a href="javascript:showCase('error')" class="btn-error">错误</a>
  <a href="javascript:showCase('skipped')" class="btn-skip">跳过</a>
  <a href="javascript:showCase('all')" class="btn-all">所有</a>
</div>

<table>
<thead><tr>
  <th>测试类</th><th>测试用例</th><th>用例描述</th>
  <th>时长</th><th>开始时间</th><th>运行结果</th><th>查看详情</th>
</tr></thead>
<tbody>
{rows}
</tbody>
</table>
</div>
"""

HTML_TEMPLATE += """
<script>
function showCase(status) {{
  var trs = document.querySelectorAll("tbody tr");
  for (var i = 0; i < trs.length; i++) {{
    var td = trs[i].children[5];
    if (!td) continue;
    var s = td.textContent.trim();
    trs[i].style.display = (status === "all" || s === status) ? "" : "none";
  }}
}}
function showLog(id) {{
  document.getElementById(id).style.display = "flex";
  document.body.style.overflow = "hidden";
}}
function hideLog(id) {{
  document.getElementById(id).style.display = "none";
  document.body.style.overflow = "auto";
}}
</script>
<style>
.modal-overlay {{ position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.6); z-index:999; display:flex; align-items:center; justify-content:center; }}
.modal-box {{ background:#fff; border-radius:8px; width:70%; max-height:70%; overflow:auto; }}
.modal-header {{ display:flex; justify-content:space-between; align-items:center; padding:12px 20px; border-bottom:1px solid #eee; }}
.modal-header h5 {{ margin:0; }}
.modal-header button {{ border:none; background:#eee; border-radius:4px; padding:4px 10px; cursor:pointer; }}
.modal-body {{ padding:16px 20px; }}
.modal-body pre {{ background:#f5f7fa; padding:12px; border-radius:4px; overflow:auto; max-height:400px; font-size:12px; white-space:pre-wrap; word-break:break-all; }}
</style>
</body></html>
"""
