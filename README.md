# React Native SDK regression reproductions

Small native-method and JavaScript reproductions for upstream reports. Each directory names its tested npm release, expected result, actual result, and controlled boundaries.

- [Expo AudioStream](expo-audio/README.md): Android lifecycle/event delivery and iOS PCM/resource handling.
- [BLE Manager and Expo Gaode Map](ble-and-gaode/README.md): scan callbacks/timers and documented map/location/search inputs.
- [React Native Blob Util](react-native-blob-util/README.md): a failed iOS file read becomes a successful empty multipart field.

Run only the directory relevant to an issue. The scripts use synthetic data and compile the actual SDK methods or classes; they do not run an application or contact a business service. Host boundary checks, full native builds, and physical-device acceptance are distinct evidence.

Prepared with AI assistance. Each report states which checks actually ran and which did not.
