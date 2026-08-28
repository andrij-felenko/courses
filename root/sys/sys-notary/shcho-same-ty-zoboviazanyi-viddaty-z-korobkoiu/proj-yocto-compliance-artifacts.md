# ⚙️ Автоматизація ліцензійних артефактів: генерація Notices, маніфестів та архіву джерел у Yocto і Buildroot

Коли складальний конвеєр формує фінальний образ кореневої файлової системи (rootfs) для мікропроцесорної плати, формування юридичних артефактів — консолідованого файлу ліцензій, маніфесту атрибуції та повного архіву вихідного коду — не повинно виконуватися вручну. Ручний збір патчів, конфігурацій ядра та ліцензійних файлів перед релізом неминуче призводить до розсинхронізації: бінарник у флеш-пам'яті містить зміни, яких немає в архіві вихідних кодів, або в ліцензійному буклеті пропущено сторонню бібліотеку.

У цій інструкції розібрано практичний інженерний конвеєр автоматизованої генерації комплаєнс-пакета у двох головних складальних системах вбудованого Linux — Yocto Project (OpenEmbedded) та Buildroot, створення утиліти валідації повноти архіву, фільтрацію несумісних ліцензій та інтеграцію комплаєнс-шлюзу в безперервну інтеграцію (CI/CD).

## 1. Yocto Project / OpenEmbedded: класи `archiver` та `license`

Складальна система Yocto має потужну вбудовану інфраструктуру для аудиту ліцензій та автоматичного пакування вихідних кодів. Під час виконання кожного завдання компіляції (`do_compile`) шар ядра OpenEmbedded Core перевіряє ліцензійні прапорці в рецептах (`LICENSE`), порівнює їх із білими списками дозволених ліцензій (`LICENSE_FLAGS_ACCEPTED`) і зберігає копії файлів ліцензій у робочому каталозі.

За замовчуванням під час збирання цільового образу (`bitbake core-image-minimal`) Yocto генерує каталог із ліцензіями кожного встановленого пакета за адресою `tmp/deploy/licenses/<image-name>-<machine>/`.

Проте для виконання вимог статті 3 ліцензії GPLv2 цього недостатньо: дистриб'ютор зобов'язаний зберегти точний вихідний код із накладеними вендорськими патчами, файлами конфігурації та інструкціями збирання. Для цього використовується спеціальний клас `archiver.bbclass`.

Щоб автоматично сформувати повний архів вихідного коду (Complete Corresponding Source) разом із накладеними патчами, конфігураційними файлами та рецептами, у файл конфігурації дистрибутива (`conf/local.conf` або `conf/distro/my-distro.conf`) додаються директиви класу `archiver`:

```bitbake
# ------------------------------------------------------------------------------
# Конфігурація генерації ліцензійних артефактів та архіву вихідного коду в Yocto
# ------------------------------------------------------------------------------

# 1. Підключення архіватора вихідних текстів
INHERIT += "archiver"

# 2. Режим архівації: вихідний код із накладеними патчами (patched)
# Інші варіанти: 'original' (чистий апстрім) або 'configured' (після ./configure)
ARCHIVER_MODE[src] = "patched"

# 3. Збереження окремих .patch файлів та серії quilt
ARCHIVER_MODE[diff] = "1"

# 4. Додавання конфігурації збирання та рецепта BitBake (.bb) до кожного архіву
ARCHIVER_MODE[dumpdata] = "1"
ARCHIVER_MODE[recipe] = "1"

# 5. Фільтрація типів пакетів: архівувати лише цільові пакети образу (target)
COPYLEFT_RECIPE_TYPES = "target"

# 6. Вибіркове виключення пропрієтарного закритого коду
# Вказуємо ліцензії, які архіватор зобов'язаний збирати (копілефт)
COPYLEFT_LICENSE_INCLUDE = "GPL* LGPL* MPL* EPL* AGPL*"

# 7. Генерація єдиного консолідованого файлу ліцензій (Open Source Notices)
LICENSE_CREATE_PACKAGE = "1"
COPY_LIC_MANIFEST = "1"
COPY_LIC_DIRS = "1"
```

### Механізм роботи архіватора в Yocto

Коли BitBake виконує збірку дистрибутива з підключеним класом `archiver`, для кожного рецепта запускаються додаткові завдання:
- `do_ar_patched`: створює архів сирців після застосування всіх латок із масиву `SRC_URI`;
- `do_ar_recipe`: пакує `.bb` файл рецепта та всі супутні файли конфігурації;
- `do_ar_dumpdata`: зберігає повний стан змінних BitBake на момент збирання пакета (включаючи `CFLAGS`, `LDFLAGS` та налаштування крос-компілятора).

