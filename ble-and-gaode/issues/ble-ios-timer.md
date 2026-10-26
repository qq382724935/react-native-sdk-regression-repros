# [12.6.0][iOS] A previous finite scan timer stops a replacement unlimited scan

`ScanOptions.seconds` explicitly documents that zero scans until `stopScan()` is called. In npm 12.6.0, `SwiftBleManager.scan` invalidates the previous timer only inside `if timeoutSeconds > 0`. Replacing a finite scan with `seconds: 0` therefore retains the previous timer.

The reproduction compiles the actual Swift `scan` and `stopTimer` methods. CoreBluetooth is a controlled boundary; Foundation Timer is real. It starts a 60-second scan, lets the existing scheduling block run, starts an unlimited scan, and manually fires the earlier timer. Before the fix that timer is still valid and calls native stop once; after moving timer invalidation outside the duration branch it is invalid and cannot stop the replacement scan.

This is a deterministic method-boundary reproduction, not a Bluetooth device test. It does not require waiting 60 seconds.

Searched scanTimer and scan-related issues/PRs. #1388 discusses bridge-reload cleanup; it does not cover finite-to-unlimited replacement.

Reproduction: [standalone source and fixtures](https://github.com/qq382724935/react-native-sdk-regression-repros/tree/main/ble-and-gaode).

```sh
python3 run.py ble-ios-timer
```

Actual before output:
```text
finite -> unlimited: oldTimerValid=true, stopCalls=1, callbacks=2
```

Actual fix output:
```text
finite -> unlimited: oldTimerValid=false, stopCalls=0, callbacks=2
```


Environment: macOS 27.0.1; Node 22.23.3, Python 3.9.6, JDK 17 / Kotlin CLI for Android-method cases, Swift 6.4 / Foundation for iOS-method cases. Consumer React Native version: 0.88.0. No full-app or physical-device reproduction is claimed. Prepared with AI assistance; the published methods and before/fix commands were checked locally.
