# Scope and evidence review

- Eight new-issue candidates remain. The null ScanRecord case is recorded under existing BLE PR #340; no new issue or comment is requested.
- BLE disabled scan is limited to the executed callback omission. Stop errors, receiver lifecycle and additional scanStopped events are not bundled into this issue.
- The iOS timer case is supported by the published ScanOptions.seconds contract: zero scans until stopScan. It runs actual Swift methods and a real Foundation Timer, with a synthetic central manager.
- CameraUpdate marks target/zoom/tilt/bearing optional. The reproduction and minimal fix retain Handler scheduling and do not impose a different Promise/animation-completion contract.
- ColorValue explicitly documents packed numeric ARGB for Android. The report is Android-specific; it does not assert that iOS numeric colors are promised.
- Missing POI location alone remains in the serialization report. Empty string/list defaults are deliberately excluded. Coordinates.heading is mandatory and both native serializers normally emit it; injecting a missing heading into an internal normalizer alone does not establish a legal public-call defect, so heading is also excluded.
- Runtime key support is explicitly documented in shipped build/search/index.js and the upstream README. The report does not infer broken privacy propagation from isolated vendor doubles; vendor-internal sharing has not been established.
- The location cleanup report concerns an allocated client after configuration failure. It preserves the current signature and does not claim Expo cannot reject an escaping exception.
- Per-call address input, keyword center/sort forwarding, custom user-drag events, resource receipt fields and global font policy are not submitted as new defects here.
- These checks are source/method/bridge-boundary evidence. No device or online vendor-service claim is made. AMap query doubles capture assigned parameters and do not simulate vendor clamping.

Existing related records checked: BLE #109, #1329, #1388, #1392 / PR #1393, PR #340; Gaode #3, #5, #12, #17, #28, #34 / PR #69, #40 / #41, #44. They differ in the ways described in each selected draft, except PR #340, which is treated as the existing matching record.