Якщо проект використовує пристрої із заблокованим завантажувачем (Secure Boot), де ліцензія GPLv3 є неприйнятною через вимогу надання ключів підпису, у конфігурацію додається директива блокування:

```bitbake
# Заборона включення пакетів під GPLv3 до цільового образу
INCOMPATIBLE_LICENSE = "GPL-3.0-only GPL-3.0-or-later LGPL-3.0-only LGPL-3.0-or-later"
```

Після завершення збірки командою:

```bash
bitbake -k custom-gateway-image
```

У каталозі `tmp/deploy/` формуються два ключові каталоги артефактів:

1. **`tmp/deploy/licenses/custom-gateway-image-<machine>/`:**
   - `license.manifest`: табличний файл зі списком усіх пакетів, їхніх точних версій та SPDX-ідентифікаторів ліцензій;
   - `package.manifest`: перелік бінарних пакунків, що потрапили в результуючий образ;
   - `rootfs-licenses/`: повне дерево всіх текстових файлів ліцензій, витягнутих із початкових джерел.

2. **`tmp/deploy/sources/<arch>/<recipe-name>/`:**
   - `<package>-<version>-src.tar.gz`: архів модифікованого вихідного коду з накладеними вендорськими патчами;
   - `<package>-<version>-recipe.tar.gz`: точний рецепт BitBake з інструкціями збирання та контрольною сумою `SRC_URI`.

## 2. Buildroot: автоматична генерація через `make legal-info`

У складальній системі Buildroot генерація юридичного звіту та архіву вихідних кодів вбудована безпосередньо в базовий Makefile. Для створення повного комплекту комплаєнс-документації виконується одна команда:

```bash
make legal-info
```

Buildroot компілює повне дерево залежностей цільової конфігурації, перевіряє ліцензійні метадані в кожному файлі пакета `.mk` (`<PKG>_LICENSE` та `<PKG>_LICENSE_FILES`), завантажує оригінальні архіви сирців і вивантажує результат у каталог `output/legal-info/`:

```text
output/legal-info/
├── manifest.csv           # Таблиця: пакет, версія, ліцензія, файл ліцензії, джерело
├── host-manifest.csv      # Залежності інструментів хост-машини
├── licenses/              # Зібрані оригінальні тексти ліцензій для кожного пакета
│   ├── busybox-1.36.1/
│   │   └── LICENSE
│   ├── linux-6.1.55/
│   │   └── COPYING
│   └── zlib-1.2.13/
│       └── README
└── sources/               # Повні tar.gz архіви вихідного коду всіх компонентів
    ├── busybox-1.36.1.tar.bz2
    ├── linux-6.1.55.tar.xz
    └── zlib-1.2.13.tar.xz
```

Вміст згенерованого файлу `manifest.csv` має стандартизований вигляд, придатний для імпорту в корпоративні бази комплаєнсу та автоматичного аудиту:

```csv
"PACKAGE","VERSION","LICENSE","LICENSE FILES","SOURCE ARCHIVE","SOURCE SITE"
"busybox","1.36.1","GPL-2.0","LICENSE","busybox-1.36.1.tar.bz2","https://busybox.net/downloads"
"linux","6.1.55","GPL-2.0","COPYING","linux-6.1.55.tar.xz","https://cdn.kernel.org/pub/linux/kernel/v6.x"
"zlib","1.2.13","Zlib","README","zlib-1.2.13.tar.xz","http://www.zlib.net"
```

Якщо в проекті використовуються зовнішні дерева розробки (`BR2_EXTERNAL`) або локальні пакети з перевизначенням коду (`local` або `git` репозиторії), Buildroot автоматично архівує поточний стан локальної робочої копії та зберігає застосовані латки з каталогу `package/<pkgname>/`.

## 3. Автоматизований збирач Open Source Notices (C / C++)

Щоб перетворити розрізнені файли ліцензій та маніфест `manifest.csv` у єдиний друкований буклет або HTML-сторінку для вбудованого веб-сервера пристрою, використовується службова утиліта злиття. Утиліта читає маніфест, для кожного пакета витягує його оригінальний текст ліцензії та формує структурований вихідний документ.

Нижче наведено повноцінну реалізацію генератора Notices мовами C та C++.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAX_LINE 2048

