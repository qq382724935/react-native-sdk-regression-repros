# [iOS] POI 缺少坐标时被错误返回为 (0, 0)

### 最小复现

[复现代码](https://github.com/qq382724935/react-native-sdk-regression-repros/tree/main/ble-and-gaode) — expo-gaode-map 2.3.2。

### 复现步骤

让 POI 的原生 `location` 为 nil，执行结果转换。

运行：`python3 run.py gaode-missing-coordinates`。

**预期：** 明确表示坐标缺失；真实的 (0, 0) 仍保留。

**实际：** 生成 `{ latitude: 0, longitude: 0 }`，把未知位置变成了真实地理点。

### 相关代码

```swift
"latitude": poi.location?.latitude ?? 0,
"longitude": poi.location?.longitude ?? 0
```

不要用 0 补齐未知坐标，并同步调整 POI.location 的可选类型。
