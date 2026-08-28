#!/bin/sh
# .git/hooks/pre-commit
set -e

echo "[HOOK] Перевірка детермінізму замкового файлу..."
python3 scripts/ci_lock_checker.py dependencies.lock

if git diff --cached --name-only | grep -E '^conanfile\.(py|txt)$' && ! git diff --cached --name-only | grep -E '^conan\.lock$'; then
    echo "ПОМИЛКА: Маніфест змінено, але conan.lock не включено до коміту!"
    echo "Виконайте 'conan lock create conanfile.py' перед створенням коміту."
    exit 1
fi
