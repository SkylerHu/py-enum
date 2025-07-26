# Release Notes

## 2.0.0
- `不兼容升级`
    - 去掉对python2等低版本的支持，要求python>=3.6
    - 仅提供 `ChoiceEnum` 的使用，使用方式类似原生的 `enum.Enum`，需要 `.value` 访问值
