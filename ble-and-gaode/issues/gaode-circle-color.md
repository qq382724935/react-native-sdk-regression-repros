# [2.3.2][Android] Circle 公开支持的数字 ARGB 直接进入 String 原生属性

公开 `ColorValue` 明确支持 Android 数字格式 `0xAARRGGBB`，Circle 的 fillColor/strokeColor 使用该类型；但 Circle 原样透传 number，而 Android CircleViewModule 声明 `Prop<String?>`。

独立复现执行实际发行 Circle JS，只替换 React/native view 边界，并核对发行包中的公开类型与原生属性声明。输入 fillColor=-2147483648、strokeColor=0，进入原生视图的仍是两个 number，而不是其字符串表示。

把合法的有/无符号 32 位 ARGB 序列化为等价 `#AARRGGBB` 后，同一代码输出 `#80000000` 和 `#00000000`，不丢弃透明度或合法零值。此报告只依赖明确文档化的 Android 数字颜色支持，不把 iOS 数字颜色扩展当作要求。

没有把受控原生属性捕获当成设备渲染验收。检索现有 issues/PRs 未找到对应颜色类型问题；#5 讨论页面返回后的覆盖物恢复。

Reproduction: [standalone source and fixtures](https://github.com/qq382724935/react-native-sdk-regression-repros/tree/main/ble-and-gaode).

```sh
python3 run.py gaode-circle-color
```

Actual before output:
```text
{"fillColor":-2147483648,"strokeColor":0,"nativePropType":"string"}
```

Actual fix output:
```text
{"fillColor":"#80000000","strokeColor":"#00000000","nativePropType":"string"}
```


Environment: macOS 27.0.1; Node 22.23.3, Python 3.9.6, JDK 17 / Kotlin CLI for Android-method cases, Swift 6.4 / Foundation for iOS-method cases. Consumer React Native version: 0.88.0. No full-app or physical-device reproduction is claimed. Prepared with AI assistance; the published methods and before/fix commands were checked locally.
