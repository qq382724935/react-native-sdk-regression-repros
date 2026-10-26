# BLE Manager and Expo Gaode Map issues

Packages: `react-native-ble-manager@12.6.0`, `expo-gaode-map@2.3.2`.

Requires Python 3.9+, Node 18+, JDK 17, Kotlin 2.2.x (`kotlinc` on PATH or `KOTLINC`), and Xcode Command Line Tools for Swift cases.

```sh
python3 prepare.py
python3 run.py all
```

The runner extracts published SDK methods and uses fixtures for platform APIs. Each case compares the original method with a small correction. A failed assertion exits nonzero.

| Case command | Actual implementation exercised | Observed before → fix |
|---|---|---|
| `python3 run.py ble-disabled-scan` | Android BleManager.scan | disabled adapter: callback count 0 → 1 (error); native scan count stays 0 |
| `python3 run.py ble-ios-timer` | SwiftBleManager.scan/stopTimer + Foundation Timer | finite→unlimited: earlier timer valid/stopCalls=1 → invalid/stopCalls=0 |
| `python3 run.py ble-null-record` | Android DefaultPeripheral constructor | null record: NPE true → false; device/RSSI retained |
| `python3 run.py gaode-search-options` | full Android searchPOI/reGeocode AsyncFunction bodies | page setter inputs 0/1 → 1/2; false extensions all → base |
| `python3 run.py gaode-camera` | Android map-view update | zoom-only ignored → applied; target-only 0/0/0 → omitted fields preserved |
| `python3 run.py gaode-circle-color` | shipped Circle JS and native prop declarations | documented Android packed ARGB numbers remain numbers → matching strings |
| `python3 run.py gaode-missing-coordinates` | iOS SearchDelegate.convertPOI | missing location becomes (0,0) → absent; actual (0,0) retained |
| `python3 run.py gaode-search-initialization` | Android initSDK and search ensureAPIKeyIsSet | runtime key accepted=false → true without Manifest key |
| `python3 run.py gaode-single-location-cleanup` | Android getCurrentLocation | configuration throw leaves stop/destroy 0/0 → 1/1 |

Use `python3 run.py CASE before` or `python3 run.py CASE fix` for a single variant. Results are in `expected-results.json`, source fixes in `fixes/`, and issue descriptions in `issues/`.

The null ScanRecord case already has [PR #340](https://github.com/innoveit/react-native-ble-manager/pull/340). Upstream licenses are in `licenses/`.
