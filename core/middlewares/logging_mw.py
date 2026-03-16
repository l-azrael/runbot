# --coding:utf-8--
import json
from typing import Callable

import allure
from emoji import emojize

from core.middlewares.base import middleware
from core.log.log import logger, runbot_logger


@middleware(name="logging", priority=900)
def logging_mw(request: dict, call_next: Callable) -> dict:
    response = call_next(request)

    level = runbot_logger.get_level()
    is_debug = level <= 10

    url = request.get("url", "")
    method = request.get("method", "")
    api_name = request.get("_api_name", url)

    log_data = {
        "url": url,
        "method": method if is_debug else None,
        "headers": request.get("headers") if is_debug else None,
        "params": request.get("params"),
        "data": request.get("data"),
        "json": request.get("json"),
        "status_code": response.get("status_code") if is_debug else None,
        "elapsed": response.get("elapsed") if is_debug else None,
        "response_body": response.get("body"),
    }
    # 过滤 None
    log_data = {k: v for k, v in log_data.items() if v is not None}

    sep = "=" * 80
    emoji_a = emojize(":A_button_(blood_type):")
    emoji_req = emojize(":rocket:")
    emoji_rep = emojize(":check_mark_button:")

    msg = (
        f"\n{sep}\n"
        f"{emoji_a} <API>: {api_name}\n"
        f"{emoji_req} <Request>  URL: {url}\n"
    )
    if log_data.get("params"):
        msg += f"     Params: {log_data['params']}\n"
    if log_data.get("json"):
        msg += f"     Body: {log_data['json']}\n"
    msg += f"{emoji_rep} <Response> Body: {log_data.get('response_body')}\n{sep}"

    if is_debug:
        logger.debug(msg)
    else:
        logger.info(msg)

    try:
        allure_data = {k: v for k, v in log_data.items()}
        allure.attach(
            json.dumps(allure_data, indent=2, ensure_ascii=False),
            name=api_name,
            attachment_type=allure.attachment_type.JSON,
        )
    except Exception:
        pass

    return response
