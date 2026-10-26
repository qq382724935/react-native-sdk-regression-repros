# Android AudioStream issues

Package: `expo-audio@58.0.10`. The runner compiles the published AudioStream classes with Kotlin coroutines and Android/Expo fixtures.

## Run

Requires JDK 17+, Python 3 and npm. Run from this directory:

```sh
mkdir -p sdk
npm pack expo-audio@58.0.10 --ignore-scripts --pack-destination sdk
tar -xzf sdk/expo-audio-58.0.10.tgz -C sdk
python3 run.py --package-dir sdk/package --download-tools
```

`--download-tools` obtains the pinned Kotlin/coroutine dependencies and checks their hashes in `toolchain.json`.

| Case | Expected | Actual |
|---|---|---|
| `stop_exception` | Release after stop throws | releaseCount=0 |
| `dead_object` | Stop using the invalid recorder | Repeated reads, still active |
| `status_snapshot` | Start/stop events `[true, false]` | `[false, false]` |
| `stale_buffer` | Discard buffers from the previous recording | One old buffer delivered after restart |

Use `--case CASE` to select one case. The published package exits 1 with four failures. Point `--package-dir` at a corrected package to run the same assertions. Code is in `Repro.kt` and `stubs/`; captured output is in `evidence/`.
