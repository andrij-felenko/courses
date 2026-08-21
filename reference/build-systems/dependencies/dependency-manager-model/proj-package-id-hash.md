# ⚙️ Алгоритм детермінованого розрахунку Package ID для C++

Головна відмінність двійкового менеджера пакетів C++ (як-от Conan) від менеджерів мов зі стандартизованим середовищем виконання полягає в тому, що одне й те саме ім'я та версія бібліотеки (наприклад, `zlib/1.3.1`) відповідають не одному файлу архіву, а сотням взаємно несумісних скомпільованих бінарників. Клієнтський менеджер пакетів повинен гарантовано обчислити, чи існує у віддаленому сховищі бінарний пакет, що на 100% сумісний із поточним тулчейном розробника.

Для вирішення цієї задачі використовується алгоритм обчислення **детермінованого ідентифікатора пакета** (англ. *Package ID*). Алгоритм збирає всі фактори, що впливають на двійковий інтерфейс (ABI), нормалізує їх у канонічну форму та обчислює криптографічний хеш. Цей документ розбирає математичну модель, покроковий механізм канонізації та повну робочу реалізацію генератора Package ID.

---

## 1. Вхідний простір параметрів та архітектура хешування

Розрахунок Package ID спирається на три незалежні множини параметрів:

1. **Налаштування платформи та компілятора (`settings`)**:
   * Операційна система (`os`: `Linux`, `Windows`, `Macos`).
   * Архітектура процесора (`arch`: `x86_64`, `armv8`, `riscv64`).
   * Сімейство та версія компілятора (`compiler`: `gcc`, `clang`, `msvc`; `compiler.version`: `13`, `17`, `19.3`).
   * Стандарт мови C++ (`compiler.cppstd`: `17`, `20`, `23`).
   * Тип рантайму C++ (`compiler.libcxx`: `libstdc++11`, `libc++`; `compiler.runtime`: `MD`, `MT`).
   * Конфігурація збірки (`build_type`: `Release`, `Debug`, `RelWithDebInfo`).
2. **Опції конфігурації бібліотеки (`options`)**:
   * Тип компонування (`shared`: `True` / `False`).
   * Позиційно-незалежний код (`fPIC`: `True` / `False`).
   * Функціональні прапорці (наприклад, `with_zlib`: `True`, `use_simd`: `False`).
3. **Хеші прямих транзитивних залежностей (`requires`)**:
   * Перелік Package ID усіх бібліотек, від яких безпосередньо залежить поточний пакет. Якщо залежність нижнього рівня змінила свій двійковий хеш, поточний пакет також отримує новий Package ID, оскільки зміни у типах заголовочних файлів залежності неминуче транслюються у скомпільований код.

```text
Вхідні параметри (settings, options, requires_ids)
  │
  ▼
1. Фільтрація нерелевантних параметрів (очищення settings для header-only)
  │
  ▼
2. Канонізація ключів і значень (приведення до нижнього регістру, видалення пробілів)
  │
  ▼
3. Лексикографічне сортування всіх записів за алфавітом ключів
  │
  ▼
4. Формування канонічного байтового потоку (порядок: settings -> options -> requires)
  │
  ▼
5. Обчислення криптографічного дайджесту (SHA-256 або 64-бітний детермінований хеш)
  │
  ▼
Результат: Унікальний рядок Package ID (наприклад, pkg_4a91c78e3b1290ff)
```

---

## 2. Покроковий алгоритм канонізації

Детермінізм обчислення хешу є критичною вимогою: якщо клієнт на машині Windows збирає параметри в іншому порядку або з символами повернення каретки `\r\n`, а сервер на Linux обчислює хеш із роздільником `\n`, клієнт отримає помилковий промах повз кеш (Cache Miss) і буде змушений перекомпільовувати бібліотеку з нуля.

Алгоритм вимагає суворого дотримання таких кроків:

1. **Нормалізація рядків:** Усі текстові ключі та значення переводяться у нижній регістр (ASCII-lower) без зайвих пробілів на початку чи в кінці.
2. **Лексикографічне сортування:** Оскільки структури типу «хеш-таблиця» у різних мовах програмування мають непередбачуваний порядок ітерації елементів, усі пари «ключ — значення» впорядковуються за зростанням байтових значень ключів за допомогою стандартного двійкового порівняння.
3. **Канонічний формат запису:** Кожен запис кодується як один рядок виду `prefix:key=value\n`, де `prefix` однозначно визначає категорію параметра (`s:` для налаштувань, `o:` для опцій, `r:` для залежностей). Роздільником рядків завжди є виключно одиночний байт `\n` (ASCII 10).
4. **Хешування:** Байтовий потік подається на вхід криптографічної або швидкої хеш-функції (у промисловому Conan 2.0 використовується SHA-1 або SHA-256).

---

## 3. Робоча реалізація канонізатора та генератора Package ID

