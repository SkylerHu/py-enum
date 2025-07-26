# 前言
主要是给开发者阅读，描述开发前后需要注意的一些事项。

# 开发环境
- `> python3.6`的python环境
- 新建虚拟环境`.env`在项目根目录下，`source .env/bin/activate`
  - virtualenv --python=python2 .env
  - pyvenv3 .env
  - python3 -m venv .env
- `pip install -U -r requirements_dev.txt`
- 系统安装`brew install pre-commit` 或者 `pip install pre-commit`
  - brew安装`/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install.sh)"`
  - 在项目更目录下执行`pre-commit install --hook-type pre-commit --hook-type commit-msg`
- 可通过`pip install -e ./`编辑模式安装用于边开发边测试使用

# 项目部分结构说明
- `pytest.ini` 测试脚本的配置
- `.coveragerc` 测试覆盖度工具使用的配置，在pytest.ini中引用
- `.pre-commit-config.yaml` git提交代码前pre-commit执行的检测相关配置
- `requirements_dev.txt` 开发需要的环境
- `requirements_test.txt` 跑测试用例需要的环境
- `tests` 测试用例目录
  - `app` 对应Django中的App模块，定义了数据库等
  - `conftest.py` pytest测试用例全局变量配置
  - `settings` Django settings配置，在pytest.ini中引用
- `py_eunm` lib核心代码
- `MANIFEST.in` 打包相关-清单文件配置
- `Makefile` 构建配置，可以执行`make help`查看具体命令
  - 定义了测试、打包、发版等很多命令
- `tox.ini` 定义各种Python版本的测试

# 提交Pull Request
提交Pull Request之前需要检查以下事项是否完成：
- 需包含测试用例，并通过`make test-all`
- 测试覆盖度要求 `make coverage`
- 尝试本地打包 `make dist`

# 运行测试用例

    pytest tests
    # 或者跑部分测试用例
    pytest tests/test_choice.py
    pytest tests/test_choice.py -k test_enum_value

# 打包发版
（以下命令都定义在了Makefile中了）
- `make clean-build` 删除本地构建缓存目录：`py_enum.egg-info`和`dist`
- `python setup.py sdist bdist_wheel --universal` 执行打包
- `twine check dist/*` 检查生成的文件是否符合pypi的要求
- `twine upload -r pypi dist/py*` 上传包
  - 需要本地`~/.pypirc`配置用户名密码
- ~~或者直接打包上传 `python setup.py sdist upload -r pypi` (已废弃)~~

# TODO
- 接入`tox-travis`实现自动化发版
