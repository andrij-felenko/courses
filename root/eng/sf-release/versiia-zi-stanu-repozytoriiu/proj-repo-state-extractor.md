# ⚙️ Автоматичний генератор метаданих версії та ворота чистоти збірки

Спроба вручну підтримувати версію у файлі заголовка призводить до двох типових виробничих катастроф: інженер забуває оновити рядок перед формуванням релізу, або бінарник збирається з локально зміненого робочого дерева і стає невідтворюваним «привидом». Створимо автоматизований конвеєр генерації метаданих версії на етапі збірки, який зчитує стан Git-дерева, перевіряє чистоту робочого каталогу, захищає систему компіляції від зайвої повної перезбірки та вбудовує типізовану структуру безпосередньо в пам'ять програми.

## Архітектура та послідовність роботи генератора

Конвеєр складається з чотирьох чітко розмежованих послідовних кроків:

1. **Екстракція стану репозиторію:** виклик утиліт контролю версій для отримання найближчого тегу, кількості комітів після нього, скороченого криптографічного хешу, детермінованої часової мітки останнього коміту та статусу модифікації файлів.
2. **Перевірка воріт чистоти (Release Gate):** якщо збірка налаштована в релізному профілі (`Release`), наявність будь-яких незбережених змін у робочому дереві або в індексі викликає негайне аварійне зупинення конвеєра з ненульовим кодом повернення.
3. **Атомарне оновлення заголовка:** запис згенерованого тексту в тимчасовий буферний файл і заміна цільового заголовка на диску лише за наявності реальних змін у байтах. Це зберігає часову мітку файлу (`mtime`) незмінною і рятує інструменти компіляції від повторного розбору всього проєкту.
4. **Компіляція та лінкування структури:** підключення згенерованого коду до бінарника з розміщенням структури у виділеній секції двійкового образу (`.version_header`).

Розглянемо реалізацію кожного етапу з урахуванням граничних випадків та особливостей вбудованих і серверних систем.

## Скрипт вилучення стану репозиторію

Реалізуємо портативний скрипт екстракції мовою Python 3, який однаково надійно працює в середовищах Linux, macOS і Windows. Скрипт акуратно обробляє ситуації, коли каталог збирається безпосередньо з розпакованого вихідного архіву (tarball), коли в репозиторії ще немає жодного тегу, або коли історія комітів була обрізана інструментами неглибокого клонування.

