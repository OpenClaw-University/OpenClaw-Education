# -*- coding: utf-8 -*-
"""
龙虾大学 (OpenClaw University) 客户端 - handler.py
实现 start_learning, query_progress, show_certificate 三个核心函数
"""

import os
import time
import logging
import json
import re
from typing import Dict, Any, Optional
from urllib.parse import urljoin

try:
    import requests
except ImportError:
    raise ImportError("requests 库未安装，请运行: pip install requests")

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("education_client")

# 默认配置
DEFAULT_API_BASE_URL = "https://your-platform.com/api/v1"
DEFAULT_TIMEOUT = 10  # 请求超时时间（秒）
DEFAULT_MAX_RETRIES = 3  # 最大重试次数


def _get_config() -> Dict[str, Any]:
    """
    获取配置信息
    优先从环境变量读取，其次使用默认值
    """
    return {
        "api_key": os.environ.get("EDUCATION_API_KEY", ""),
        "api_base_url": os.environ.get(
            "EDUCATION_API_BASE_URL",
            DEFAULT_API_BASE_URL
        ),
        "timeout": DEFAULT_TIMEOUT,
        "max_retries": DEFAULT_MAX_RETRIES
    }


def _make_request(
    method: str,
    url: str,
    headers: Optional[Dict[str, str]] = None,
    json_data: Optional[Dict[str, Any]] = None,
    params: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    发送 HTTP 请求的封装函数
    包含错误处理和重试机制

    Args:
        method: HTTP 方法 (GET/POST/DELETE)
        url: 请求 URL
        headers: 请求头
        json_data: JSON 请求体
        params: URL 查询参数

    Returns:
        响应的 JSON 数据

    Raises:
        requests.exceptions.RequestException: 请求失败时抛出
    """
    config = _get_config()
    timeout = config["timeout"]
    max_retries = config["max_retries"]

    for attempt in range(max_retries):
        try:
            if method.upper() == "GET":
                response = requests.get(
                    url,
                    headers=headers,
                    params=params,
                    timeout=timeout
                )
            elif method.upper() == "POST":
                response = requests.post(
                    url,
                    headers=headers,
                    json=json_data,
                    timeout=timeout
                )
            elif method.upper() == "DELETE":
                response = requests.delete(
                    url,
                    headers=headers,
                    timeout=timeout
                )
            else:
                raise ValueError(f"不支持的 HTTP 方法: {method}")

            # 检查 HTTP 状态码
            response.raise_for_status()

            # 解析响应
            try:
                return response.json()
            except json.JSONDecodeError:
                return {"raw_response": response.text}

        except requests.exceptions.Timeout:
            logger.warning(f"请求超时 (尝试 {attempt + 1}/{max_retries}): {url}")
            if attempt == max_retries - 1:
                raise requests.exceptions.Timeout(
                    f"请求超时，已达到最大重试次数 ({max_retries})"
                )
            time.sleep(1.5 ** attempt)  # 指数退避

        except requests.exceptions.ConnectionError as e:
            logger.warning(f"连接错误 (尝试 {attempt + 1}/{max_retries}): {e}")
            if attempt == max_retries - 1:
                raise requests.exceptions.ConnectionError(
                    f"无法连接到服务器: {url}"
                )
            time.sleep(1.5 ** attempt)

        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP 错误: {e}")
            raise

        except requests.exceptions.RequestException as e:
            logger.error(f"请求异常: {e}")
            raise


def _execute_task(description: str, context: Dict[str, Any]) -> str:
    """
    执行任务的扩展点函数
    根据任务类型调用不同的执行逻辑

    Args:
        description: 任务描述
        context: 执行上下文

    Returns:
        任务执行结果
    """
    # 获取任务类型，默认为 text
    task_type = context.get("task_type", "text")

    logger.info(f"开始执行任务 (类型: {task_type})")

    if task_type == "code":
        # 代码编写任务 - 这里预留扩展点
        # 后续可以调用代码执行环境或外部服务
        return "# Python 代码任务执行结果\n# 此处预留代码执行逻辑\nprint('Hello, World!')"

    elif task_type == "browser":
        # 浏览器操作任务 - 预留扩展
        return "浏览器操作任务已完成"

    else:
        # 文本问答任务 - 默认处理
        # 提取关键信息并生成响应
        return f"已完成任务: {description}"


def _build_headers(api_key: str) -> Dict[str, str]:
    """
    构建请求头

    Args:
        api_key: API Key

    Returns:
        包含认证信息的请求头
    """
    return {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "User-Agent": "OpenClaw-Education-Client/1.0.0"
    }


def start_learning(context: Dict[str, Any]) -> Dict[str, Any]:
    """
    开始或继续学习任务
    流程:
    1. 调用 /task/next 获取下一个任务
    2. 如果没有任务，调用 /certificate 获取证书
    3. 执行任务并提交结果

    Args:
        context: 包含配置信息的字典

    Returns:
        包含 reply 字段的响应字典
    """
    config = _get_config()
    api_key = config["api_key"]
    api_base_url = config["api_base_url"]

    # 检查 API Key 是否配置
    if not api_key:
        return {
            "reply": (
                "❌ API Key 未配置！\n\n"
                "请先在 OpenClaw 中配置您的 API Key:\n"
                "- 配置项: api_key\n"
                "- 环境变量: EDUCATION_API_KEY\n\n"
                "您可以在教育平台的用户中心生成新的 API Key。"
            ),
            "success": False
        }

    headers = _build_headers(api_key)

    try:
        # 步骤 1: 获取下一个任务
        next_task_url = urljoin(api_base_url, "/task/next")
        logger.info("正在获取下一个学习任务...")

        task_response = _make_request(
            "GET",
            next_task_url,
            headers=headers
        )

        # 检查是否没有待完成的任务
        if task_response.get("status") == "completed":
            logger.info("所有课程已完成，获取证书信息")
            return _get_certificate(api_base_url, headers)

        # 提取任务信息
        task_id = task_response.get("task_id")
        description = task_response.get("description", "")
        task_type = task_response.get("type", "text")

        if not task_id:
            return {
                "reply": "⚠️ 获取任务失败：未返回有效的任务 ID",
                "success": False
            }

        # 步骤 2: 执行任务
        logger.info(f"正在执行任务 {task_id}...")
        task_context = {
            "task_type": task_type,
            "task_id": task_id
        }
        result = _execute_task(description, task_context)

        # 步骤 3: 提交任务结果
        submit_url = urljoin(api_base_url, "/task/result")
        logger.info(f"正在提交任务 {task_id} 的结果...")

        submit_data = {
            "task_id": task_id,
            "result": result,
            "execution_time": 0  # 可以记录实际执行时间
        }

        submit_response = _make_request(
            "POST",
            submit_url,
            headers=headers,
            json_data=submit_data
        )

        # 解析评估结果
        correct = submit_response.get("correct", False)
        message = submit_response.get("message", "")
        next_stage_unlocked = submit_response.get("next_stage_unlocked", False)

        # 构建回复消息
        if correct:
            reply = f"✅ 任务完成正确！\n\n"
            reply += f"📝 评估反馈: {message}\n\n"

            if next_stage_unlocked:
                reply += "🎉 恭喜！已解锁下一个学习阶段！\n"
                reply += "继续说「开始学习」进入下一阶段。"
            else:
                reply += "继续说「开始学习」获取下一个任务。"
        else:
            reply = f"❌ 任务评估未通过\n\n"
            reply += f"📝 反馈: {message}\n\n"
            reply += "请检查任务要求后重试，说「开始学习」重新尝试。"

        return {
            "reply": reply,
            "success": correct,
            "task_id": task_id,
            "next_stage_unlocked": next_stage_unlocked
        }

    except requests.exceptions.Timeout:
        logger.error("请求超时")
        return {
            "reply": (
                "⏰ 连接超时，请检查网络后重试。\n"
                "可以说「开始学习」重试。"
            ),
            "success": False
        }

    except requests.exceptions.ConnectionError:
        logger.error("无法连接到服务器")
        return {
            "reply": (
                "🌐 无法连接到教育平台服务器。\n"
                "请检查:\n"
                "1. API 基础地址是否正确\n"
                "2. 网络连接是否正常\n\n"
                "当前配置的地址: " + api_base_url
            ),
            "success": False
        }

    except Exception as e:
        logger.error(f"学习流程异常: {e}")
        return {
            "reply": f"⚠️ 学习过程中出现错误: {str(e)}",
            "success": False
        }


def query_progress(context: Dict[str, Any]) -> Dict[str, Any]:
    """
    查询当前学习进度

    Returns:
        包含学习进度信息的响应字典
    """
    config = _get_config()
    api_key = config["api_key"]
    api_base_url = config["api_base_url"]

    if not api_key:
        return {
            "reply": (
                "❌ API Key 未配置！\n\n"
                "请先在 OpenClaw 中配置您的 API Key。"
            ),
            "success": False
        }

    headers = _build_headers(api_key)

    try:
        progress_url = urljoin(api_base_url, "/progress")
        logger.info("正在查询学习进度...")

        response = _make_request(
            "GET",
            progress_url,
            headers=headers
        )

        # 提取进度信息
        major = response.get("major", "未知")
        stage = response.get("stage", "未知")
        completed = response.get("completed", 0)
        total = response.get("total", 0)
        next_stage = response.get("next_stage", "无")

        # 计算进度百分比
        percentage = (completed / total * 100) if total > 0 else 0

        # 构建进度条
        bar_length = 20
        filled = int(bar_length * completed / total) if total > 0 else 0
        progress_bar = "█" * filled + "░" * (bar_length - filled)

        reply = f"📊 学习进度\n\n"
        reply += f"🎯 专业方向: {major}\n"
        reply += f"📍 当前阶段: {stage}\n"
        reply += f"📈 进度: [{progress_bar}] {completed}/{total} ({percentage:.1f}%)\n"
        reply += f"⏭️ 下一阶段: {next_stage}\n"

        return {
            "reply": reply,
            "success": True,
            "progress": {
                "major": major,
                "stage": stage,
                "completed": completed,
                "total": total,
                "percentage": percentage
            }
        }

    except requests.exceptions.Timeout:
        return {
            "reply": "⏰ 查询超时，请检查网络后重试。",
            "success": False
        }

    except requests.exceptions.ConnectionError:
        return {
            "reply": "🌐 无法连接到教育平台服务器。",
            "success": False
        }

    except Exception as e:
        logger.error(f"查询进度异常: {e}")
        return {
            "reply": f"⚠️ 查询进度失败: {str(e)}",
            "success": False
        }


def show_certificate(context: Dict[str, Any]) -> Dict[str, Any]:
    """
    查看已获得的证书

    Args:
        context: 上下文信息

    Returns:
        包含证书信息的响应字典
    """
    config = _get_config()
    api_key = config["api_key"]
    api_base_url = config["api_base_url"]

    if not api_key:
        return {
            "reply": (
                "❌ API Key 未配置！\n\n"
                "请先在 OpenClaw 中配置您的 API Key。"
            ),
            "success": False
        }

    headers = _build_headers(api_key)

    try:
        # 调用证书获取接口
        return _get_certificate(api_base_url, headers)

    except Exception as e:
        logger.error(f"获取证书异常: {e}")
        return {
            "reply": f"⚠️ 获取证书失败: {str(e)}",
            "success": False
        }


def _get_certificate(
    api_base_url: str,
    headers: Dict[str, str]
) -> Dict[str, Any]:
    """
    从 API 获取证书信息的内部函数

    Args:
        api_base_url: API 基础地址
        headers: 请求头

    Returns:
        包含证书信息的响应字典
    """
    cert_url = urljoin(api_base_url, "/certificate")
    logger.info("正在获取证书...")

    response = _make_request(
        "GET",
        cert_url,
        headers=headers
    )

    certificate_jwt = response.get("certificate_jwt", "")
    major = response.get("major", "未知")
    stage = response.get("stage", "未知")
    issued_at = response.get("issued_at", "未知")
    cert_id = response.get("cert_id", "未知")
    skills = response.get("skills", [])

    if not certificate_jwt:
        return {
            "reply": (
                "📜 暂无证书\n\n"
                "完成当前专业方向的全部课程后即可获得证书。\n"
                "继续说「开始学习」完成任务吧！"
            ),
            "success": False
        }

    # 构建证书展示信息
    reply = f"🎓 数字证书\n\n"
    reply += f"━━━━━━━━━━━━━━━━━━━━\n"
    reply += f"📛 专业: {major}\n"
    reply += f"🎯 阶段: {stage}\n"
    reply += f"🆔 证书ID: {cert_id}\n"
    reply += f"📅 颁发时间: {issued_at}\n"
    reply += f"🛠️ 技能: {', '.join(skills) if skills else '无'}\n"
    reply += f"━━━━━━━━━━━━━━━━━━━━\n\n"
    reply += f"✅ 证书验证: 可通过平台 API 进行验签\n"
    reply += f"🔐 证书格式: JWT\n\n"
    reply += f"恭喜完成 {major} {stage} 阶段学习！"

    return {
        "reply": reply,
        "success": True,
        "certificate": {
            "major": major,
            "stage": stage,
            "cert_id": cert_id,
            "issued_at": issued_at,
            "skills": skills
        }
    }


def check_version(context: Dict[str, Any]) -> Dict[str, Any]:
    """
    检查 Skill 最新版本（供内部使用或扩展）

    Returns:
        版本信息
    """
    config = _get_config()
    api_base_url = config["api_base_url"]

    try:
        version_url = urljoin(api_base_url, "/skill/latest-version")
        response = _make_request("GET", version_url)

        latest_version = response.get("version", "未知")
        download_url = response.get("download_url", "")
        changelog = response.get("changelog", "")

        current_version = "1.0.0"

        reply = f"📦 Skill 版本信息\n\n"
        reply += f"当前版本: {current_version}\n"
        reply += f"最新版本: {latest_version}\n\n"

        if latest_version != current_version:
            reply += "🆕 发现新版本！请更新 Skill 以获得最新功能。\n\n"
            reply += f"更新日志:\n{changelog}\n\n"
            reply += f"下载地址: {download_url}"
        else:
            reply += "✅ 您使用的是最新版本！"

        return {
            "reply": reply,
            "success": True,
            "needs_update": latest_version != current_version,
            "latest_version": latest_version
        }

    except Exception as e:
        logger.error(f"检查版本异常: {e}")
        return {
            "reply": f"⚠️ 检查版本失败: {str(e)}",
            "success": False
        }