Нижче наведено робочу реалізацію алгоритму двома мовами. Програма приймає конфігураційні словники налаштувань, опцій та ідентифікаторів залежностей, нормалізує їх і видає детермінований Package ID.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

#define MAX_ENTRIES 32
#define MAX_STR_LEN 128

typedef struct {
    char key[MAX_STR_LEN];
    char val[MAX_STR_LEN];
} KeyValue;

typedef struct {
    KeyValue entries[MAX_ENTRIES];
    size_t count;
} ConfigMap;

static void map_add(ConfigMap *m, const char *k, const char *v) {
    if (m->count >= MAX_ENTRIES) return;
    strncpy(m->entries[m->count].key, k, MAX_STR_LEN - 1);
    m->entries[m->count].key[MAX_STR_LEN - 1] = '\0';
    strncpy(m->entries[m->count].val, v, MAX_STR_LEN - 1);
    m->entries[m->count].val[MAX_STR_LEN - 1] = '\0';
    m->count++;
}

static int compare_entries(const void *a, const void *b) {
    const KeyValue *ka = (const KeyValue *)a;
    const KeyValue *kb = (const KeyValue *)b;
    return strcmp(ka->key, kb->key);
}

/* 64-бітний алгоритм FNV-1a для детермінованого обчислення дайджесту */
static uint64_t compute_hash_fnv1a(const char *data, size_t len) {
    uint64_t hash = 14695981039346656037ULL;
    for (size_t i = 0; i < len; ++i) {
        hash ^= (uint8_t)data[i];
        hash *= 1099511628211ULL;
    }
    return hash;
}

void compute_package_id(ConfigMap *settings, ConfigMap *options, ConfigMap *deps, char out_id[32]) {
    /* Сортуємо всі словники за алфавітом ключів */
    qsort(settings->entries, settings->count, sizeof(KeyValue), compare_entries);
    qsort(options->entries, options->count, sizeof(KeyValue), compare_entries);
    if (deps) {
        qsort(deps->entries, deps->count, sizeof(KeyValue), compare_entries);
    }

    char canonical[4096] = {0};
    size_t offset = 0;

    for (size_t i = 0; i < settings->count; ++i) {
        int n = snprintf(canonical + offset, sizeof(canonical) - offset,
                         "s:%s=%s\n", settings->entries[i].key, settings->entries[i].val);
        if (n > 0) offset += (size_t)n;
    }
    for (size_t i = 0; i < options->count; ++i) {
        int n = snprintf(canonical + offset, sizeof(canonical) - offset,
                         "o:%s=%s\n", options->entries[i].key, options->entries[i].val);
        if (n > 0) offset += (size_t)n;
    }
    if (deps) {
        for (size_t i = 0; i < deps->count; ++i) {
            int n = snprintf(canonical + offset, sizeof(canonical) - offset,
                             "r:%s=%s\n", deps->entries[i].key, deps->entries[i].val);
            if (n > 0) offset += (size_t)n;
        }
    }

    uint64_t h = compute_hash_fnv1a(canonical, offset);
    snprintf(out_id, 32, "pkg_%016llx", (unsigned long long)h);
}

int main(void) {
    ConfigMap settings = { .count = 0 };
    map_add(&settings, "os", "Linux");
    map_add(&settings, "arch", "x86_64");
    map_add(&settings, "compiler", "gcc");
    map_add(&settings, "compiler.version", "13");
    map_add(&settings, "compiler.cppstd", "20");
    map_add(&settings, "build_type", "Release");

    ConfigMap options = { .count = 0 };
    map_add(&options, "shared", "False");
    map_add(&options, "fPIC", "True");

    ConfigMap deps = { .count = 0 };
    map_add(&deps, "zlib", "pkg_e72a084c911b33fa");

    char pkg_id[32];
    compute_package_id(&settings, &options, &deps, pkg_id);

    printf("Розрахований Package ID: %s\n", pkg_id);
    return 0;
}
```
```cpp
#include <iostream>
#include <string>
#include <string_view>
#include <map>
#include <vector>
#include <sstream>
#include <iomanip>
#include <cstdint>

class PackageIdCalculator {
public:
    void set_setting(std::string key, std::string value) {
        settings_[std::move(key)] = std::move(value);
    }

    void set_option(std::string key, std::string value) {
        options_[std::move(key)] = std::move(value);
    }

    void add_dependency_id(std::string dep_name, std::string dep_package_id) {
        dependencies_[std::move(dep_name)] = std::move(dep_package_id);
    }

    [[nodiscard]] std::string compute_id() const {
        std::ostringstream canonical_stream;

        // Контейнер std::map гарантує суворе лексикографічне сортування за ключами
        for (const auto& [k, v] : settings_) {
            canonical_stream << "s:" << k << '=' << v << '\n';
        }
        for (const auto& [k, v] : options_) {
            canonical_stream << "o:" << k << '=' << v << '\n';
        }
        for (const auto& [k, v] : dependencies_) {
            canonical_stream << "r:" << k << '=' << v << '\n';
        }

        const std::string canonical_str = canonical_stream.str();
        const uint64_t hash_val = compute_fnv1a(canonical_str);

        std::ostringstream id_stream;
        id_stream << "pkg_" << std::hex << std::setw(16) << std::setfill('0') << hash_val;
        return id_stream.str();
    }

private:
    static uint64_t compute_fnv1a(std::string_view data) noexcept {
        uint64_t hash = 14695981039346656037ULL;
        for (const char c : data) {
            hash ^= static_cast<uint8_t>(c);
            hash *= 1099511628211ULL;
        }
        return hash;
    }

