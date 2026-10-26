# [2.3.2][Android] 公开 initSDK 的运行时 key 未被搜索模块采用

发行包 `build/search/index.js` 的 initSearch 说明明确列出：调用 initSDK 设置 key 后，无需再次配置搜索。项目 README 也说明未使用配置插件或原生配置时，可调用 initSDK 后使用搜索能力。

Android `initSDK` 只把运行时 key 交给 MapsInitializer/AMapLocationClient，而搜索 ensureAPIKeyIsSet 又只查 Manifest，未读取同次初始化的 key。

独立复现执行实际 initSDK 和 ensureAPIKeyIsSet 方法；Manifest 替身没有 key，传给 initSDK 的是合成字符串。原版地图和定位收到 key，但搜索拒绝配置；保存并复用同次 runtime key 后，搜索接受且值一致。不访问真实服务、不使用真实凭证。

本报告只针对公开承诺的运行时 key 来源；不推断厂商内部的隐私状态是否共享，不要求新增权限或同意流程。

现有 #12/#17 讨论配置插件/Manifest，#44 询问空 key；本例使用非空运行时 key，触发入口不同。

Reproduction: [standalone source and fixtures](https://github.com/qq382724935/react-native-sdk-regression-repros/tree/main/ble-and-gaode).

```sh
python3 run.py gaode-search-initialization
```

Actual before output:
```text
runtime init key accepted by search=false; searchKeyMatches=false
```

Actual fix output:
```text
runtime init key accepted by search=true; searchKeyMatches=true
```


Environment: macOS 27.0.1; Node 22.23.3, Python 3.9.6, JDK 17 / Kotlin CLI for Android-method cases, Swift 6.4 / Foundation for iOS-method cases. Consumer React Native version: 0.88.0. No full-app or physical-device reproduction is claimed. Prepared with AI assistance; the published methods and before/fix commands were checked locally.
