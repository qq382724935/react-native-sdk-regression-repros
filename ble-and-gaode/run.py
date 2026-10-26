from pathlib import Path
import difflib, hashlib, json, os, re, shutil, subprocess, sys, tarfile
from prepare import ROOT, CACHE, prepare

CASES = ['ble-disabled-scan', 'ble-ios-timer', 'ble-null-record', 'gaode-search-options', 'gaode-camera', 'gaode-circle-color', 'gaode-missing-coordinates', 'gaode-search-initialization', 'gaode-single-location-cleanup']

def block(text, signature):
    if text.count(signature) != 1:
        raise RuntimeError('Missing or ambiguous source marker: ' + signature)
    start = text.index(signature)
    brace = text.index('{', start)
    # Mask strings/comments while preserving offsets; source is never rewritten.
    mask = re.sub(r'//[^\n]*|/\*[\s\S]*?\*/|"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'', lambda m: ' ' * len(m.group()), text)
    depth = 0
    for end in range(brace, len(mask)):
        if mask[end] == '{': depth += 1
        elif mask[end] == '}':
            depth -= 1
            if depth == 0: return text[start:end + 1]
    raise RuntimeError('Unclosed source marker: ' + signature)

def source(package, relative):
    file = CACHE / package / 'package' / relative
    with tarfile.open(CACHE / (package + '.tgz')) as archive:
        expected = archive.extractfile('package/' + relative).read()
    if file.read_bytes() != expected:
        raise RuntimeError('Extracted source differs from verified tarball: ' + relative)
    return expected.decode()

def replace_once(text, old, new):
    if text.count(old) != 1: raise RuntimeError('Fix anchor no longer matches: ' + old[:60])
    return text.replace(old, new)

def units(case):
    gaode = 'expo-gaode-map-2.3.2'; ble = 'react-native-ble-manager-12.6.0'
    android = 'android/src/main/java/expo/modules/gaodemap/'
    if case == 'ble-disabled-scan':
        raw = block(source(ble, 'android/src/main/java/it/innove/BleManager.java'), 'public void scan(ReadableMap scanningOptions,')
        fixed = replace_once(raw, 'if (!getBluetoothAdapter().isEnabled()) {\n            return;', 'if (!getBluetoothAdapter().isEnabled()) {\n            callback.invoke("Bluetooth is not enabled");\n            return;')
        return 'java', {'SOURCE': (raw, fixed)}
    if case == 'ble-null-record':
        raw = block(source(ble, 'android/src/main/java/it/innove/DefaultPeripheral.java'), 'public DefaultPeripheral(BleManager bleManager, ScanResult result)')
        fixed = replace_once(raw, 'Objects.requireNonNull(result.getScanRecord()).getBytes()', 'result.getScanRecord() != null ? result.getScanRecord().getBytes() : null')
        return 'java', {'SOURCE': (raw, fixed)}
    if case == 'ble-ios-timer':
        swift = source(ble, 'ios/SwiftBleManager.swift')
        scan = block(swift, '@objc public func scan(')
        timer = '''            if let scanTimer = scanTimer {
                scanTimer.invalidate()
                self.scanTimer = nil
            }
'''
        fixed = replace_once(scan, timer, '')
        fixed = replace_once(fixed, '        let timeoutSeconds =', '        scanTimer?.invalidate()\n        scanTimer = nil\n        let timeoutSeconds =')
        stop = block(swift, '@objc func stopTimer()')
        return 'swift', {'SOURCE': (scan + '\n' + stop, fixed + '\n' + stop)}
    if case == 'gaode-search-options':
        text = source(gaode, android + 'search/ExpoGaodeMapSearchModule.kt')
        raw = block(text, 'AsyncFunction("searchPOI")') + '\n' + block(text, 'AsyncFunction("reGeocode")')
        fixed = replace_once(raw, 'query.pageNum = pageNum - 1 // 高德 SDK 从 0 开始', 'query.pageNum = pageNum')
        fixed = replace_once(fixed, 'query.extensions = "all"', 'query.extensions = if (options["requireExtension"] as? Boolean != false) "all" else "base"')
        return 'kotlin', {'SOURCE': (raw, fixed)}
    if case == 'gaode-camera':
        raw = block(source(gaode, android + 'managers/CameraManager.kt'), 'fun moveCamera(position:')
        fixed = (ROOT / 'fixes/camera-method.kt').read_text().strip()
        return 'kotlin', {'SOURCE': (raw, fixed)}
    if case == 'gaode-circle-color':
        android_module = source(gaode, android + 'overlays/CircleViewModule.kt')
        ios_module = source(gaode, 'ios/overlays/CircleViewModule.swift')
        assert 'Prop<String?>("fillColor")' in android_module and 'Prop<String?>("strokeColor")' in android_module
        assert ios_module.count('color: String?') >= 2
        assert 'export type ColorValue = string | number;' in source(gaode, 'build/types/common.types.d.ts')
        raw = source(gaode, 'build/components/overlays/Circle.js')
        # Only the imports/default export are bound by the tiny renderer fixture.
        raw = re.sub(r'^import .*;\n', '', raw, flags=re.M)
        raw = raw.replace('export default React.memo(Circle);', 'const RenderCircle = React.memo(Circle);')
        raw = re.sub(r'\n//# sourceMappingURL=.*', '', raw)
        fixed = replace_once(raw, '    const normalizedCenter = normalizeLatLng(center);', '''    const normalizedCenter = normalizeLatLng(center);
    for (const key of ['fillColor', 'strokeColor']) {
        const color = restProps[key];
        if (typeof color === 'number' && Number.isInteger(color) && color >= -0x80000000 && color <= 0xffffffff) {
            restProps[key] = `#${(color >>> 0).toString(16).padStart(8, '0').toUpperCase()}`;
        }
    }''')
        return 'js', {'SOURCE': (raw, fixed)}
    if case == 'gaode-missing-coordinates':
        raw = block(source(gaode, 'ios/ExpoGaodeMapSearchModule.swift'), 'private func convertPOI(')
        old = '''        "location": [
          "latitude": poi.location?.latitude ?? 0,
          "longitude": poi.location?.longitude ?? 0
        ],
'''
        fixed = replace_once(raw, old, '')
        fixed = replace_once(fixed, '      return result', '''      if let coordinate = poi.location {
          result["location"] = ["latitude": coordinate.latitude, "longitude": coordinate.longitude]
      }
      return result''')
        return 'swift', {'SOURCE': (raw, fixed)}
    if case == 'gaode-search-initialization':
        init = source(gaode, android + 'modules/SDKInitializer.kt')
        search = source(gaode, android + 'search/ExpoGaodeMapSearchModule.kt')
        setup = block(init, 'fun applyPrivacyState(') + '\n' + block(init, 'fun initSDK(')
        setup = setup.replace('android.util.Log', 'Log').replace('expo.modules.kotlin.exception.CodedException', 'CodedException')
        fixed_setup = setup
        fixed_setup = replace_once(fixed_setup, '            AMapLocationClient.setApiKey(androidKey)', '            AMapLocationClient.setApiKey(androidKey)\n            configuredKey = androidKey')
        guard = block(search, 'private fun ensureAPIKeyIsSet(').replace('android.content.pm.PackageManager', 'PackageManager')
        fixed_guard = replace_once(guard, 'val apiKey = try {', 'val apiKey = SDKInitializer.configuredKey ?: try {')
        return 'kotlin', {'SETUP': (setup, fixed_setup), 'GUARD': (guard, fixed_guard)}
    if case == 'gaode-single-location-cleanup':
        raw = block(source(gaode, android + 'modules/LocationManager.kt'), 'fun getCurrentLocation(')
        fixed = (ROOT / 'fixes/single-location-method.kt').read_text().strip()
        return 'kotlin', {'SOURCE': (raw, fixed)}
    raise RuntimeError(case)

def execute(language, text, folder):
    extension = {'java': 'java', 'swift': 'swift', 'kotlin': 'kt', 'js': 'cjs'}[language]
    file = folder / ('Main.' + extension); file.write_text(text)
    if language == 'java':
        subprocess.run(['javac', 'Main.java'], cwd=folder, check=True, capture_output=True, text=True)
        command = ['java', '-ea', 'Main']
    elif language == 'swift':
        subprocess.run(['xcrun', 'swiftc', '-swift-version', '5', '-module-cache-path', '.swift-cache', 'Main.swift', '-o', 'probe'], cwd=folder, check=True, capture_output=True, text=True)
        command = ['./probe']
    elif language == 'kotlin':
        # Optional local compiler descriptor; never copied into the public bundle.
        if os.environ.get('KOTLIN_ENV'):
            env = json.loads(Path(os.environ['KOTLIN_ENV']).read_text())
            subprocess.run([env['java'], '-cp', env['compilerClasspath'], env['compilerMain'], '-no-stdlib', '-no-reflect', '-classpath', env['compileClasspath'], '-jvm-target', '17', '-d', '.', 'Main.kt'], cwd=folder, check=True, capture_output=True, text=True)
            command = [env['java'], '-cp', '.' + os.pathsep + env['runtimeClasspath'], 'MainKt']
        else:
            subprocess.run([os.environ.get('KOTLINC', 'kotlinc'), 'Main.kt', '-jvm-target', '17', '-include-runtime', '-d', 'probe.jar'], cwd=folder, check=True, capture_output=True, text=True)
            command = ['java', '-jar', 'probe.jar']
    else: command = ['node', 'Main.cjs']
    result = subprocess.run(command, cwd=folder, check=True, capture_output=True, text=True)
    return result.stdout.strip()

def run(case, mode):
    language, parts = units(case)
    fixture = (ROOT / 'fixtures' / (case + '.txt')).read_text()
    changes = []
    for key, (before, fixed) in parts.items():
        fixture = fixture.replace('// ' + key, before if mode == 'before' else fixed)
        changes.extend(difflib.unified_diff((before.rstrip() + '\n').splitlines(True), (fixed.rstrip() + '\n').splitlines(True), 'upstream/' + key, 'fixed/' + key))
    fixture = fixture.replace('FIXED_MODE', 'true' if mode == 'fix' else 'false')
    folder = ROOT / '.work' / case / mode; folder.mkdir(parents=True, exist_ok=True)
    output = execute(language, fixture, folder)
    (folder / 'output.txt').write_text(output + '\n')
    (ROOT / 'fixes' / (case + '.diff')).write_text(''.join(changes))
    print('[' + case + ' / ' + mode + ']\n' + output)
    return output

if __name__ == '__main__':
    if len(sys.argv) < 2 or sys.argv[1] not in CASES + ['all']:
        raise SystemExit('Usage: python3 run.py {' + '|'.join(CASES) + '|all} [before|fix]')
    prepare()
    cases = CASES if sys.argv[1] == 'all' else [sys.argv[1]]
    modes = [sys.argv[2]] if len(sys.argv) > 2 else ['before', 'fix']
    if any(mode not in ['before', 'fix'] for mode in modes):
        raise SystemExit('Mode must be before or fix')
    outputs = {}
    try:
        for case in cases:
            outputs[case] = {mode: run(case, mode) for mode in modes}
    except subprocess.CalledProcessError as error:
        print(error.stdout or '', error.stderr or '', file=sys.stderr)
        raise SystemExit(error.returncode)
    (ROOT / '.work' / 'latest-results.json').write_text(json.dumps(outputs, indent=2) + '\n')
