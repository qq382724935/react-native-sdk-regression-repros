# expo-audio Android AudioStream lifecycle reproduction

This standalone JVM reproduction compiles the **complete, unchanged** published `AudioStream.kt` and `AudioStreamFileWriter.kt`. It runs their real Kotlin coroutines against small controlled Android/Expo boundaries. It does not copy or reimplement AudioStream's algorithms and does not modify an application or depend on its tests.

Tested release: `expo-audio@58.0.10` on 2026-10-26. Its `AudioStream.kt` SHA-256 is `98700a145f31e2348d388a6e987ccc3b66e7555ad7be7687a405028fc643f252`. The owning investigation also compared this file with Expo main at `836012e66b147d3cf7410e23629902473c45b902` and found it identical.

## Run

Requirements: Python 3, JDK 17 or later, and npm to obtain the release. Kotlin CLI installation and Android SDK/device are not required.

```sh
mkdir -p sdk
npm pack expo-audio@58.0.10 --ignore-scripts --pack-destination sdk
tar -xzf sdk/expo-audio-58.0.10.tgz -C sdk
python3 run.py --package-dir sdk/package --label upstream --download-tools
```

`--download-tools` downloads missing fixed Maven artifacts and verifies their SHA-256 values in `toolchain.json`. Verified existing Gradle-cache artifacts can be used without downloads. The compiler is Kotlin 2.1.20; the runtime uses kotlinx-coroutines 1.10.2. No `CI` or other environment bypass is used.

The release should exit **1**, reporting these four failed expectations:

```text
stop_exception: releaseCount=0, stopCount=1, isStreaming=false
dead_object: reads=10, isStreaming=true, releaseCount=0, statuses=[true]
status_snapshot: statuses=[false, false]
stale_buffer: oldFramesDeliveredAfterRestart=1, statuses=[true, true, true]
SUMMARY failures=4
```

Use `--case stop_exception`, `--case dead_object`, `--case status_snapshot`, or `--case stale_buffer` to isolate a scenario. No assertion is inverted to make the broken baseline pass.

To compare a patched package, provide its directory with another label:

```sh
python3 run.py --package-dir /path/to/patched/expo-audio --label patched
```

The checked local candidate passed the unchanged scenarios: release count 1; one dead-object read followed by inactive state and release; `[true, false]` status snapshots; zero stale frames. Both baseline and candidate were run three additional times on real IO threads, with the same four failures/four passes each time. See `evidence/` for logs and source hashes. These results cover these scenarios only, not the candidate's other changes.

## Controlled boundaries and limits

- `AudioStream.kt` and `AudioStreamFileWriter.kt` are copied byte-for-byte; the runner records hashes. Four DTO declarations and three exception declarations are extracted unchanged from the package. Expo record annotations/interfaces are compile-time doubles.
- `AudioRecord` is a hardware double. It supplies an initialized 16 kHz mono PCM16 recorder; it can throw the documented `IllegalStateException` from `stop()`, return `ERROR_DEAD_OBJECT` from `read()`, or return one valid four-byte frame. The test does not synthesize real microphone or OS failures.
- The SDK's `CoroutineScope(Dispatchers.IO)`, capture loop, `launch`, cancellation, `ByteBuffer` work, and lifecycle methods execute unchanged. A two-millisecond delay inside the hardware double only bounds allocation rate in the broken retry loop.
- Expo `AppContext.mainQueue` is represented by a real coroutine dispatcher whose queued tasks are explicitly drained. This makes a busy-main-thread ordering deterministic. `SharedObject.emit` records payloads instead of crossing JSI; `NativeArrayBuffer` holds the real Java buffer instead of entering JNI.
- The candidate-only Media3 resampler double throws if exercised. Requested and reported sample rates match, so resampling, Android interruption callbacks, and file recording are outside these cases.
- This is **source-level fault injection on a JVM**, not an Android device/Expo Go/native-build acceptance test. It establishes the SDK response to the supplied boundary outcomes. It does not establish the frequency of those outcomes on devices, prove a hardware read/release race, or cover read/append exceptions.

## Issue grouping

Three independent reports are appropriate:

1. `stop()` exception permanently skips recorder release (`stop_exception`).
2. `ERROR_DEAD_OBJECT` is retried on the invalid recorder while `isStreaming` remains true (`dead_object`). Android explicitly says the object must be recreated: [AudioRecord reference](https://developer.android.com/reference/android/media/AudioRecord#ERROR_DEAD_OBJECT).
3. Queued events lack operation snapshots/session invalidation (`status_snapshot` and `stale_buffer`).

Searches of Expo issues/PRs on 2026-10-26 found no matching AudioStream lifecycle reports. The existing [#50310](https://github.com/expo/expo/issues/50310) / [#50327](https://github.com/expo/expo/pull/50327) concern short-read buffer capacity and are separate; the tested 58.0.10 source already contains that fix. One broader `"dead object"` issue query timed out; the exact `"AudioStream" "ERROR_DEAD_OBJECT"` issue query and the corresponding PR query returned no matches. This is bounded search evidence, not a guarantee that no duplicate exists.