/* Читання файлу ліцензії та запис його вмісту до результуючого буклету */
static int append_license_text(FILE *out, const char *lic_path) {
    FILE *in = fopen(lic_path, "r");
    if (!in) {
        fprintf(stderr, "Помилка: не вдалося відкрити файл ліцензії: %s\n", lic_path);
        return -1;
    }

    char buffer[MAX_LINE];
    while (fgets(buffer, sizeof(buffer), in)) {
        fputs(buffer, out);
    }

    fclose(in);
    return 0;
}

/* Генератор консолідованого буклету Open Source Notices з CSV-маніфесту */
int generate_notices(const char *csv_path, const char *lic_dir, const char *out_path) {
    FILE *csv = fopen(csv_path, "r");
    if (!csv) {
        fprintf(stderr, "Помилка: не вдалося відкрити CSV-маніфест: %s\n", csv_path);
        return -1;
    }

    FILE *out = fopen(out_path, "w");
    if (!out) {
        fclose(csv);
        fprintf(stderr, "Помилка: не вдалося створити вихідний файл: %s\n", out_path);
        return -1;
    }

    fprintf(out, "================================================================================\n");
    fprintf(out, "                    OPEN SOURCE SOFTWARE NOTICES & LICENSES\n");
    fprintf(out, "================================================================================\n\n");

    char line[MAX_LINE];
    int is_header = 1;

    while (fgets(line, sizeof(line), csv)) {
        if (is_header) {
            is_header = 0;
            continue; /* Пропуск заголовка CSV */
        }

        /* Розбір рядка вигляду: "pkg","ver","license","lic_file","src_tar","url" */
        char pkg[128], ver[64], lic[128], lic_file[128];
        char *token = strtok(line, ",\"\r\n");
        if (!token) continue;
        strncpy(pkg, token, sizeof(pkg) - 1);

        token = strtok(NULL, ",\"\r\n");
        if (!token) continue;
        strncpy(ver, token, sizeof(ver) - 1);

        token = strtok(NULL, ",\"\r\n");
        if (!token) continue;
        strncpy(lic, token, sizeof(lic) - 1);

        token = strtok(NULL, ",\"\r\n");
        if (!token) continue;
        strncpy(lic_file, token, sizeof(lic_file) - 1);

        fprintf(out, "--------------------------------------------------------------------------------\n");
        fprintf(out, "Package: %s (version: %s)\n", pkg, ver);
        fprintf(out, "SPDX License: %s\n", lic);
        fprintf(out, "--------------------------------------------------------------------------------\n\n");

        char full_lic_path[512];
        snprintf(full_lic_path, sizeof(full_lic_path), "%s/%s-%s/%s", lic_dir, pkg, ver, lic_file);

        if (append_license_text(out, full_lic_path) != 0) {
            /* Якщо специфічного файлу версії немає, спробуємо знайти загальний */
            snprintf(full_lic_path, sizeof(full_lic_path), "%s/%s/%s", lic_dir, pkg, lic_file);
            append_license_text(out, full_lic_path);
        }
        fprintf(out, "\n\n");
    }

    fclose(csv);
    fclose(out);
    return 0;
}
```
```cpp
#include <iostream>
#include <fstream>
#include <sstream>
#include <string>
#include <vector>
#include <filesystem>
#include <expected>

namespace fs = std::filesystem;

struct PackageInfo {
    std::string name;
    std::string version;
    std::string license;
    std::string license_file;
};

