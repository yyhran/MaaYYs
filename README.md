
<!-- markdownlint-disable MD033 MD041 -->
<p align="center">
  <img alt="LOGO" src="R.png" width="256" height="256" />
</p>

<div align="center">

# MaaYYs

</div>

本仓库为 Tanyashue 所开发的痒痒鼠自动化应用，旨在帮助玩家完成日常任务。
**部分功能还在开发中--很多功能还并不完善**  
**由于MaaFw2.0还在更新,项目将迁移到2.0版本.部分功能会有bug**



---

## 功能介绍

MaaYYs 提供了一系列自动化工具，以简化玩家在游戏中的重复性操作。该项目支持以下功能：

- **每日任务自动化**：帮助玩家完成日常任务，如签到、领取奖励等。
- **樱饼挂副本**：提供简单的副本自动化功能，自动挂樱饼。
- **自定义任务**：支持用户自定义任务流程，满足不同的需求。

> **声明**: 本项目仅提供游戏中必要的每日任务自动化操作，不支持全自动战斗。对于副本，当前仅支持樱饼自动挂副本功能。  
> 由于游戏规则的限制，本项目不接受关于**自动探索副本**和**自动御魂副本**的代码合并请求。

---

## 安装与配置

### 环境依赖

- Python 3.8+
- [MaaFramework](https://github.com/MaaXYZ/MaaFramework) ==1.8.9
- PySide6

### 安装步骤

1. 克隆本仓库：
    ```bash
    git clone https://github.com/yourusername/MaaYYs.git
    ```

2. 安装依赖：
    ```bash
    pip install -r requirements.txt
    ```

3. 运行程序时用VSCODE：
    ```bash
    python src/main.py
    ```

---

## 贡献指南

欢迎各位开发者为本项目贡献代码！在提交 Pull Request 之前，请确保：

1. 遵循项目的代码风格和规范。
2. 避免提交全自动副本和御魂的相关功能代码。

---

## 常见问题

### 1. 为什么不支持全自动战斗？

出于对游戏规则的尊重，本项目仅限于完成每日任务，并不支持全自动战斗功能。

### 2. 可以自定义任务吗？

是的，用户可以通过编写自定义任务流程文件，灵活配置不同的任务自动化操作。

### 3. 为什么我的游戏里部分场景无法识别

因为大部分场景我都没有 (┬┬﹏┬┬)  
欢迎大家提供素材

---

## 鸣谢

本项目由 **[MaaFramework](https://github.com/MaaXYZ/MaaFramework)** 强力驱动！

