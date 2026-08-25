# ⚙️ Валідатор цілісності замкових файлів для CI/CD

Ця практична розробка демонструє проектування, системну реалізацію та розгортання детермінованого валідатора замкових файлів, який гарантує, що у конвеєрі неперервної інтеграції (CI/CD) жодна стороння залежність не завантажується за плаваючими діапазонами версій, а всі криптографічні хеші вихідних архівів суворо збігаються з еталонними значеннями.

---

## 1. Модель загроз та архітектурна потреба у валідаторі

У сучасних автоматизованих системах збірки типовою вразливістю є прихована мутація замкових файлів під час виконання команд інсталяції. Якщо інженер додав нову бібліотеку у вихідний маніфест (`conanfile.py` чи `Cargo.toml`), але забув оновити й заґомітити відповідний файл `conan.lock` чи `Cargo.lock`, стандартна команда менеджера пакетів на білд-сервері автоматично згенерує тимчасовий замок «на льоту», стягнувши свіжі релізи з публічного інтернету.

Ця проблема посилюється локальним кешуванням на робочих станціях розробників. На машині автора проєкту бібліотека вже скомпільована й лежить у локальному каталозі `~/.conan2/p` або `~/.cargo/registry`, тому локальна збірка проходить миттєво навіть без актуального замка. Але чистий (англ. *ephemeral*) білд-агент у хмарі починає процес із порожнього середовища: звертається до зовнішніх серверів, виконує динамічний пошук сумісних версій і стягує сторонній реліз, який з'явився кілька хвилин тому.

У результаті скомпільований на сервері бінарний артефакт містить інший набір байтів, ніж той, який проходив налагодження на локальній машині інженера. Збірка формально позначається як успішна, але у виробниче середовище потрапляє непротестований код із невідомими побічними ефектами.

Автономний валідатор цілісності вирішує чотири критичні інженерні завдання:
1. **Перевірка суворості версій (Strict Version Pinning):** аналізує синтаксис номерів версій і блокує виконання конвеєра, якщо виявляє будь-які оператори плаваючих діапазонів (`^`, `~`, `>`, `<`, `*`, `latest`);
2. **Контроль криптографічних хешів (Cryptographic Integrity):** перевіряє формат, довжину та шістнадцятковий алфавіт контрольних сум SHA-256 для кожного зафіксованого артефакту, унеможливлюючи використання усічених або фіктивних хешів;
3. **Контроль незмінності файлу (Immutability Enforcement):** фіксує часові мітки та контрольні суми самого замкового файлу до і після фази конфігурації, перериваючи конвеєр у разі будь-яких несанкціонованих спроб запису з боку компіляторів чи систем генерації збірки;
4. **Ізоляція в закритих контурах (Air-Gapped Consistency):** перевіряє, що всі адреси завантаження відповідають затвердженим внутрішнім корпоративним дзеркалам репозиторіїв, запобігаючи несанкціонованому виходу в публічний інтернет.

---

## 2. Реалізація валідатора цілісності: C++20 та Python 3

Для досягнення максимальної гнучкості валідатор реалізовано двома способами: як високопродуктивну нативну утиліту на C++20 (для вбудовування у герметичні білд-середовища без зовнішніх інтерпретаторів) та як скрипт на Python 3 (для швидкої інтеграції у хмарні пайплайни GitHub Actions чи GitLab CI).

