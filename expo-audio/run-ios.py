"""Run the actual AudioStream class with controlled session/engine/Expo boundaries."""
import argparse
import hashlib
import re
import subprocess
import sys
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument('--sdk', type=Path, required=True)
parser.add_argument('--label', default='upstream')
parser.add_argument('--case', choices=['all', 'startup-cleanup', 'stereo-layout', 'converter-failure'], default='all')
args = parser.parse_args()
if not re.fullmatch(r'[A-Za-z0-9_-]+', args.label):
    parser.error('--label must contain only letters, digits, underscores, or hyphens')
root = Path(__file__).resolve().parent
out = root / '.build' / args.label
out.mkdir(parents=True, exist_ok=True)
raw = (args.sdk / 'ios/AudioStream.swift').read_text()
print('AudioStream.swift sha256=' + hashlib.sha256(raw.encode()).hexdigest(), flush=True)
source = raw.replace('import AVFoundation\n', '').replace('import ExpoModulesCore\n', '')
assert source.count('AVAudioConverter(from:') == 1
# Only the converter construction boundary can be forced to fail. Conversion is real AVFoundation.
source = source.replace('AVAudioConverter(from:', 'makeConverter(from:')
cases = (root / 'ios/Cases.swift').read_text()
if 'func stop() {' in source:
    cases = cases.replace('try? stream.stop()', 'stream.stop()')
combined = (root / 'ios/Boundary.swift').read_text() + '\n' + source + '\n' + cases
(out / 'main.swift').write_text(combined)
subprocess.run(['swiftc', '-swift-version', '5', '-module-cache-path', str(out / 'module-cache'),
                str(out / 'main.swift'), '-o', str(out / 'ios-repro')], check=True)
scenarios = ['startup-cleanup', 'stereo-layout', 'converter-failure'] if args.case == 'all' else [args.case]
failures = 0
for scenario in scenarios:
    result = subprocess.run([str(out / 'ios-repro'), scenario], timeout=15)
    failures += result.returncode != 0
print(f'{len(scenarios)} cases; {failures} failure(s)', flush=True)
sys.exit(1 if failures else 0)
