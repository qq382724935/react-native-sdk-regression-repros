# [Android] Circle 数字颜色未转换，传给原生的类型不匹配

### 最小复现

[复现代码](https://github.com/qq382724935/react-native-sdk-regression-repros/tree/main/ble-and-gaode) — expo-gaode-map 2.3.2。

### 复现步骤

使用数字 ARGB 颜色：

```tsx
<Circle
  center={{ latitude: 39.9, longitude: 116.4 }}
  radius={100}
  fillColor={-2147483648}
  strokeColor={0}
/>
```

运行：`python3 run.py gaode-circle-color`。

**预期：** 支持公开类型允许的数字颜色，并保留透明度和零值。

**实际：** JS 直接传 number，而 Android 原生属性接收 String。

### 相关代码

```kotlin
Prop<String?>("fillColor") { view: CircleView, color ->
    view.setFillColor(color)
}
```

进入原生前将数字转换为等价字符串，例如 `-2147483648 → #80000000`、`0 → #00000000`。