```py
#!/usr/bin/env python3
import subprocess
import sys
import os
import re
import time
import zlib

def run_git(cmd):
    try:
        res = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )
        return res.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None

def extract_version_info(is_release_mode=False):
    # Перевірка наявності каталогу .git
    git_dir = run_git(["git", "rev-parse", "--git-dir"])
    if not git_dir:
        # Режим fallback: читання статичного version.txt якщо зібрано з архіву без VCS
        if os.path.exists("version.txt"):
            with open("version.txt", "r", encoding="utf-8") as f:
                raw_ver = f.read().strip()
                return parse_version_string(raw_ver, is_dirty=False, timestamp=int(time.time()), is_git=False)
        sys.stderr.write("ПОМИЛКА: Каталог не є Git-репозиторієм і version.txt відсутній!\n")
        sys.exit(1)

    # 1. Отримання базового рядка версії через git describe
    raw_desc = run_git(["git", "describe", "--tags", "--always", "--dirty", "--long"])
    if not raw_desc:
        raw_desc = "v0.0.0-0-g0000000"

    # 2. Перевірка статусу робочого дерева
    status_out = run_git(["git", "status", "--porcelain"])
    is_dirty = bool(status_out) or raw_desc.endswith("-dirty")

    # 3. Ворота чистоти для релізного профілю
    if is_release_mode and is_dirty:
        sys.stderr.write("\n=======================================================\n")
        sys.stderr.write("КРИТИЧНА ПОМИЛКА ВОРОТ ЗБІРКИ: ВИЯВЛЕНО БРУДНЕ ДЕРЕВО!\n")
        sys.stderr.write("Заборонено випускати Release-бінарник із незбереженими сирцями.\n")
        sys.stderr.write("Незбережені або модифіковані файли:\n")
        sys.stderr.write(status_out if status_out else "Невідповідність індексу Git\n")
        sys.stderr.write("=======================================================\n\n")
        sys.exit(1)

    # 4. Часова мітка останнього коміту (SOURCE_DATE_EPOCH для детермінізму)
    ts_str = run_git(["git", "log", "-1", "--format=%ct"])
    timestamp = int(ts_str) if ts_str and ts_str.isdigit() else int(time.time())

    return parse_version_string(raw_desc, is_dirty, timestamp, is_git=True)

def parse_version_string(raw, is_dirty, timestamp, is_git):
    # Очікуваний формат: v<major>.<minor>.<patch>-<commits>-g<hash>
    clean_raw = raw.replace("-dirty", "")
    match = re.match(r"^v?(\d+)\.(\d+)\.(\d+)(?:-(\d+)-g([0-9a-fA-F]+))?$", clean_raw)
    
    if match:
        major = int(match.group(1))
        minor = int(match.group(2))
        patch = int(match.group(3))
        commits = int(match.group(4)) if match.group(4) else 0
        git_hash = match.group(5) if match.group(5) else "0000000"
        tag_name = f"v{major}.{minor}.{patch}"
    else:
        # Fallback якщо тегів взагалі немає в репозиторії
        major, minor, patch, commits = 0, 0, 0, 0
        git_hash = run_git(["git", "rev-parse", "--short=8", "HEAD"]) or "0000000"
        tag_name = "v0.0.0-untagged"

    return {
        "major": major,
        "minor": minor,
        "patch": patch,
        "commits": commits,
        "hash": git_hash[:8].ljust(8, '\0'),
        "tag": tag_name,
        "dirty": is_dirty,
        "timestamp": timestamp,
        "is_git": is_git,
        "full_string": raw
    }
```

## Генерація коду C та C++

Згенерований файл містить типізовану структуру даних, константи часу компіляції та розміщує структуру у виділеній секції пам'яті `.version_header`. Зверніть увагу на прагму пакування `#pragma pack(push, 4)`: вона гарантує, що зміщення полів у пам'яті будуть ідентичними незалежно від цільової архітектури (32-бітний ARM чи 64-бітний x86-64), що дозволяє зовнішнім інструментам і завантажувачам надійно парсити бінарник безпосередньо з флеш-пам'яті.

