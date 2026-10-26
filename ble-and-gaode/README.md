# Standalone SDK regressions (published npm snapshots)

This bundle checks `expo-gaode-map@2.3.2` and `react-native-ble-manager@12.6.0`. It downloads only their official npm archives and verifies `dist.integrity` before extracting source. Each selected source file is checked byte-for-byte against that verified archive. No application, backend, credentials, device data, or private configuration is required.

The before runs execute actual published Java/Swift/Kotlin methods, Expo registration bodies, or the shipped Circle JavaScript component. Fixtures replace only the unavailable Android, CoreBluetooth, AMap, Expo and React/native-view boundaries. The iOS timer case uses the real Foundation Timer and manually fires the earlier timer; there is no timing race or Bluetooth hardware in that check. Suggested fixes are intentionally limited to the demonstrated defect. Method diffs in `fixes/` are evidence, not ready-to-apply repository patches.

Requirements: Python 3.9+, Node 18+, JDK 17, Kotlin 2.2.x CLI (`kotlinc` on PATH, or set KOTLINC), and Xcode Command Line Tools for Swift cases. Linux can run the Java/Kotlin/JavaScript cases individually. Tests do not access AMap/Bluetooth/network services; only `prepare.py` may download npm archives.

```sh
python3 prepare.py
python3 run.py all
```

Every command checks both before and fix outputs and exits nonzero on an unexpected result. Use `python3 run.py CASE before` or `python3 run.py CASE fix` to run one variant. Generated SDK downloads and compiler outputs stay in ignored `.cache/` and `.work/` directories.

| Case command | Actual implementation exercised | Observed before → fix |
|---|---|---|
| `python3 run.py ble-disabled-scan` | Android BleManager.scan | disabled adapter: callback count 0 → 1 (error); native scan count stays 0 |
| `python3 run.py ble-ios-timer` | SwiftBleManager.scan/stopTimer + Foundation Timer | finite→unlimited: earlier timer valid/stopCalls=1 → invalid/stopCalls=0 |
| `python3 run.py ble-null-record` | Android DefaultPeripheral constructor | null record: NPE true → false; device/RSSI retained |
| `python3 run.py gaode-search-options` | full Android searchPOI/reGeocode AsyncFunction bodies | page setter inputs 0/1 → 1/2; false extensions all → base |
| `python3 run.py gaode-camera` | Android CameraManager.moveCamera | zoom-only ignored → applied; target-only 0/0/0 → omitted fields preserved |
| `python3 run.py gaode-circle-color` | shipped Circle JS and native prop declarations | documented Android packed ARGB numbers remain numbers → matching strings |
| `python3 run.py gaode-missing-coordinates` | iOS SearchDelegate.convertPOI | missing location becomes (0,0) → absent; actual (0,0) retained |
| `python3 run.py gaode-search-initialization` | Android initSDK and search ensureAPIKeyIsSet | runtime key accepted=false → true without Manifest key |
| `python3 run.py gaode-single-location-cleanup` | Android getCurrentLocation | configuration throw leaves stop/destroy 0/0 → 1/1 |

`expected-results.json` contains the actual captured before/fix stdout. This is method/bridge-boundary evidence. It does not establish device behavior, AMap service responses, platform rendering, full native builds, or Expo Promise timing. The search fixture records pageNum setter inputs without emulating vendor clamping or invoking a service.

`ble-null-record` is retained only as evidence for existing [PR #340](https://github.com/innoveit/react-native-ble-manager/pull/340); no new issue/comment is proposed for it. The publish manifest identifies eight new-issue drafts and this existing-record entry.

The public reports deliberately exclude empty-string/array defaults, unavailable heading representation, unverified vendor-internal privacy propagation, added API/event capabilities, and asynchronous camera completion policy. The camera fix retains the original Handler scheduling. The location cleanup fix keeps the existing public signature.

The source remains governed by its upstream license; copies are in `licenses/`. Public upload files are enumerated in `publish-files.txt`; do not upload `.cache/`, `.work/`, or local compiler descriptors.
