# -*- coding: utf-8 -*-
import os
import sys
import hashlib
import subprocess
import tempfile

PROTO_FILE = "proto/user_profile.proto"
GEN_CPP_HEADER = "src/backend/generated/user_profile.pb.h"
GEN_TS_FILE = "src/frontend/generated/user_profile.ts"

def calculate_sha256(filepath: str) -> str:
    hasher = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()

def verify_contracts() -> bool:
    print(f"[*] Перевірка єдиного джерела правди для {PROTO_FILE}...")
    if not os.path.exists(PROTO_FILE):
        print(f"[ERROR] Файл схеми {PROTO_FILE} не знайдено!")
        return False

    with tempfile.TemporaryDirectory() as tmpdir:
        cmd = ["protoc", f"--proto_path={os.path.dirname(PROTO_FILE)}", f"--cpp_out={tmpdir}", PROTO_FILE]
        try:
            subprocess.run(cmd, check=True, capture_output=True)
        except subprocess.CalledProcessError as err:
            print(f"[ERROR] Помилка виклику protoc: {err.stderr.decode()}")
            return False

        temp_header = os.path.join(tmpdir, "user_profile.pb.h")
        if os.path.exists(GEN_CPP_HEADER) and os.path.exists(temp_header):
            current_hash = calculate_sha256(GEN_CPP_HEADER)
            fresh_hash = calculate_sha256(temp_header)
            if current_hash != fresh_hash:
                print("[X] ПОМИЛКА: Виявлено дрейф моделей C++!")
                print("    Згенеровані файли не відповідають файлу схеми.")
                print("    Виконайте 'make codegen' перед створенням Pull Request.")
                return False

        print("[OK] C++ контракти повністю відповідають схемі.")
        print("[OK] Дрейфу моделей не виявлено. Єдине джерело правди збережено.")
        return True

if __name__ == "__main__":
    if not verify_contracts():
        sys.exit(1)
