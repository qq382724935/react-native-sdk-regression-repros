from pathlib import Path
import base64, hashlib, json, tarfile, urllib.request
ROOT = Path(__file__).resolve().parent
CACHE = ROOT / '.cache'
def prepare():
    CACHE.mkdir(exist_ok=True)
    for spec in json.loads((ROOT / 'packages.json').read_text()):
        key = spec['name'] + '-' + spec['version']
        archive = CACHE / (key + '.tgz')
        if not archive.exists():
            with urllib.request.urlopen(spec['url'], timeout=60) as response:
                archive.write_bytes(response.read())
        algorithm, expected = spec['integrity'].split('-', 1)
        actual = base64.b64encode(hashlib.new(algorithm, archive.read_bytes()).digest()).decode()
        if actual != expected:
            raise RuntimeError('Integrity mismatch: ' + key)
        target = CACHE / key
        target.mkdir(exist_ok=True)
        if not (target / 'package/package.json').exists():
            with tarfile.open(archive) as archive_file:
                for member in archive_file.getmembers():
                    if not (member.isfile() or member.isdir()) or not (target / member.name).resolve().is_relative_to(target.resolve()):
                        raise RuntimeError('Unsafe archive member: ' + member.name)
                archive_file.extractall(target)
        print(key + ': verified official npm integrity')
if __name__ == '__main__':
    prepare()
