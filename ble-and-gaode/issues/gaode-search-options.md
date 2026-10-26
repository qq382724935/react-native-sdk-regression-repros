# [2.3.2][Android] pageNum 减一且 requireExtension=false 仍发送 all

2.3.2 的公开 `POISearchOptions.pageNum` 说明从 1 开始；`ReGeocodeOptions.requireExtension` 说明控制是否返回扩展信息。但 Android 实现分别使用 `query.pageNum = pageNum - 1` 和固定 `query.extensions = "all"`。

官方 [PoiSearch.Query#setPageNum 方法详细说明](https://a.amap.com/lbs/static/unzip/Android_Map_Doc/Search/com/amap/api/services/poisearch/PoiSearch.Query.html#setPageNum-int-) 标注，自 5.2.1 起页码已改为从 1 开始，和 iOS 一致；页面摘要仍有旧的 0 基描述，应以这条版本说明为准。因此这里不是将公开 1 基输入合法转换为厂商 0 基输入。

独立复现提取、编译并执行原包完整 `searchPOI` / `reGeocode` AsyncFunction 回调体，仅以厂商替身记录输入，不发服务请求。页码 1、2 被写为 0、1，false 被写为 all。修正两处赋值后为 1、2 和 base。替身不模拟厂商页码钳制，因此输出明确记录“setter 输入”，不是在线搜索结果。

预期只需落实已经公开的两个输入；不新增搜索操作、默认定位或其他协议。相同减一逻辑也存在于周边/多边形查询，可由维护者一并核对。

已检索本仓 issues/PRs；#40/#41 是 iOS Double/Int 桥接问题，与此 Android 输入映射不同。

Reproduction: [standalone source and fixtures](https://github.com/qq382724935/react-native-sdk-regression-repros/tree/main/ble-and-gaode).

```sh
python3 run.py gaode-search-options
```

Actual before output:
```text
requested pages=[1, 2]; captured pageNum assignments=[0, 1]
requireExtension=false; dispatched extensions=all
```

Actual fix output:
```text
requested pages=[1, 2]; captured pageNum assignments=[1, 2]
requireExtension=false; dispatched extensions=base
```


Environment: macOS 27.0.1; Node 22.23.3, Python 3.9.6, JDK 17 / Kotlin CLI for Android-method cases, Swift 6.4 / Foundation for iOS-method cases. Consumer React Native version: 0.88.0. No full-app or physical-device reproduction is claimed. Prepared with AI assistance; the published methods and before/fix commands were checked locally.
