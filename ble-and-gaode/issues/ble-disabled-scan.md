# [Android] scan() never settles when Bluetooth is disabled

### Minimal reproducible example

[Reproduction code](https://github.com/qq382724935/react-native-sdk-regression-repros/tree/main/ble-and-gaode) — react-native-ble-manager 12.6.0, Android.

### Steps to reproduce

1. Disable Bluetooth.
2. Call `BleManager.scan(...)`.

Run: `python3 run.py ble-disabled-scan`.

**Expected:** The scan Promise rejects with an error.

**Actual:** The method returns without invoking its callback, leaving the Promise pending.

### Relevant code

```java
if (!getBluetoothAdapter().isEnabled()) {
    return;
}
```

Invoke the existing error callback before returning.
