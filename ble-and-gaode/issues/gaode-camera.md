# [2.3.2][Android] moveCamera 忽略仅 zoom 的输入，更新 target 又重置未提供字段

公开 `CameraUpdate.target/zoom/tilt/bearing` 都是可选字段，但 Android CameraManager.moveCamera 仅在 target 存在时更新相机；并用全新 Builder 构建 target 更新，从而重置没有提供的视野字段。

独立复现编译执行实际发行方法，AMap 为受控边界。初始 zoom/tilt/bearing=12/20/30：只传 `{zoom:16}` 后仍为 12；随后只传 target，三个视野字段变为 0/0/0。

建议从当前相机建立 Builder，仅更新实际提供的字段。同一复现得到 zoom=16，随后仍保留 16/20/30。复现中的最小修正保留原 Handler 调度；本报告不要求动画完成回执或改变 Promise 完成时机。

未执行真机地图或完整 Expo 宿主；这里证明的是公开可选输入与实际相机方法的不一致。检索本仓现有记录，#3 是相机事件能力请求，未发现相同部分输入问题。

Reproduction: [standalone source and fixtures](https://github.com/qq382724935/react-native-sdk-regression-repros/tree/main/ble-and-gaode).

```sh
python3 run.py gaode-camera
```

Actual before output:
```text
zoom-only: zoom=12.0
target-only: zoom=0.0, tilt=0.0, bearing=0.0
```

Actual fix output:
```text
zoom-only: zoom=16.0
target-only: zoom=16.0, tilt=20.0, bearing=30.0
```


Environment: macOS 27.0.1; Node 22.23.3, Python 3.9.6, JDK 17 / Kotlin CLI for Android-method cases, Swift 6.4 / Foundation for iOS-method cases. Consumer React Native version: 0.88.0. No full-app or physical-device reproduction is claimed. Prepared with AI assistance; the published methods and before/fix commands were checked locally.
