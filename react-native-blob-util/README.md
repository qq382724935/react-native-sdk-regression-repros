# iOS multipart: failed read becomes a successful empty file part

This reproduction executes the unchanged `buildFormBody:boundary:onComplete:` method extracted from `react-native-blob-util@0.25.1`. It replaces only `ReactNativeBlobUtilFS` with a controlled callback and suppresses diagnostics.

Requirements: macOS, Xcode Command Line Tools (`clang++` and Foundation), Python 3.

## Obtain the official package

Run these commands in this reproduction's directory:

```sh
curl --fail --location https://registry.npmjs.org/react-native-blob-util/-/react-native-blob-util-0.25.1.tgz --output react-native-blob-util-0.25.1.tgz
python3 - <<'PY'
import base64
import hashlib
from pathlib import Path

expected = 'HMzab2SL8h48pvfufji0TKdet/jnNvamxYmYyNqTV5YOge00V28ycdc3S4leHjGXMJ1+fS2j2SrQ3aG5pzbx1w=='
actual = base64.b64encode(hashlib.sha512(Path('react-native-blob-util-0.25.1.tgz').read_bytes()).digest()).decode()
assert actual == expected, 'Official npm dist.integrity mismatch'
print('Official npm dist.integrity verified')
PY
tar -xzf react-native-blob-util-0.25.1.tgz
```

The pinned digest is the SHA-512 portion of the official [0.25.1 registry metadata](https://registry.npmjs.org/react-native-blob-util/0.25.1).

## Run the unmodified source

```sh
python3 reproduce-ios-multipart.py --sdk ./package
```

Expected exit status: **1**. The nil-content case incorrectly succeeds; the other three controls pass:

```text
nil-content: FAIL (callbacks=1, error=false, expected_error=true)
explicit-error: PASS (callbacks=1, error=true, expected_error=true)
empty-file: PASS (callbacks=1, error=false, expected_error=false)
nonempty-file: PASS (callbacks=1, error=false, expected_error=false)
4 cases; 1 failure(s)
```

The actual 0.25.1 `ReactNativeBlobUtilFS.mm` can supply `(nil, nil, nil)`: after checking that a path exists, it calls `NSData dataWithContentsOfFile:` without checking the resulting data, then invokes the callback with nil error for `encoding:nil`. A read failure after the existence check can therefore reach the builder as nil content. The fixture supplies that nil callback result.

## Check the minimal correction

Apply `fix-ios-multipart-nil.patch` to the disposable extracted package, then run the same script:

```sh
git -C package apply --check ../fix-ios-multipart-nil.patch
git -C package apply ../fix-ios-multipart-nil.patch
python3 reproduce-ios-multipart.py --sdk ./package
```

Expected exit status: **0**, with all four cases passing. The correction rejects nil content without rejecting a legitimate zero-byte `NSData` result. The script prints hashes of the supplied source and extracted method so each result can be tied to the bytes actually compiled.
