# Changelog

[中文文档](CHANGELOG-2.x.zh.md) | **English**

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/), and this project adheres to [Semantic Versioning](https://semver.org/).

For 1.x releases, see [CHANGELOG-1.x](./CHANGELOG-1.x.md).

## 2.1.2

### Changed

- Updated package description.
- Added bilingual (English & Chinese) documentation support.

## 2.1.1

### Fixed

- Adjusted typing declarations in `.pyi` file.

## 2.1.0

### Changed

- Dropped Python 2 support; now requires `Python >= 3.6`.
- Inherits native `Enum` to ensure mypy compatibility in downstream projects.
- Removed dependency on `six`.

### Fixed

- Enforced `unique` decorator on `ChoiceEnum`.

## 2.0.0

### Changed

- **Breaking**: `ChoiceEnum` now follows native `enum.Enum` pattern — access values via `.value`.