:::tabs
```c
/* Згенеровано автоматично: не редагувати вручну */
#ifndef VERSION_INFO_H
#define VERSION_INFO_H

#include <stdint.h>
#include <stdbool.h>

#define VERSION_MAGIC 0x56455253U /* 'VERS' */
#define VERSION_STRUCT_VER 1U

#define BUILD_FLAG_DIRTY      (1U << 0)
#define BUILD_FLAG_DEBUG      (1U << 1)
#define BUILD_FLAG_PRERELEASE (1U << 2)
#define BUILD_FLAG_CI         (1U << 3)

#pragma pack(push, 4)
typedef struct {
    uint32_t magic;
    uint16_t struct_version;
    uint16_t flags;
    uint16_t major;
    uint16_t minor;
    uint16_t patch;
    uint16_t reserved;
    uint32_t commit_count;
    char     git_sha_short[8];
    uint64_t timestamp;
    char     tag_name[32];
    uint32_t crc32;
} version_info_t;
#pragma pack(pop)

/* Розміщення у виділеній секції двійкового образу */
#if defined(__GNUC__) || defined(__clang__)
__attribute__((section(".version_header"), used))
#endif
extern const version_info_t g_firmware_version;

/* Допоміжні функції читання */
static inline bool version_is_dirty(const version_info_t *v) {
    return (v->flags & BUILD_FLAG_DIRTY) != 0;
}

static inline bool version_is_release(const version_info_t *v) {
    return (v->flags & (BUILD_FLAG_DIRTY | BUILD_FLAG_DEBUG | BUILD_FLAG_PRERELEASE)) == 0;
}

#endif /* VERSION_INFO_H */
```
```cpp
/* Згенеровано автоматично: не редагувати вручну */
#pragma once

#include <cstdint>
#include <string_view>
#include <array>
#include <span>

namespace build_metadata {

inline constexpr std::uint32_t magic_signature = 0x56455253U; // 'VERS'
inline constexpr std::uint16_t struct_version_v1 = 1U;

enum class BuildFlags : std::uint16_t {
    None       = 0,
    Dirty      = 1U << 0,
    Debug      = 1U << 1,
    Prerelease = 1U << 2,
    Ci         = 1U << 3
};

constexpr BuildFlags operator|(BuildFlags a, BuildFlags b) noexcept {
    return static_cast<BuildFlags>(static_cast<std::uint16_t>(a) | static_cast<std::uint16_t>(b));
}

constexpr bool has_flag(BuildFlags value, BuildFlags flag) noexcept {
    return (static_cast<std::uint16_t>(value) & static_cast<std::uint16_t>(flag)) != 0;
}

#pragma pack(push, 4)
struct VersionInfo {
    std::uint32_t magic;
    std::uint16_t struct_version;
    BuildFlags    flags;
    std::uint16_t major;
    std::uint16_t minor;
    std::uint16_t patch;
    std::uint16_t reserved;
    std::uint32_t commit_count;
    std::array<char, 8> git_sha_short;
    std::uint64_t timestamp;
    std::array<char, 32> tag_name;
    std::uint32_t crc32;

    [[nodiscard]] constexpr bool is_dirty() const noexcept {
        return has_flag(flags, BuildFlags::Dirty);
    }

    [[nodiscard]] constexpr bool is_official_release() const noexcept {
        return !is_dirty() && !has_flag(flags, BuildFlags::Debug | BuildFlags::Prerelease);
    }

    [[nodiscard]] std::string_view tag() const noexcept {
        return std::string_view(tag_name.data());
    }

    [[nodiscard]] std::string_view sha() const noexcept {
        return std::string_view(git_sha_short.data(), 8);
    }
};
#pragma pack(pop)

#if defined(__GNUC__) || defined(__clang__)
[[gnu::section(".version_header"), gnu::used]]
#endif
extern const VersionInfo active_version_descriptor;

} // namespace build_metadata
```
:::

## Атомарний запис і захист кешу компіляції

Якщо під час кожного запуску утиліти складання (`make` чи `ninja`) беззастережно перезаписувати файл `version_info.h`, його часова мітка останньої модифікації на диску оновлюватиметься. Це змусить систему компіляції вважати цей файл зміненим і запустити повторну трансляцію всіх модулів проєкту, які прямо чи опосередковано включають цей заголовок. У результаті швидка інкрементальна збірка перетворюється на виснажливу повну перекомпіляцію (так званий «шторм збірки», англ. *rebuild storm*).

Щоб запобігти цьому, генератор спочатку створює буфер у пам'яті або записує тимчасовий файл `version_info.h.tmp`, побайтово звіряє його вміст із наявним файлом на диску і здійснює запис **виключно у випадку, коли в даних виявлено реальну різницю**. Якщо стан Git не змінився (той самий коміт і той самий статус чистоти), системний виклик запису пропускається, і дата файлу на файловій системі залишається недоторканою.

```py
def write_header_atomically(header_path, content):
    # Якщо файл уже існує на диску і його вміст збігається — зберігаємо старий mtime
    if os.path.exists(header_path):
        with open(header_path, "r", encoding="utf-8") as existing:
            if existing.read() == content:
                return False # Файл не змінювався, перезбірка залежних одиниць не потрібна

    tmp_path = header_path + ".tmp"
    with open(tmp_path, "w", encoding="utf-8") as f:
        f.write(content)

    # Атомарна заміна файлу в межах однієї файлової системи
    os.replace(tmp_path, header_path)
    return True
```

## Інтеграція в систему збірки CMake

Підключимо генератор до системи збірки CMake через створення спеціальної цілі `add_custom_target`, яка перевіряє стан репозиторію перед компіляцією основного двійкового файлу. Ми використовуємо механізм генераторних виразів (`generator expressions`), щоб автоматично передавати прапорець `--fail-on-dirty` тільки для конфігурацій типу `Release` та `MinSizeRel`, залишаючи розробникам свободу експериментів під час збірки відлагоджувального профілю `Debug`.

