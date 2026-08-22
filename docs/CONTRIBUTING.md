# Contributing to py-enum

[中文文档](CONTRIBUTING.zh.md) | **English**

Thank you for your interest in contributing to py-enum! Issues and Pull Requests are welcome.

## Prerequisites

- Python 3.9+
- [pre-commit](https://pre-commit.com/)

## Development Setup

1. Clone the repository and create a virtual environment:

```bash
git clone https://github.com/skylerhu/py-enum.git
cd py-enum
python3 -m venv .env
source .env/bin/activate
```

2. Install development dependencies:

```bash
pip install -U pip
pip install -r requirements_dev.txt
pip install -e .
```

3. Install pre-commit hooks:

```bash
pre-commit install --hook-type pre-commit --hook-type commit-msg
```

## Project Structure

```
py-enum/
├── py_enum/              # Core library
├── tests/                # Test cases
│   ├── app/              # Django App module
│   ├── conftest.py       # pytest global config
│   └── settings.py       # Django settings (referenced in pytest.ini)
├── docs/                 # Documentation
├── pytest.ini            # pytest config
├── .coveragerc           # Coverage config
├── tox.ini               # Multi-version Python test config
├── Makefile              # Build, test, release commands
├── .pre-commit-config.yaml
├── requirements_dev.txt
├── requirements_test.txt
└── MANIFEST.in
```

## Running Tests

```bash
# Run all tests
make test
# Or use pytest directly
pytest tests

# Run specific file or test case
pytest tests/test_choice.py
pytest tests/test_choice.py -k test_enum_value

# Multi-version tests via tox
make test-all
```

## Code Coverage

```bash
make coverage
```

This generates an HTML report in `.coverage/htmlcov/` and opens it in your browser.

## Code Style

The project uses [pre-commit](https://pre-commit.com/) for code style checks, which runs automatically on commit. You can also run it manually:

```bash
pre-commit run -a
```

## Submitting a Pull Request

Before submitting a PR, please ensure the following:

- [ ] Includes corresponding test cases
- [ ] All tests pass: `make test-all`
- [ ] Coverage meets requirements: `make coverage`
- [ ] Code style checks pass: `pre-commit run -a`
- [ ] Local build succeeds: `make dist`

## Publishing (Maintainers Only)

```bash
make clean
make dist
twine upload -r pypi dist/py*
```

Requires PyPI credentials configured in `~/.pypirc`.
