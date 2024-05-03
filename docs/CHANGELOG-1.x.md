# Release Notes

## 1.1.1 (2024-05-03)
- feat: `ChoiceEnum`增加`choices`/`values`/`labels`三个属性的访问
- fix: `ChoiceEnum`的`__contains__`方法可用于member实例化对象的判断

## 1.1.0 (2024-04-24)
- feat: 增加方法`ChoiceEnum.to_js_enum`返回数组数据，可以用于前端枚举库js-enumerate使用
- test: 补充了`ChoiceEnum`在`argparse`choice中使用的测试用例

## 1.0.1 (2023-09-28)
- fix: 调整初始化方法`_EnumDict.py2_init`，修复Python2版本在`Enum`中使用`_ignore_`的问题

## 1.0.0 (2023-09-27)
- build: lib发版
