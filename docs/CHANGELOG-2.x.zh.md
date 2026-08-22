# 变更日志

**中文** | [English](CHANGELOG-2.x.md)

本项目的所有重要变更都会记录在此文件中。

格式基于 [Keep a Changelog](https://keepachangelog.com/)，版本号遵循[语义化版本](https://semver.org/lang/zh-CN/)。

1.x 版本请查看 [CHANGELOG-1.x](./CHANGELOG-1.x.md)。

## 2.1.1

### 修复

- 调整 `.pyi` 中的 typing 声明。

## 2.1.0

### 变更

- 去掉对 Python 2 的支持，要求 `Python >= 3.6`。
- 继承原生 `Enum`，保障下游项目通过 mypy 检测。
- 去掉对 `six` 的依赖。

### 修复

- `ChoiceEnum` 强制增加了 `unique` 装饰器。

## 2.0.0

### 变更

- **不兼容升级**：`ChoiceEnum` 改为类似原生 `enum.Enum` 的使用方式，需通过 `.value` 访问值。
