# [12.6.0][Android] scan() never invokes its callback when Bluetooth is disabled

The published Android `BleManager.scan` returns immediately when `getBluetoothAdapter().isEnabled()` is false, without invoking its callback. The JavaScript `scan()` Promise is settled only by that callback, so this path leaves the caller pending rather than reporting that scanning could not start.

The standalone reproduction extracts and compiles the actual Java method from the integrity-verified npm 12.6.0 package. It supplies an existing, disabled adapter and an initialized scan manager. No hardware is required. The unmodified method invokes zero callbacks; adding an error callback invokes it once and still does not start a native scan.

Expected: the disabled-adapter path should return a failure through its existing callback/Promise interface. This report is limited to this executed path; it makes no claim about native stop failures or new event fields.

Related records checked: #109 concerns disabling Bluetooth during an ongoing scan; #1329 requests started-state visibility. Neither describes this pending callback path.

Reproduction: [standalone source and fixtures](https://github.com/qq382724935/react-native-sdk-regression-repros/tree/main/ble-and-gaode).

```sh
python3 run.py ble-disabled-scan
```

Actual before output:
```text
disabled adapter: callbackCount=0, nativeScanCount=0
```

Actual fix output:
```text
disabled adapter: callbackCount=1, nativeScanCount=0
callback error=Bluetooth is not enabled
```


Environment: macOS 27.0.1; Node 22.23.3, Python 3.9.6, JDK 17 / Kotlin CLI for Android-method cases, Swift 6.4 / Foundation for iOS-method cases. Consumer React Native version: 0.88.0. No full-app or physical-device reproduction is claimed. Prepared with AI assistance; the published methods and before/fix commands were checked locally.