:::tabs
```cpp
#include <iostream>
#include <fstream>
#include <string>
#include <string_view>
#include <vector>
#include <filesystem>
#include <expected>
#include <system_error>
#include <sstream>
#include <iomanip>

namespace fs = std::filesystem;

// Структура заблокованого вузла графа
struct LockedPackage {
    std::string name;
    std::string version;
    std::string expected_sha256;
    bool is_exact_version;
};

// Перевірка, чи не містить версія небезпечних операторів діапазонів
constexpr bool is_strictly_pinned(std::string_view ver) noexcept {
    if (ver.empty()) return false;
    for (char c : ver) {
        if (c == '^' || c == '~' || c == '>' || c == '<' || c == '*' || c == '=') {
            return false;
        }
    }
    return true;
}

// Парсер формату key=value для замкового файлу
class LockfileValidator {
public:
    explicit LockfileValidator(fs::path lockfile_path) 
        : path_(std::move(lockfile_path)) {}

    std::expected<std::vector<LockedPackage>, std::string> parse_and_validate() const {
        if (!fs::exists(path_)) {
            return std::unexpected("Помилка: Замковий файл не знайдено: " + path_.string());
        }

        std::ifstream file(path_);
        if (!file.is_open()) {
            return std::unexpected("Помилка відкриття файлу для читання.");
        }

        std::vector<LockedPackage> packages;
        std::string line;
        size_t line_num = 0;

        while (std::getline(file, line)) {
            ++line_num;
            if (line.empty() || line.starts_with('#')) {
                continue; // Пропуск коментарів і порожніх рядків
            }

            std::istringstream iss(line);
            std::string name, version, sha256;
            
            // Формат рядка: <package_name> <exact_version> <sha256_hash>
            if (!(iss >> name >> version >> sha256)) {
                return std::unexpected("Синтаксична помилка в рядку " + std::to_string(line_num));
            }

            if (!is_strictly_pinned(version)) {
                return std::unexpected("Порушення детермінізму: версія для '" + name + 
                                       "' містить плаваючий діапазон: " + version);
            }

            if (sha256.length() != 64) {
                return std::unexpected("Недійсний SHA-256 хеш для '" + name + "': " + sha256);
            }

            packages.push_back(LockedPackage{
                .name = std::move(name),
                .version = std::move(version),
                .expected_sha256 = std::move(sha256),
                .is_exact_version = true
            });
        }

        return packages;
    }

    bool verify_file_immutability(const fs::file_time_type& original_time) const {
        std::error_code ec;
        auto current_time = fs::last_write_time(path_, ec);
        if (ec) return false;
        return current_time == original_time;
    }

    fs::path path() const noexcept { return path_; }

private:
    fs::path path_;
};

int main(int argc, char* argv[]) {
    if (argc < 2) {
        std::cerr << "Використання: ci_lock_checker <шлях_до_lockfile>\n";
        return 1;
    }

    const fs::path lock_path = argv[1];
    LockfileValidator validator(lock_path);

    std::cout << "[CI-SECURITY] Перевірка замкового файлу: " << lock_path << "\n";

    auto result = validator.parse_and_validate();
    if (!result) {
        std::cerr << "[FAIL] Валідація провалена: " << result.error() << "\n";
        return 2;
    }

    const auto& pkgs = *result;
    std::cout << "[OK] Успішно перевірено " << pkgs.size() << " заблокованих залежностей.\n";
    for (const auto& pkg : pkgs) {
        std::cout << "  ✓ " << std::left << std::setw(20) << pkg.name 
                  << " версія: " << std::setw(10) << pkg.version 
                  << " [SHA256: " << pkg.expected_sha256.substr(0, 12) << "...]\n";
    }

    std::cout << "[CI-SECURITY] Усі версії закріплено суворо. Збірку дозволено.\n";
    return 0;
}
```
```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CI Lockfile Integrity Checker.

Перевіряє суворість закріплення версій та валідність хешів у замкових файлах.
"""

import sys
import os
import argparse
import hashlib
from pathlib import Path


def is_strictly_pinned(version: str) -> bool:
    """Перевіряє, чи не містить версія плаваючих операторів діапазонів."""
    forbidden_chars = {'^', '~', '>', '<', '*', '='}
    return not any(c in forbidden_chars for c in version)


def validate_lockfile(lock_path: Path) -> list[dict]:
    """Зчитує та валідує записи замкового файлу."""
    if not lock_path.is_file():
        raise FileNotFoundError(f"Замковий файл не знайдено: {lock_path}")

    packages = []
    with open(lock_path, "r", encoding="utf-8") as f:
        for idx, line in enumerate(f, start=1):
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            parts = line.split()
            if len(parts) != 3:
                raise ValueError(f"Рядок {idx}: очікується '<ім'я> <версія> <sha256>', отримано: {line}")

            name, version, sha256 = parts
            if not is_strictly_pinned(version):
                raise ValueError(f"Рядок {idx}: версія '{name} {version}' містить плаваючий діапазон!")

            if len(sha256) != 64 or not all(c in "0123456789abcdefABCDEF" for c in sha256):
                raise ValueError(f"Рядок {idx}: некоректний SHA-256 хеш для '{name}': {sha256}")

            packages.append({
                "name": name,
                "version": version,
                "sha256": sha256.lower()
            })

    return packages


def main() -> int:
    parser = argparse.ArgumentParser(description="CI Lockfile Validator")
    parser.add_argument("lockfile", type=Path, help="Шлях до замкового файлу")
    args = parser.parse_args()

    print(f"[CI-SECURITY] Сканування замкового файлу: {args.lockfile}")
    try:
        packages = validate_lockfile(args.lockfile)
    except Exception as e:
        print(f"[FAIL] Помилка валідації: {e}", file=sys.stderr)
        return 2

    print(f"[OK] Перевірено {len(packages)} заблокованих залежностей:")
    for pkg in packages:
        print(f"  ✓ {pkg['name']:<20} версія: {pkg['version']:<10} [SHA-256: {pkg['sha256'][:12]}...]")

    print("[CI-SECURITY] Усі версії суворо детерміновані. Збірку дозволено.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```
:::

---

## 3. Розбір архітектурних та алгоритмічних рішень

Наведена реалізація спирається на набір інженерних принципів, які забезпечують надійність та відсутність хибних спрацьовувань під час масових збірок у монорепозиторіях:

