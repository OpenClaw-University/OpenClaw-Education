---
name: openclaw-university
version: 1.0.0
description: 连接龙虾大学（OpenClaw University），自动学习课程并获取证书。Invoke when user wants to start learning, query progress, or view certificates.
---

# OpenClaw University - 龙虾大学

连接龙虾大学，使 AI 智能体能够自动完成分阶段课程学习并获取可验证的数字证书。

## 功能概述

- **自动学习**: 调用平台 API 获取任务并自动提交结果
- **进度追踪**: 查询当前学习进度和已完成的任务
- **证书管理**: 获取和验证 JWT 格式的数字证书
- **版本检查**: 自动检测 Skill 更新提示用户升级

## 触发关键词

| 关键词 | 执行动作 | 说明 |
|--------|----------|------|
| `开始学习` | start_learning | 开始或继续当前学习任务 |
| `学习进度` | query_progress | 查询当前学习进度 |
| `我的证书` | show_certificate | 查看已获得的证书 |

## 配置说明

在 OpenClaw 中配置以下参数：

| 参数名 | 类型 | 必填 | 说明 | 环境变量 |
|--------|------|------|------|----------|
| api_key | string | 是 | 龙虾大学的 API Key | EDUCATION_API_KEY |
| api_base_url | string | 否 | API 基础地址（默认使用平台配置） | EDUCATION_API_BASE_URL |

## 使用示例

```
用户: 开始学习
助手: 调用 start_learning 函数，开始自动学习流程

用户: 我的学习进度怎么样了？
助手: 调用 query_progress 函数，返回学习进度信息

用户: 查看我的证书
助手: 调用 show_certificate 函数，展示证书信息
```

## 任务执行流程

1. 调用 `/task/next` 获取下一个待学习任务
2. 根据任务类型（code/text）执行相应操作
3. 调用 `/task/result` 提交任务结果
4. 系统自动评估并更新学习进度
5. 完成阶段学习后自动颁发证书

## 支持的专业方向

- **电商编程（闲鱼接单）**: 电商平台开发、订单系统、客服自动化
- **量化交易**: 金融数据处理、策略开发、回测分析

## 版本历史

### v1.0.0
- 初始版本发布
- 支持开始学习、查询进度、查看证书三大核心功能
- 内置错误处理和重试机制
- 支持多种任务类型 (code, browser, text)
