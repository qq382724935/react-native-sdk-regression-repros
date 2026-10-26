# [Android] 单次定位启动失败后没有释放定位对象

### 最小复现

[复现代码](https://github.com/qq382724935/react-native-sdk-regression-repros/tree/main/ble-and-gaode) — expo-gaode-map 2.3.2。

### 复现步骤

让 `setLocationOption()` 在创建定位对象后抛出异常。

运行：`python3 run.py gaode-single-location-cleanup`。

**预期：** 失败后调用 stopLocation 和 onDestroy，释放已创建的对象。

**实际：** 清理只放在定位回调内；配置阶段抛错后，两者都不会执行。

### 相关代码

```kotlin
val tempClient = AMapLocationClient(appContext)
tempClient.setLocationOption(onceOption)
tempClient.setLocationListener { location ->
    // Return the result.
    tempClient.stopLocation()
    tempClient.onDestroy()
}
tempClient.startLocation()
```

配置和启动异常也应进入同一个清理入口，确保只结束一次。
