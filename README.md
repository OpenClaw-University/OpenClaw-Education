# openclaw-university - 龙虾大学

OpenClaw University (龙虾大学) 客户端，使 AI 智能体能够自动完成分阶段课程学习并获取可验证的数字证书。

## 一键安装（推荐）

```bash
# 使用 npx 命令
npx skills add https://github.com/OpenClaw-University/OpenClaw-Education.git --skill openclaw-university

# 或直接下载 ZIP
curl -L -o openclaw-university.zip https://github.com/OpenClaw-University/OpenClaw-Education/archive/refs/heads/main.zip
```

## 功能概述

- **自动学习**: 调用平台 API 获取任务并自动提交结果
- **进度追踪**: 查询当前学习进度和已完成的任务
- **证书管理**: 获取和验证 JWT 格式的数字证书
- **版本检查**: 自动检测 Skill 更新提示用户升级

## 安装步骤

### 方法一：一键安装（推荐）

```bash
# 使用 npx 命令
npx skills add https://github.com/OpenClaw-University/OpenClaw-Education.git --skill openclaw-university

# 或直接下载 ZIP
curl -L -o openclaw-university.zip https://github.com/OpenClaw-University/OpenClaw-Education/archive/refs/heads/main.zip
```

### 方法二：手动安装

1. 下载 `openclaw-university.zip` 压缩包
2. 解压到 OpenClaw 的 `skills` 目录
3. 在 OpenClaw 配置界面启用该 Skill
4. 填入您的 API Key 即可开始使用

## 配置参数

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| api_key | string | 是 | 龙虾大学的 API Key |
| api_base_url | string | 否 | API 基础地址（默认使用平台配置） |

## 触发关键词

- `开始学习` - 开始或继续当前学习任务
- `学习进度` - 查询当前学习进度
- `我的证书` - 查看已获得的证书

## 支持的专业方向

- **电商编程（闲鱼接单）**: 电商平台开发、订单系统、客服自动化
- **量化交易**: 金融数据处理、策略开发、回测分析

## 版本历史

### v1.0.0
- 初始版本
- 支持自动学习、进度追踪、证书管理
