# [Android] 单独调整地图缩放不生效，移动中心点会重置地图视角

### 最小复现

[复现代码](https://github.com/qq382724935/react-native-sdk-regression-repros/tree/main/ble-and-gaode) — expo-gaode-map 2.3.2。

### 复现步骤

1. 当前地图缩放为 12，倾斜角为 20，方向角为 30。
2. 调用 `moveCamera({ zoom: 16 })`。
3. 再调用 `moveCamera({ target: { latitude: 39.9, longitude: 116.4 } })`。

运行：`python3 run.py gaode-camera`。

**预期：** 第二步缩放变为 16；第三步只移动中心点，保留缩放和角度。

**实际：** 第二步没有变化；第三步把缩放、倾斜角和方向角都重置为 0。

### 相关代码

```kotlin
if (target != null) {
    val builder = CameraPosition.Builder().target(latLng)
    // Apply supplied zoom, tilt and bearing.
}
```

从当前 `aMap.cameraPosition` 创建 Builder，只修改传入的字段；没有 target 时也应处理 zoom、tilt 和 bearing。