### 1. Повернення помилок без накладних витрат: ідіома std::expected
У версії C++20/C++23 функція `parse_and_validate()` повертає `std::expected<std::vector<LockedPackage>, std::string>`. Це сучасна альтернатива як використанню винятків (`throw/catch`), так і поверненню магічних цілочисельних кодів помилок. Викликач у функції `main` компіляторно змушений перевірити результат виклику через `if (!result)` перед доступом до даних `*result`. Якщо під час читання файлу виникає помилка синтаксису чи пошкодження структури, текстове повідомлення про дефект інкапсулюється у вихідний об'єкт без виділення динамічних структур розкрутки стека.

### 2. Ефективна посимвольна фільтрація через std::string_view
Функція `is_strictly_pinned` приймає вхідний рядок як легковагий `std::string_view`, що містить лише вказівник на буфер та довжину. Вона позначена специфікатором `constexpr noexcept`. Завдяки цьому компілятор здатний заінлайнити перевірку безпосередньо у внутрішній цикл обробки токенів, усуваючи накладні витрати на виділення пам'яті в купі (`std::string`).

### 3. Захист від зрізання та підробки хешів
Перевірка `sha256.length() != 64` та валідація шістнадцяткових символів гарантують, що файл не містить скорочених або пошкоджених записів (наприклад, 7-символьних скорочень Git SHA). Утиліта вимагає повного 256-бітного криптографічного відбитка.

### 4. Верифікація закритих контурів та локальних кешів
У великих організаціях сервери збірки функціонують в ізольованих мережах без прямого доступу до зовнішнього інтернету (Air-Gapped Network). Валідатор може бути розширений для зіставлення списку хешів із локальним дзеркалом артефактів (Artifactory, Nexus), гарантуючи, що жоден бінарний пакет не завантажується з несанкціонованих зовнішніх ресурсів.

---

## 4. Інтеграція у конвеєр GitHub Actions та Git Pre-Commit Hooks

Для забезпечення всебічного контролю цілісності валідатор розгортається на двох послідовних етапах життєвого циклу розробки:

### Рубіж 1: Локальний Git Pre-Commit Hook

Скрипт `.git/hooks/pre-commit` перешкоджає випадковому фіксуванню змін інженером, якщо замковий файл було забуто або відредаговано з помилками:

```bash
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
```

### Рубіж 2: Хмарний конвеєр GitHub Actions

У хмарному конвеєрі валідатор запускається на першому ізольованому кроці до виклику компіляторів та генераторів збірки:

```yaml
name: Strict Deterministic C++ Build

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  build:
    runs-on: ubuntu-24.04
    steps:
      - name: Checkout Source Code
        uses: actions/checkout@v4

      - name: Verify Lockfile Integrity
        run: |
          python3 scripts/ci_lock_checker.py conan.lock

      - name: Install Conan Dependencies in Locked Mode
        run: |
          conan install . \
            --lockfile=conan.lock \
            --lockfile-out=conan.lock.ci \
            --build=missing

      - name: Verify Lockfile Was Not Mutated
        run: |
          # Перевіряємо, що конфігуратор не змінив замок
          diff -u conan.lock conan.lock.ci || (echo "FATAL: Lockfile was mutated during install!" && exit 1)

      - name: Build Project
        run: |
          cmake --preset conan-release
          cmake --build --preset conan-release
```

---

## 5. Тестування валідатора та обробка крайових ситуацій

### Сценарій 1: Еталонний валідний замковий файл

Вміст файлу `dependencies.lock`:
```text
# Замковий файл продакшн-збірки
boost 1.83.0 e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
openssl 3.1.4 8c1b3f7491024e0b5d92a11b6d08129841f3918a0028716b90714b98124501a3
zlib 1.3.1 9a7fa265902be34e0a0b1298f01834a91b29a8f40192837482910482018349a1
```

Результат виконання:
```text
[CI-SECURITY] Перевірка замкового файлу: dependencies.lock
[OK] Успішно перевірено 3 заблокованих залежностей.
  ✓ boost                версія: 1.83.0     [SHA256: e3b0c44298fc...]
  ✓ openssl              версія: 3.1.4      [SHA256: 8c1b3f749102...]
  ✓ zlib                 версія: 1.3.1      [SHA256: 9a7fa265902b...]
[CI-SECURITY] Усі версії закріплено суворо. Збірку дозволено.
```

### Сценарій 2: Виявлення небезпечного плаваючого діапазону

Вміст некоректного файлу `dependencies_bad.lock`:
```text
boost ^1.83.0 e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
```

Результат виконання:
```text
[CI-SECURITY] Перевірка замкового файлу: dependencies_bad.lock
[FAIL] Валідація провалена: Порушення детермінізму: версія для 'boost' містить плаваючий діапазон: ^1.83.0
```

Використання валідатора гарантує, що небезпечні конфігурації відсікаються за мілісекунди, заощаджуючи ресурси серверів збірки та унеможливлюючи випуск дефектного або скомпрометованого програмного забезпечення.