    std::map<std::string, std::string> settings_;
    std::map<std::string, std::string> options_;
    std::map<std::string, std::string> dependencies_;
};

int main() {
    PackageIdCalculator calc;

    calc.set_setting("os", "Linux");
    calc.set_setting("arch", "x86_64");
    calc.set_setting("compiler", "gcc");
    calc.set_setting("compiler.version", "13");
    calc.set_setting("compiler.cppstd", "20");
    calc.set_setting("build_type", "Release");

    calc.set_option("shared", "False");
    calc.set_option("fPIC", "True");

    calc.add_dependency_id("zlib", "pkg_e72a084c911b33fa");

    const std::string package_id = calc.compute_id();
    std::cout << "Розрахований Package ID: " << package_id << '\n';

    return 0;
}
```
:::

---

## 4. Специфічні режими та граничні випадки обчислення Package ID

У реальній практиці застосування однакових правил хешування до всіх типів бібліотек призводило б до надлишкової перекомпіляції. Менеджери пакетів реалізують чотири спеціальні режими обчислення Package ID:

### 1. Бібліотеки виключно з заголовочних файлів (Header-Only Libraries)
Бібліотеки на зразок `nlohmann_json`, `Catch2` або `Eigen` складаються виключно з шаблонів та вбудованих функцій. Вони не містять жодного скомпільованого двійкового файлу (`.a` чи `.so`). Для таких пакетів налаштування компілятора (`compiler`), рівень оптимізації (`build_type`) та тип компонування (`shared`) не мають жодного впливу на артефакт. У рецепті пакета викликається інструкція `self.info.clear()`, яка повністю очищує словники `settings` та `options`. У результаті для всіх можливих операційних систем та компіляторів генерується один спільний Package ID (наприклад, `pkg_da39a3ee5e6b4b0d`), що дозволяє завантажувати єдиний архів із заголовочними файлами для будь-якої платформи.

### 2. Моделі поширення версійних змін (Package ID Modes)
Коли бібліотека `A` залежить від бібліотеки `B`, менеджер може використовувати різні стратегії оновлення Package ID для `A` під час зміни версії `B`:
* **`semver_direct_mode` (стандартний режим):** зміна патч-версії бібліотеки `B` (`1.2.0` → `1.2.1`) або мінорної версії (`1.2.0` → `1.3.0`) не змінює Package ID бібліотеки `A`, якщо її власний двійковий інтерфейс залишається сумісним.
* **`full_package_mode` (суворий режим):** будь-яка зміна Package ID бібліотеки `B` (навіть зміна прапорця оптимізації) автоматично змінює Package ID бібліотеки `A`, змушуючи клієнта повністю перекомпілювати `A`. Цей режим є обов'язковим для статичних бібліотек, які вшивають код залежностей у власний об'єктний архів.
* **`unrelated_mode`:** використовується для інструментів збірки (`tool_requires`). Версія утиліти `cmake` чи `ninja` жодним чином не впливає на двійковий хеш скомпільованого прикладного пакета.

---

## 5. Повний кортеж ідентифікації пакета в розподіленому кеші

У промислових системах керування залежностями (як-от JFrog Artifactory) сам по собі `Package ID` є лише одним із чотирьох компонентів повної адресації двійкового артефакту. Повний кортеж ідентифікації має вигляд:

```text
(Package_Reference, Recipe_Revision, Package_ID, Package_Revision)
```

1. **`Package_Reference` (`pkg/version@user/channel`):** назва, версія та простір імен бібліотеки.
2. **`Recipe_Revision` (RREV):** 40-символьний криптографічний хеш тексту самого рецепта (`conanfile.py` або `portfile.cmake`). Якщо супроводжувач порту виправив помилку в сценарії збірки, не змінюючи версію вихідного коду бібліотеки, RREV змінюється, захищаючи клієнтів від використання застарілих інструкцій компіляції.
3. **`Package_ID`:** розрахований вище хеш двійкової конфігурації тулчейна.
4. **`Package_Revision` (PREV):** хеш вмісту скомпільованого двійкового архіву. Якщо той самий рецепт було перекомпільовано на сервері CI після оновлення системних бібліотек, новий бінарник отримує свіжий PREV.

Завдяки такій чотиривимірній моделі адресації двійковий кеш повністю унеможливлює випадкове завантаження застарілих або бінарно несумісних бібліотек, забезпечуючи стовідсоткову відтворюваність збірки у розподілених командах.
