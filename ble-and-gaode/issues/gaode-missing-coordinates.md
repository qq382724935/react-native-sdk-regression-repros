# [2.3.2][iOS] POI 没有原生 location 时被序列化为 (0,0)

iOS `SearchDelegate.convertPOI` 对 `poi.location` 缺失分别使用 latitude/longitude 的 `?? 0`，使没有坐标的原生对象变成一个实际地理位置 (0,0)。

独立复现编译执行 npm 2.3.2 中完整的实际 convertPOI 方法，使用 location=nil 的受控 AMapPOI 对象。原方法生成 location={latitude:0,longitude:0}。同一方法保留真实坐标、缺失位置明确缺省后，不再生成假坐标；真实的 (0,0) 仍完整保留。

当前 TypeScript POI.location 是必填，建议维护者同步选择明确的不可用表示与结果类型，而不要用有效地理点代表未知。本报告不要求改变空字符串/数组默认约定，也不报告 heading 缺值，因为当前 heading 类型必填且缺少合法公开路径的证据。

这是实际序列化方法对可空原生对象的边界复现，并未宣称在线服务必然返回该样本。检索本仓 issues/PRs 未发现相同坐标转换记录。

Reproduction: [standalone source and fixtures](https://github.com/qq382724935/react-native-sdk-regression-repros/tree/main/ble-and-gaode).

```sh
python3 run.py gaode-missing-coordinates
```

Actual before output:
```text
missing native coordinate -> [0.0, 0.0]
real native (0, 0) remains (0, 0)
```

Actual fix output:
```text
missing native coordinate -> absent
real native (0, 0) remains (0, 0)
```


Environment: macOS 27.0.1; Node 22.23.3, Python 3.9.6, JDK 17 / Kotlin CLI for Android-method cases, Swift 6.4 / Foundation for iOS-method cases. Consumer React Native version: 0.88.0. No full-app or physical-device reproduction is claimed. Prepared with AI assistance; the published methods and before/fix commands were checked locally.
