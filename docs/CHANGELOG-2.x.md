# Release Notes

## 2.1.0
- feat: 去掉对py2的支持，要求py>=3.6
    - 继承原生Enum，保障其他项目使用时能通过mypy检测

## 2.0.0
- `不兼容升级`：使用 `ChoiceEnum` 的方式类似原生的 `enum.Enum`，需要 `.value` 访问值
