import base64
import csv
import hashlib
import os
import shutil
import subprocess
import sys
import sysconfig
import zipfile
from pathlib import Path

PKG_NAME = "fastmath"
VERSION = "1.0.0"
PYTHON_TAG = f"cp{sys.version_info.major}{sys.version_info.minor}"
ABI_TAG = f"cp{sys.version_info.major}{sys.version_info.minor}"
PLATFORM_TAG = "manylinux_2_28_x86_64"
WHEEL_NAME = f"{PKG_NAME}-{VERSION}-{PYTHON_TAG}-{ABI_TAG}-{PLATFORM_TAG}.whl"


def compile_and_patch_binaries(build_dir: Path) -> Path:
    """Скомпілювати C-розширення та налаштувати RUNPATH через patchelf."""
    py_include = sysconfig.get_path("include")
    ext_suffix = sysconfig.get_config_var("EXT_SUFFIX") or ".so"
    pkg_dir = build_dir / PKG_NAME
    libs_dir = pkg_dir / "fastmath.libs"
    libs_dir.mkdir(parents=True, exist_ok=True)

    engine_so = libs_dir / "libengine.so"
    output_so = pkg_dir / f"_fastmath{ext_suffix}"

    # 1. Компіляція допоміжної бібліотеки libengine.so
    subprocess.run([
        "gcc", "-O3", "-shared", "-fPIC",
        "-o", str(engine_so),
        "src/engine.c",
        f"-Wl,-soname,libengine-{PKG_NAME}.so.1"
    ], check=True)

    # 2. Компіляція C-розширення Python
    subprocess.run([
        "gcc", "-O3", "-shared", "-fPIC",
        f"-I{py_include}",
        "-o", str(output_so),
        "src/fastmath.c",
        f"-L{libs_dir}", "-lengine"
    ], check=True)

    # 3. Модифікація ELF заголовків: прив'язка до $ORIGIN
    subprocess.run([
        "patchelf",
        "--set-rpath", "$ORIGIN/fastmath.libs",
        "--replace-needed", "libengine.so", f"libengine-{PKG_NAME}.so.1",
        str(output_so)
    ], check=True)

    # 4. Створення пітонівського пакету
    (pkg_dir / "__init__.py").write_text(
        "from ._fastmath import dot_product\n__all__ = ['dot_product']\n",
        encoding="utf-8"
    )

    return output_so


def generate_metadata_and_record(build_dir: Path) -> None:
    """Створити каталог .dist-info з метаданими та маніфестом RECORD."""
    dist_info = build_dir / f"{PKG_NAME}-{VERSION}.dist-info"
    dist_info.mkdir(parents=True, exist_ok=True)

    # 1. Генерація METADATA
    metadata_content = (
        "Metadata-Version: 2.3\n"
        f"Name: {PKG_NAME}\n"
        f"Version: {VERSION}\n"
        "Summary: High performance vector math native extension\n"
        "Requires-Python: >=3.9\n"
        "Description-Content-Type: text/markdown\n\n"
        "# FastMath\nNative vector computation module."
    )
    (dist_info / "METADATA").write_text(metadata_content, encoding="utf-8")

    # 2. Генерація WHEEL
    wheel_content = (
        "Wheel-Version: 1.0\n"
        "Generator: custom-wheel-builder 1.0\n"
        "Root-Is-Purelib: false\n"
        f"Tag: {PYTHON_TAG}-{ABI_TAG}-{PLATFORM_TAG}\n"
    )
    (dist_info / "WHEEL").write_text(wheel_content, encoding="utf-8")

    # 3. Розрахунок криптографічного маніфесту RECORD
    record_rel_path = f"{PKG_NAME}-{VERSION}.dist-info/RECORD"
    rows: list[tuple[str, str, str | int]] = []

    for file_path in sorted(build_dir.rglob("*")):
        if file_path.is_file():
            rel = file_path.relative_to(build_dir).as_posix()
            if rel == record_rel_path:
                continue
            data = file_path.read_bytes()
            digest = hashlib.sha256(data).digest()
            hash_b64 = base64.urlsafe_b64encode(digest).decode("ascii").rstrip("=")
            rows.append((rel, f"sha256={hash_b64}", len(data)))

    # Запис самого RECORD без хешу
    rows.append((record_rel_path, "", ""))

    with open(dist_info / "RECORD", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, lineterminator="\n")
        writer.writerows(rows)


def build_final_wheel_archive(build_dir: Path, output_file: Path) -> None:
    """Запакувати результат у детермінований ZIP-архів wheel."""
    with zipfile.ZipFile(output_file, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for file_path in sorted(build_dir.rglob("*")):
            if file_path.is_file():
                arcname = file_path.relative_to(build_dir).as_posix()
                # Встановлення фіксованих дозволів на файли (0755 для бінарників, 0644 для тексту)
                zinfo = zipfile.ZipInfo.from_file(file_path, arcname=arcname)
                # Нормалізація дати до 1980-01-01 для детермінованого SHA-256 архіву
                zinfo.date_time = (1980, 1, 1, 0, 0, 0)
                if file_path.suffix in [".so", ".pyd", ".dylib"]:
                    zinfo.external_attr = 0o755 << 16
                else:
                    zinfo.external_attr = 0o644 << 16
                
                with open(file_path, "rb") as f:
                    zf.writestr(zinfo, f.read())
    
    print(f"Успішно зібрано бінарний архів: {output_file}")
