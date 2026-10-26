# Expo AudioStream issues

Tested package: `expo-audio@58.0.10`.

## Setup

Run in this directory:

```sh
mkdir -p sdk
npm pack expo-audio@58.0.10 --ignore-scripts --pack-destination sdk
tar -xzf sdk/expo-audio-58.0.10.tgz -C sdk
```

## iOS source

Requires macOS, Xcode Command Line Tools and Python 3. The runner uses AVFoundation buffers/conversion and fixtures for the engine and events.

```sh
python3 run-ios.py --sdk sdk/package
```

| Case | Expected | Actual |
|---|---|---|
| `startup-cleanup` | Clean up after engine start fails | Tap stays installed |
| `stereo-layout` | Stereo samples `[1, 3, 2, 4]` | First-channel bytes `[1, 2, 99, 99]` |
| `converter-failure` | Reject unavailable conversion or report actual format | Float32 emitted for an Int16 request |

Use `--case CASE` to run one case. The published package exits 1. Source and result logs are in `ios/` and `evidence/`.

## Android source

Requires JDK 17+ and Python 3.

```sh
python3 android/run.py --package-dir sdk/package --download-tools
```

The four cases cover release after a stop error, a dead recorder, status snapshots and old buffers after restart. See [Android code and commands](android/README.md).