```cmake
# CMakeLists.txt
cmake_minimum_required(VERSION 3.20)
project(FirmwareApp C CXX)

set(VERSION_HEADER_PATH "${CMAKE_CURRENT_BINARY_DIR}/generated/version_info.h")
set(VERSION_SOURCE_PATH "${CMAKE_CURRENT_BINARY_DIR}/generated/version_info.c")

# Визначення, чи активний релізний режим
set(IS_RELEASE_BUILD FALSE)
if(CMAKE_BUILD_TYPE STREQUAL "Release" OR CMAKE_BUILD_TYPE STREQUAL "MinSizeRel")
    set(IS_RELEASE_BUILD TRUE)
endif()

add_custom_target(generate_version_metadata
    COMMAND ${Python3_EXECUTABLE} "${CMAKE_CURRENT_SOURCE_DIR}/scripts/gen_version.py"
            --output-header "${VERSION_HEADER_PATH}"
            --output-source "${VERSION_SOURCE_PATH}"
            $<$<BOOL:${IS_RELEASE_BUILD}>:--fail-on-dirty>
    BYPRODUCTS "${VERSION_HEADER_PATH}" "${VERSION_SOURCE_PATH}"
    COMMENT "Перевірка стану Git-репозиторію та генерація метаданих версії..."
)

add_executable(firmware_app
    src/main.c
    src/driver.c
    "${VERSION_SOURCE_PATH}"
)

add_dependencies(firmware_app generate_version_metadata)
target_include_directories(firmware_app PRIVATE "${CMAKE_CURRENT_BINARY_DIR}/generated")
```

## Інженерні пастки реалізації

Під час впровадження автоматичного генератора версії команди розробки найчастіше стикаються з трьома критичними підводними каменями:

1. **Невідстежувані тимчасові файли (Untracked Files):** утиліта `git status --porcelain` за замовчуванням виводить будь-які сторонні файли, що з'явилися в каталозі проєкту. Якщо інженер випадково залишив текстовий лог, тимчасовий скрипт або дамп пам'яті, конвеєр може помилково визначити дерево як «брудне» і заблокувати випуск. Рішення полягає у суворій підтримці файлу `.gitignore` або явному виклику перевірки з прапорцем `git status --porcelain --untracked-files=no`, якщо команда свідомо бажає ігнорувати невідстежувані артефакти.
2. **Автоматичне перетворення кінців рядків (CRLF / LF):** на робочих станціях під керуванням Windows увімкнена опція `core.autocrlf=true` може перетворювати розділювачі рядків під час вичитування файлів. Для Git це виглядає як масова модифікація сотень файлів сирців одночасно, перетворюючи чисту збірку на брудну. Щоб уникнути таких хибних спрацьовувань, завжди додавайте файл `.gitattributes` у корінь репозиторію із явним правилом `* text=auto eol=lf`.
3. **Обрізана історія клонування в хмарному CI (Shallow Clones):** сучасні сервіси автоматизації (GitHub Actions, GitLab CI) за замовчуванням виконують поверхневе клонування репозиторію з глибиною один коміт (`git clone --depth=1`). У такому стані в локальному сховищі відсутні батьківські коміти та анотовані теги, тому виклик `git describe` повертає помилку або аварійний рядок з нулями. У конфігурації завдання CI обов'язково встановлюйте параметр повного витягування історії (`fetch-depth: 0`).
4. **Брудні підмодулі (Git Submodules):** якщо проєкт використовує зовнішні бібліотеки у вигляді підмодулів, зміна стану підмодуля (локальний коміт або незбережена правка всередині підкаталогу) не завжди відображається у виводі кореневого `git describe`, проте робить усю кодову базу невідтворюваною. Скрипт воріт релізу зобов'язаний додатково виконувати команду `git submodule status --recursive`, щоб гарантувати абсолютну чистоту всіх залежностей перед початком фінальної збірки.
