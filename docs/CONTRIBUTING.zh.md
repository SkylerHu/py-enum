# 贡献指南

**中文** | [English](CONTRIBUTING.md)

感谢你对 py-enum 的关注！欢迎提交 Issue 和 Pull Request。

## 前置要求

- Python 3.9+
- [pre-commit](https://pre-commit.com/)

## 开发环境搭建

1. 克隆仓库并创建虚拟环境：

```bash
git clone https://github.com/skylerhu/py-enum.git
cd py-enum
python3 -m venv .env
source .env/bin/activate
```

2. 安装开发依赖：

```bash
pip install -U pip
pip install -r requirements_dev.txt
pip install -e .
```

3. 安装 pre-commit 钩子：

```bash
pre-commit install --hook-type pre-commit --hook-type commit-msg
```

## 项目结构

```
py-enum/
├── py_enum/              # 核心代码
├── tests/                # 测试用例
│   ├── app/              # Django App 模块
│   ├── conftest.py       # pytest 全局配置
│   └── settings.py       # Django settings（pytest.ini 中引用）
├── docs/                 # 文档
├── pytest.ini            # pytest 配置
├── .coveragerc           # 覆盖率工具配置
├── tox.ini               # 多版本 Python 测试配置
├── Makefile              # 构建、测试、发版等命令
├── .pre-commit-config.yaml
├── requirements_dev.txt
├── requirements_test.txt
└── MANIFEST.in
```

## 运行测试

```bash
# 运行全部测试
make test
# 或直接使用 pytest
pytest tests

# 运行指定文件或用例
pytest tests/test_choice.py
pytest tests/test_choice.py -k test_enum_value

# 多版本测试（通过 tox）
make test-all
```

## 代码覆盖率

```bash
make coverage
```

会在 `.coverage/htmlcov/` 生成 HTML 报告并自动打开浏览器。

## 代码风格

项目使用 [pre-commit](https://pre-commit.com/) 管理代码风格检查，提交时自动运行。也可以手动执行：

```bash
pre-commit run -a
```

## 提交 Pull Request

提交 PR 前，请确认以下事项：

- [ ] 包含对应的测试用例
- [ ] 通过全部测试：`make test-all`
- [ ] 覆盖率达标：`make coverage`
- [ ] 代码风格检查通过：`pre-commit run -a`
- [ ] 本地打包正常：`make dist`

## 发版（仅维护者）

```bash
make clean
make dist
twine upload -r pypi dist/py*
```

需要在 `~/.pypirc` 中配置 PyPI 凭证。