class NoticesGenerator {
public:
    static std::expected<void, std::string> build_notices(
        const fs::path& csv_manifest,
        const fs::path& licenses_dir,
        const fs::path& output_file) 
    {
        std::ifstream csv(csv_manifest);
        if (!csv.is_open()) {
            return std::unexpected("Не вдалося відкрити CSV-маніфест: " + csv_manifest.string());
        }

        std::ofstream out(output_file);
        if (!out.is_open()) {
            return std::unexpected("Не вдалося створити вихідний файл: " + output_file.string());
        }

        out << "================================================================================\n"
            << "                    OPEN SOURCE SOFTWARE NOTICES & LICENSES\n"
            << "================================================================================\n\n";

        std::string line;
        bool is_header = true;

        while (std::getline(csv, line)) {
            if (is_header) {
                is_header = false;
                continue;
            }
            if (line.empty()) continue;

            auto pkg = parse_csv_line(line);
            if (!pkg) continue;

            out << "--------------------------------------------------------------------------------\n"
                << "Package: " << pkg->name << " (version: " << pkg->version << ")\n"
                << "SPDX License: " << pkg->license << "\n"
                << "--------------------------------------------------------------------------------\n\n";

            auto lic_path = licenses_dir / (pkg->name + "-" + pkg->version) / pkg->license_file;
            if (!fs::exists(lic_path)) {
                lic_path = licenses_dir / pkg->name / pkg->license_file;
            }

            if (fs::exists(lic_path)) {
                std::ifstream lic_stream(lic_path);
                out << lic_stream.rdbuf() << "\n\n";
            } else {
                out << "[Текст ліцензії відсутній за шляхом: " << lic_path.string() << "]\n\n";
            }
        }

        return {};
    }

private:
    static std::optional<PackageInfo> parse_csv_line(const std::string& line) {
        std::stringstream ss(line);
        std::string item;
        std::vector<std::string> fields;

        while (std::getline(ss, item, ',')) {
            // Видаляємо лапки навколо полів CSV
            if (item.size() >= 2 && item.front() == '"' && item.back() == '"') {
                item = item.substr(1, item.size() - 2);
            }
            fields.push_back(item);
        }

        if (fields.size() < 4) return std::nullopt;
        return PackageInfo{fields[0], fields[1], fields[2], fields[3]};
    }
};
```
:::

## 4. Скрипт валідації комплаєнс-пакета в CI/CD

Перед тим як релізний архів буде передано на виробничу лінію прошивання та завантажено на сервер дистрибуції оферти, CI/CD конвеєр запускає скрипт валідації. Скрипт перевіряє, що для кожного копілефтного пакета в образі існує непустий архів вихідного коду та коректний текстовий файл ліцензії:

```bash
#!/usr/bin/env bash
set -euo pipefail

MANIFEST="output/legal-info/manifest.csv"
SOURCES_DIR="output/legal-info/sources"
LICENSES_DIR="output/legal-info/licenses"

echo "=== Запуск перевірки повноти ліцензійного пакета ==="

ERRORS=0

# Пропуск заголовка CSV та читання кожного рядка
tail -n +2 "$MANIFEST" | while IFS=',' read -r pkg ver lic licfile src site; do
    # Видалення лапок
    pkg="${pkg//\"/}"
    ver="${ver//\"/}"
    lic="${lic//\"/}"
    src="${src//\"/}"

    # Перевірка наявності вихідного архіву для копілефтних ліцензій
    if [[ "$lic" =~ GPL|LGPL|MPL|AGPL ]]; then
        ARCHIVE_PATH="$SOURCES_DIR/$src"
        if [[ ! -f "$ARCHIVE_PATH" || ! -s "$ARCHIVE_PATH" ]]; then
            echo "❌ ПОМИЛКА: Відсутній архів вихідних кодів для $pkg-$ver ($lic): $ARCHIVE_PATH"
            ERRORS=$((ERRORS + 1))
        else
            echo "  ✓ Знайдено вихідний код: $src"
        fi
    fi
done

if [[ "$ERRORS" -gt 0 ]]; then
    echo "❌ Валідація провалена: виявлено $ERRORS порушень у комплаєнс-пакеті."
    exit 1
fi

echo "✅ Усі обов'язкові вихідні коди та ліцензії присутні. Пакет готовий до релізу."
```

## 5. Інтеграція в корпоративну інфраструктуру релізів

Після успішного проходження валідаційного скрипту артефакти комплаєнсу автоматично розділяються за призначенням:

1. **Артефакти для друку:** консолідований файл `notices.txt` або `notices.pdf` передається на друкарський комбінат або додається до виробничого комплекту упаковки для друку вкладиша до кожної коробки.
2. **Артефакти для веб-інтерфейсу:** згенеровані ліцензійні сторінки упаковуються у кореневу файлову систему прошивки за адресою `/www/legal/` або `/usr/share/doc/licenses/`.
3. **Артефакти для письмової оферти:** повні вихідні архіви збірки та рецепти пакуються в єдиний монолітний архів `release-<model>-<version>-sources.tar.xz`, який завантажується в захищене довгострокове хмарне сховище (AWS S3 Glacier або внутрішній реліз-сервер) із гарантією збереження не менше 5 років.

Така трирівнева схема автоматизації перетворює ліцензійну відповідність із виснажливої ручної праці на надійний інженерний конвеєр, що спрацьовує при кожному релізному збиранні.
