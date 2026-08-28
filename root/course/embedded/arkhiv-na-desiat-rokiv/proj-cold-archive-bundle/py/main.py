#!/usr/bin/env python3
import os
import sys
import json
import hashlib
import subprocess
import shutil
from datetime import datetime, timezone

def sha256_file(filepath):
    """Обчислення SHA-256 для файлу блоками по 64 КБ."""
    h = hashlib.sha256()
    with open(filepath, 'rb') as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

def create_git_bundle(repo_path, output_bundle):
    """Створення автономного git bundle з усіма гілками та тегами."""
    cmd = ["git", "-C", repo_path, "bundle", "create", output_bundle, "--all"]
    subprocess.run(cmd, check=True)

def seal_archive(project_dir, output_archive_dir):
    os.makedirs(output_archive_dir, exist_ok=True)
    os.makedirs(os.path.join(output_archive_dir, "src"), exist_ok=True)
    os.makedirs(os.path.join(output_archive_dir, "bin"), exist_ok=True)
    os.makedirs(os.path.join(output_archive_dir, "env"), exist_ok=True)
    os.makedirs(os.path.join(output_archive_dir, "hw"), exist_ok=True)
    os.makedirs(os.path.join(output_archive_dir, "docs"), exist_ok=True)

    # 1. Експорт вихідного коду в автономний bundle
    main_bundle = os.path.join(output_archive_dir, "src", "main_firmware.bundle")
    create_git_bundle(project_dir, main_bundle)

    # 2. Отримання SHA коміту та дерева
    commit_sha = subprocess.check_output(
        ["git", "-C", project_dir, "rev-parse", "HEAD"], text=True
    ).strip()

    # 3. Експорт образу контейнера тулчейну (якщо використовується Docker/Podman)
    container_tar = os.path.join(output_archive_dir, "env", "builder_env.tar.gz")
    # subprocess.run(["docker", "save", "firmware-builder:v1.0", "-o", container_tar], check=True)

    # 4. Формування маніфесту
    manifest = {
        "schema_version": "1.2.0",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "epoch_timestamp": int(datetime.now(timezone.utc).timestamp()),
        "commit_sha": commit_sha,
        "files": []
    }

    # Обхід усіх файлів у структурі та збір хешів
    for root, _, files in os.walk(output_archive_dir):
        for f in files:
            if f in ["archive-manifest.json", "archive-manifest.sig"]:
                continue
            full_path = os.path.join(root, f)
            rel_path = os.path.relpath(full_path, output_archive_dir).replace("\\", "/")
            manifest["files"].append({
                "path": rel_path,
                "size_bytes": os.path.getsize(full_path),
                "sha256": sha256_file(full_path)
            })

    manifest_path = os.path.join(output_archive_dir, "archive-manifest.json")
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    print(f"[OK] Архів успішно сформовано: {output_archive_dir}")
    print(f"[OK] Маніфест містить {len(manifest['files'])} артефактів.")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Використання: archive_seal.py <каталог_проєкту> <каталог_архіву>")
        sys.exit(1)
    seal_archive(sys.argv[1], sys.argv[2])
