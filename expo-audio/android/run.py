#!/usr/bin/env python3
"""Compile an unchanged Expo AudioStream with controlled Android/Expo boundaries."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import urllib.request

ROOT = Path(__file__).resolve().parent


def declaration(text, name):
    match = re.search(rf"^(?:enum )?class {re.escape(name)}\b", text, re.M)
    if not match:
        raise ValueError(f"Missing SDK declaration: {name}")
    start = match.start()
    opening = text.index("{", start)
    depth = 1
    index = opening + 1
    while depth:
        if text[index] == "{":
            depth += 1
        elif text[index] == "}":
            depth -= 1
        index += 1
    return text[start:index]


def dependency_jars(download):
    jars = []
    for item in json.loads((ROOT / "toolchain.json").read_text()):
        relative = Path(item["group"]) / item["artifact"] / item["version"]
        candidates = list((Path.home() / ".gradle/caches/modules-2/files-2.1" / relative).glob("*/*.jar"))
        local = ROOT / ".tools" / f'{item["artifact"]}-{item["version"]}.jar'
        if local.exists():
            candidates.insert(0, local)
        jar = next((p for p in candidates if hashlib.sha256(p.read_bytes()).hexdigest() == item["sha256"]), None)
        if jar is None and download:
            local.parent.mkdir(parents=True, exist_ok=True)
            data = urllib.request.urlopen(item["url"], timeout=60).read()
            if hashlib.sha256(data).hexdigest() != item["sha256"]:
                raise ValueError(f'Checksum mismatch for {item["artifact"]}')
            local.write_bytes(data)
            jar = local
        if jar is None:
            raise SystemExit(f'Missing verified {item["artifact"]}@{item["version"]}; use --download-tools')
        jars.append(jar)
    return jars


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--package-dir", type=Path, required=True, help="Extracted expo-audio package directory")
    parser.add_argument("--label", default="run")
    parser.add_argument("--case", default="all", choices=["all", "stop_exception", "dead_object", "status_snapshot", "stale_buffer"])
    parser.add_argument("--download-tools", action="store_true", help="Download missing fixed, checksum-verified Maven jars")
    args = parser.parse_args()
    if not re.fullmatch(r"[a-zA-Z0-9_-]+", args.label):
        parser.error("--label only allows letters, numbers, underscores and hyphens")
    source = args.package_dir.resolve() / "android/src/main/java/expo/modules/audio"
    out = ROOT / "out" / args.label
    out.mkdir(parents=True, exist_ok=True)
    copied = []
    manifest = {}
    for name in ("AudioStream.kt", "AudioStreamFileWriter.kt"):
        data = (source / name).read_bytes()
        target = out / name
        target.write_bytes(data)
        manifest[name] = {"sha256": hashlib.sha256(data).hexdigest(), "unchanged": True}
        copied.append(target)
    records = (source / "AudioRecords.kt").read_text()
    names = ["AudioStreamEncoding", "AudioStreamOptions", "AudioStreamFileFormat", "AudioStreamFileRecordingResult"]
    types = "package expo.modules.audio\nimport java.net.URL\nimport expo.modules.kotlin.records.*\nimport expo.modules.kotlin.types.Enumerable\n"
    types += "\n\n".join(declaration(records, name) for name in names)
    exceptions = (source / "AudioExceptions.kt").read_text()
    selected_exceptions = []
    for name in ("AudioStreamUnsupportedConfigException", "AudioStreamInitializationException", "AudioStreamFileException"):
        match = re.search(rf"internal class {name}\(message: String\) :\s*CodedException\(message\)", exceptions)
        if not match:
            raise ValueError(f"Missing SDK exception: {name}")
        selected_exceptions.append(match.group())
    types += "\n" + "\n".join(selected_exceptions)
    types = types.replace("import java.net.URL", "import java.net.URL\nimport expo.modules.kotlin.exception.CodedException")
    (out / "SDKTypes.kt").write_text(types)
    manifest["AudioRecords.kt"] = {"sha256": hashlib.sha256(records.encode()).hexdigest(), "extractedDeclarations": names}
    manifest["AudioExceptions.kt"] = {"sha256": hashlib.sha256(exceptions.encode()).hexdigest(), "extractedDeclarations": ["AudioStreamUnsupportedConfigException", "AudioStreamInitializationException", "AudioStreamFileException"]}
    (out / "source-manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    jars = dependency_jars(args.download_tools)
    compiler_path = os.pathsep.join(map(str, jars))
    runtime_path = os.pathsep.join(str(p) for p in jars if any(name in p.name for name in ("kotlin-stdlib", "kotlinx-coroutines-core", "annotations-")))
    sources = [*copied, out / "SDKTypes.kt", *sorted((ROOT / "stubs").glob("*.kt")), ROOT / "Repro.kt"]
    compile_command = ["java", "-cp", compiler_path, "org.jetbrains.kotlin.cli.jvm.K2JVMCompiler", "-no-stdlib", "-no-reflect", "-nowarn", "-jvm-target", "17", "-classpath", runtime_path, "-d", str(out / "classes"), *map(str, sources)]
    compiled = subprocess.run(compile_command, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    (out / "compile.log").write_text(compiled.stdout)
    if compiled.returncode:
        print(compiled.stdout)
        return compiled.returncode
    print(f'SDK AudioStream.kt SHA-256 {manifest["AudioStream.kt"]["sha256"]}')
    ran = subprocess.run(["java", "-cp", str(out / "classes") + os.pathsep + runtime_path, "repro.ReproKt", args.case], text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=30)
    print(ran.stdout, end="")
    (out / "result.log").write_text(ran.stdout)
    (out / "result.json").write_text(json.dumps({"case": args.case, "exitCode": ran.returncode, "source": manifest, "evidence": ran.stdout.splitlines()}, indent=2) + "\n")
    return ran.returncode


if __name__ == "__main__":
    sys.exit(main())
