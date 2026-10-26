# Expo AudioStream native-boundary reproductions

Version: `expo-audio@58.0.10`, checked on 2026-10-26. The Android and iOS AudioStream sources match Expo main at `836012e66b147d3cf7410e23629902473c45b902`.

These scripts execute the SDK's real native implementation with controlled operating-system and Expo boundaries. They do not need an application, credentials, a microphone, or a device. They establish the code's response to specific boundary outcomes; they do not establish how often those outcomes occur on phones.

## Obtain the release

```sh
mkdir -p sdk
npm pack expo-audio@58.0.10 --ignore-scripts --pack-destination sdk
tar -xzf sdk/expo-audio-58.0.10.tgz -C sdk
```

npm verifies the published archive integrity. Each runner also prints hashes of the source it compiles.

## iOS implementation on a macOS host

Requirements: macOS, Xcode Command Line Tools with Swift and AVFoundation, and Python 3.

```sh
python3 run-ios.py --sdk sdk/package --label upstream
```

Expected exit status on the published package: **1**, with three failures:

| Case | Expected behavior | Published behavior |
| --- | --- | --- |
| `startup-cleanup` | A rejected engine start is cleaned up by `stop()` | Tap stays installed and engine stop count is 0 |
| `stereo-layout` | Two planar input channels become `[1, 3, 2, 4]` | Output is `[1, 2, 99, 99]`, copied from only the first plane |
| `converter-failure` | Reject an unsupported requested PCM conversion | Start succeeds and emits Float32 for an Int16 request without an encoding field |

Pass `--case startup-cleanup`, `--case stereo-layout`, or `--case converter-failure` to isolate one failure. Point `--sdk` at a corrected package with `--label corrected` to run exactly the same expectations. The checked downstream package passes all three; output is recorded in `evidence/`.

`AudioStream.swift` is included unchanged except for removing module imports and replacing the AVAudioConverter construction call with a controllable factory. Format objects, buffers, conversion, and byte copies use real AVFoundation/Foundation. The engine, input-node tap, session, and Expo event bridge are controlled boundaries. The factory returns the real AVAudioConverter except in the explicit unavailable-converter case. Test calls adapt to the SDK's throwing/non-throwing stop signature.

The session-active value in the output is diagnostic only. The startup assertion concerns this stream's tap/engine; it does not prescribe when a shared audio session must be deactivated.

The stereo case allocates four frames per plane but marks only two frames valid. The sentinel values are inside the allocation, so the reproduction never needs an out-of-bounds read. It verifies the actual emitted bytes, not a mock conversion algorithm. No claim of device exploitation or hardware reproduction is made.

Suggested reports: one failed-start resource-cleanup issue, and one PCM-format issue covering planar layout and the unsupported-converter fallback.

## Android implementation on a JVM

```sh
python3 android/run.py --package-dir sdk/package --label upstream --download-tools
```

The published package exits **1** with four failed expectations. See [Android instructions and controlled boundaries](android/README.md) for individual cases, pinned tools, and results.

The earlier short-read issue [expo/expo#50310](https://github.com/expo/expo/issues/50310) is already fixed in this tested release. It is separate from these lifecycle and format failures.
