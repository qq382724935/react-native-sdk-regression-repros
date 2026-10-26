# [iOS] Previous scan timeout stops a new unlimited scan

### Minimal reproducible example

[Reproduction code](https://github.com/qq382724935/react-native-sdk-regression-repros/tree/main/ble-and-gaode) — react-native-ble-manager 12.6.0, iOS.

### Steps to reproduce

1. Start a scan with a timeout.
2. Before it expires, start another scan with `seconds: 0`.
3. Let the first timeout fire.

Run: `python3 run.py ble-ios-timer`.

**Expected:** The new scan continues until `stopScan()` is called.

**Actual:** The previous timer stops the new scan.

### Relevant code

```swift
if timeoutSeconds > 0 {
    scanTimer?.invalidate()
    // Create the new timer.
}
```

Invalidate the previous timer before checking the new timeout, including when it is zero.
