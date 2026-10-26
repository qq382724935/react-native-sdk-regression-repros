# [Android] initSDK 设置的 key 无法用于搜索

### 最小复现

[复现代码](https://github.com/qq382724935/react-native-sdk-regression-repros/tree/main/ble-and-gaode) — expo-gaode-map 2.3.2。

### 复现步骤

1. 不在 Manifest 配置 key。
2. 调用公开的 `initSDK` 设置运行时 key。
3. 发起搜索。

运行：`python3 run.py gaode-search-initialization`。

**预期：** 搜索复用 initSDK 已设置的 key。

**实际：** 地图和定位收到 key，搜索仍只检查 Manifest 并报缺少配置。

### 相关代码

```kotlin
MapsInitializer.setApiKey(androidKey)
AMapLocationClient.setApiKey(androidKey)
// Search ensureAPIKeyIsSet() only reads Manifest metadata.
```

保存并复用 initSDK 收到的 key。发行包 `build/search/index.js` 已说明调用 initSDK 后无需再次配置搜索。
