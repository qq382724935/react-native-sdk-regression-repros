# [Android] 搜索页码偏移，关闭扩展信息仍返回 all

### 最小复现

[复现代码](https://github.com/qq382724935/react-native-sdk-regression-repros/tree/main/ble-and-gaode) — expo-gaode-map 2.3.2。

### 复现步骤

1. 分别传 `pageNum: 1` 和 `pageNum: 2` 查询 POI。
2. 逆地理查询传 `requireExtension: false`。

运行：`python3 run.py gaode-search-options`。

**预期：** 传给高德的页码是 1、2；关闭扩展信息时传 `base`。

**实际：** 页码被减成 0、1；扩展信息始终传 `all`。

### 相关代码

```kotlin
query.pageNum = pageNum - 1
query.extensions = "all"
```

直接传入 pageNum，并根据 requireExtension 选择 all/base。[高德 setPageNum 说明](https://a.amap.com/lbs/static/unzip/Android_Map_Doc/Search/com/amap/api/services/poisearch/PoiSearch.Query.html)明确自 5.2.1 起页码从 1 开始。
