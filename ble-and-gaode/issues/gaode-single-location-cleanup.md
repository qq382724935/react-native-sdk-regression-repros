# [2.3.2][Android] 单次定位配置异常后，已创建 client 没有停止与销毁

`LocationManager.getCurrentLocation` 创建独立 AMapLocationClient 后依次配置、注册监听和启动；清理只在结果回调中执行。配置或启动在回调之前抛错时，已创建 client 没有走 stopLocation/onDestroy。

独立复现提取并执行实际 Kotlin 方法，以受控厂商 client 在 setLocationOption 抛出合成异常。原版已创建对象的 stopCount/destroyCount 都是 0。局部修正让终态与清理共用仅执行一次的入口，相同反例为 1/1。修正保持既有 `getCurrentLocation(promise)` 签名，不添加 includeAddress 或其他能力。

Expo 桥可能拒绝逃逸异常；本报告不声称 JS 一定收不到错误。这里验证的是已创建资源的清理缺口。未执行真实设备定位。

#34 / PR #69 针对 iOS 单次定位；本例是 Android 在配置阶段抛错后的资源收尾。

Reproduction: [standalone source and fixtures](https://github.com/qq382724935/react-native-sdk-regression-repros/tree/main/ble-and-gaode).

```sh
python3 run.py gaode-single-location-cleanup
```

Actual before output:
```text
configuration exception escaped=true, rejectionCount=0, stopCount=0, destroyCount=0
```

Actual fix output:
```text
configuration exception escaped=false, rejectionCount=1, stopCount=1, destroyCount=1
```


Environment: macOS 27.0.1; Node 22.23.3, Python 3.9.6, JDK 17 / Kotlin CLI for Android-method cases, Swift 6.4 / Foundation for iOS-method cases. Consumer React Native version: 0.88.0. No full-app or physical-device reproduction is claimed. Prepared with AI assistance; the published methods and before/fix commands were checked locally.
