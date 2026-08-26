# ⚙️ Конвеєр ліцензійного аудиту бінарних залежностей на C та C++

У виробничих конвеєрах складання системного програмного забезпечення — від вбудованих Linux-дистрибутивів на базі Yocto або Buildroot до мінімалістичних контейнерних образів мікросервісів — критично важливо автоматично верифікувати ліцензійну чистоту кожного скомпільованого артефакту ще до його передачі кінцевим замовникам або завантаження в публічний реєстр.

Помилкове включення сторонньої бібліотеки під ліцензією `GPL-2.0-only` у статично скомпонований двійковий файл комерційного застосунку, або прямий виклик функцій динамічної бібліотеки під `AGPL-3.0` у закритому бекенд-демоні створює непереборні юридичні ризики примусового розкриття вихідного коду всієї інтелектуальної власності компанії.

Цей проєкт реалізує повноцінний автономний двигун ліцензійного аудиту та верифікації графа залежностей. Він аналізує архітектурний спосіб зв'язування компонентів, парсить нормалізовані ідентифікатори ліцензійних угод стандарту SPDX, обчислює взаємну сумісність за бітовою матрицею правил і генерує формальний юридичний звіт для блокування чи схвалення збірки в конвеєрі CI/CD.

## Архітектура та принцип роботи аудитора

Двигун аудиту працює як контрольний шлюз якості (*Quality Gate*) на завершальному етапі конвеєра складання після компонування бінарних артефактів. Його робота складається з чотирьох послідовних стадій:

1. **Інспекція способів зв'язування (Linkage Inspection):**
   Інструмент аналізує двійковий файл ELF. За допомогою читання заголовків секції `.dynamic` та записів `DT_NEEDED` він виявляє всі спільні бібліотеки (`.so`), з якими зв'язаний бінарник. Для модулів, що не мають запису `DT_NEEDED`, перевіряється таблиця символів `.symtab` для виявлення слідів статичного компонування стороннього об'єктного коду (`.a` / `.o`). Взаємодія через IPC (Unix domain sockets, pipes, REST) маркується окремим типом зв'язування.
2. **Зіставлення метаданих пакунків (SPDX Resolution):**
   Для кожної виявленої залежності зчитується нормалізований ліцензійний вираз (наприклад, з маніфестів пакунків, файлів `.pc` у `pkg-config` або вбудованих ELF-секцій `.comment` і `.note.spdx`).
3. **Обчислення булевої сумісності (Compatibility Matrix Evaluation):**
   Двигун транслює строкові SPDX-ідентифікатори у бітові маски ліцензійних родин і виконує перевірку сумісності пари `(Target_License, Dep_License, Link_Type)` за константний час `O(1)`.
4. **Формування вердикту та аварійне переривання:**
   Якщо виявлено хоча б одне неприпустиме поєднання (наприклад, статичний лінк GPL у пропрієтарний бінарник або спільне використання Apache 2.0 та GPL-2.0-only), процес завершується з ненульовим кодом повернення, блокуючи публікацію релізу в репозиторії.

## Деталі аналізу формату ELF та динамічного компонування

Під час аналізу бінарних файлів інструмент зчитує системні структури з системного заголовка `<elf.h>`. Секція динамічного компонування `SHT_DYNAMIC` містить масив структур `Elf64_Dyn`. Кожен елемент із тегом `d_tag == DT_NEEDED` містить зміщення в таблиці рядків `DT_STRTAB`, що вказує на точне ім'я залежної бібліотеки (наприклад, `libmbedcrypto.so.3` або `libsqlite3.so.0`).

Якщо бібліотеку знайдено у списку `DT_NEEDED`, спосіб компонування класифікується як `LINK_DYNAMIC`. Якщо ж функції бібліотеки викликаються в секції коду `.text`, але ім'я бібліотеки відсутнє у списку динамічних залежностей, це свідчить про те, що статичний архів `.a` був повністю вшитий у бінарник компонувачем на етапі збирання (`LINK_STATIC`).

## Алгебра бітових масок у матриці сумісності

Застосування бітових масок дозволяє закодувати складні юридичні правила у швидкі порозрядні операції. Кожному класу ліцензій присвоюється окремий біт у машинному слові. Це забезпечує високу швидкість обробки: навіть якщо проєкт містить тисячі транзитивних залежностей, перевірка всього графа займає кілька мікросекунд, що критично важливо для важких конвеєрів CI/CD.

## Реалізація інструменту ліцензійного аудиту

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>

/* Бітові маски ліцензійних родин для швидкої алгебраїчної перевірки */
typedef enum {
    LIC_UNKNOWN      = 0,
    LIC_PERMISSIVE   = 1 << 0,  /* MIT, BSD, ISC */
    LIC_APACHE2      = 1 << 1,  /* Apache 2.0 (патентний грант) */
    LIC_WEAK_COPYLEFT= 1 << 2,  /* LGPL, MPL */
    LIC_GPL2_ONLY    = 1 << 3,  /* GPL-2.0-only */
    LIC_GPL3_PLUS    = 1 << 4,  /* GPL-3.0+, LGPL-3.0+ */
    LIC_AGPL3        = 1 << 5,  /* AGPL-3.0 (мережевий копілефт) */
    LIC_PROPRIETARY  = 1 << 6   /* Закритий комерційний код */
} LicenseType;

typedef enum {
    LINK_STATIC,
    LINK_DYNAMIC,
    LINK_IPC_BOUNDARY
} LinkageType;

typedef struct {
    const char *name;
    const char *spdx_id;
    LicenseType type;
    LinkageType linkage;
} Dependency;

typedef struct {
    const char *project_name;
    LicenseType target_license;
    Dependency *deps;
    size_t dep_count;
} ProjectContext;

/* Перевірка сумісності пари ліцензій за способом зв'язування */
static bool is_pair_compatible(LicenseType target, LicenseType dep_lic, LinkageType link) {
    /* Міжпроцесна ізоляція (IPC) знімає обмеження ліцензійного зараження */
    if (link == LINK_IPC_BOUNDARY) {
        return true;
    }

    /* Пропрієтарний цільовий продукт */
    if (target == LIC_PROPRIETARY) {
        if (dep_lic == LIC_PERMISSIVE || dep_lic == LIC_APACHE2) {
            return true;
        }
        /* Слабкий копілефт (LGPL) дозволений ТІЛЬКИ при динамічному лінкуванні */
        if (dep_lic == LIC_WEAK_COPYLEFT) {
            return (link == LINK_DYNAMIC);
        }
        /* Сильний або мережевий копілефт категорично заборонений */
        return false;
    }

    /* Цільовий проєкт під GPL-2.0-only */
    if (target == LIC_GPL2_ONLY) {
        if (dep_lic == LIC_PERMISSIVE || dep_lic == LIC_GPL2_ONLY) {
            return true;
        }
        /* Конфлікт століття: Apache 2.0 несумісна з GPL-2.0-only */
        if (dep_lic == LIC_APACHE2) {
            return false;
        }
        if (dep_lic == LIC_GPL3_PLUS || dep_lic == LIC_AGPL3) {
            return false;
        }
        return true;
    }

    /* Цільовий проєкт під GPL-3.0+ */
    if (target == LIC_GPL3_PLUS) {
        /* GPLv3 сумісна з Apache 2.0 та Permissive */
        if (dep_lic == LIC_PERMISSIVE || dep_lic == LIC_APACHE2 ||
            dep_lic == LIC_GPL3_PLUS || dep_lic == LIC_WEAK_COPYLEFT) {
            return true;
        }
        /* GPL-2.0-only несумісна з GPLv3, якщо немає застереження 'or later' */
        if (dep_lic == LIC_GPL2_ONLY) {
            return false;
        }
        return true;
    }

    return false;
}

/* Запуск повного аудиту графа залежностей */
static int audit_project(const ProjectContext *ctx) {
    int violations = 0;
    printf("[AUDIT] Перевірка проєкту: %s\n", ctx->project_name);
    printf("------------------------------------------------------------\n");

    for (size_t i = 0; i < ctx->dep_count; ++i) {
        const Dependency *d = &ctx->deps[i];
        bool ok = is_pair_compatible(ctx->target_license, d->type, d->linkage);

        const char *link_str = (d->linkage == LINK_STATIC) ? "STATIC" :
                               (d->linkage == LINK_DYNAMIC) ? "DYNAMIC (.so)" : "IPC";

        if (ok) {
            printf("  [PASS] %-15s | SPDX: %-15s | Link: %-12s\n", d->name, d->spdx_id, link_str);
        } else {
            printf("  [FAIL] %-15s | SPDX: %-15s | Link: %-12s  <-- ЮРИДИЧНИЙ КОНФЛІКТ!\n",
                   d->name, d->spdx_id, link_str);
            violations++;
        }
    }

    printf("------------------------------------------------------------\n");
    if (violations > 0) {
        printf("[ВИСНОВОК] Збірку заблоковано! Знайдено %d несумісних ліцензій.\n", violations);
        return 1;
    } else {
        printf("[ВИСНОВОК] Аудит пройдено успішно. Всі компоненти сумісні.\n");
        return 0;
    }
}

int main(void) {
    /* Тестовий стек компонентів вбудованого контролера */
    Dependency deps[] = {
        {"cJSON",       "MIT",                 LIC_PERMISSIVE,    LINK_STATIC},
        {"mbedTLS",     "Apache-2.0",          LIC_APACHE2,       LINK_STATIC},
        {"libmodbus",   "LGPL-2.1-or-later",   LIC_WEAK_COPYLEFT, LINK_DYNAMIC},
        {"busybox",     "GPL-2.0-only",        LIC_GPL2_ONLY,     LINK_IPC_BOUNDARY},
        {"libgpl_math", "GPL-2.0-only",        LIC_GPL2_ONLY,     LINK_STATIC} /* Порушення! */
    };

    ProjectContext proprietary_app = {
        .project_name = "EdgeGateway-Daemon (Proprietary)",
        .target_license = LIC_PROPRIETARY,
        .deps = deps,
        .dep_count = sizeof(deps) / sizeof(deps[0])
    };

    return audit_project(&proprietary_app);
}
```
```cpp
#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <expected>
#include <format>
#include <span>

namespace license_audit {

enum class LicenseType {
    Unknown,
    Permissive,    // MIT, BSD, ISC
    Apache2,       // Apache 2.0
    WeakCopyleft,  // LGPL, MPL
    Gpl2Only,      // GPL-2.0-only
    Gpl3Plus,      // GPL-3.0+, LGPL-3.0+
    Agpl3,         // AGPL-3.0
    Proprietary    // Комерційні закриті умови
};

enum class Linkage {
    Static,
    Dynamic,
    IpcBoundary
};

struct Dependency {
    std::string name;
    std::string spdx_id;
    LicenseType type;
    Linkage linkage;
};

struct AuditViolation {
    std::string component_name;
    std::string spdx_id;
    std::string reason;
};

class ComplianceEngine {
public:
    static constexpr bool is_compatible(LicenseType target, LicenseType dep, Linkage link) noexcept {
        if (link == Linkage::IpcBoundary) {
            return true;
        }

        switch (target) {
        case LicenseType::Proprietary:
            if (dep == LicenseType::Permissive || dep == LicenseType::Apache2) {
                return true;
            }
            if (dep == LicenseType::WeakCopyleft) {
                return link == Linkage::Dynamic;
            }
            return false;

        case LicenseType::Gpl2Only:
            if (dep == LicenseType::Permissive || dep == LicenseType::Gpl2Only) {
                return true;
            }
            if (dep == LicenseType::Apache2 || dep == LicenseType::Gpl3Plus || dep == LicenseType::Agpl3) {
                return false; // Патентний конфлікт Apache 2.0 або невідповідність версій GPL
            }
            return true;

        case LicenseType::Gpl3Plus:
            if (dep == LicenseType::Permissive || dep == LicenseType::Apache2 ||
                dep == LicenseType::Gpl3Plus || dep == LicenseType::WeakCopyleft) {
                return true;
            }
            if (dep == LicenseType::Gpl2Only) {
                return false; // GPL-2.0-only без опції 'or-later' несумісна з v3
            }
            return true;

        default:
            return false;
        }
    }

    static std::expected<void, std::vector<AuditViolation>> audit(
        std::string_view project_name,
        LicenseType target_license,
        std::span<const Dependency> dependencies)
    {
        std::vector<AuditViolation> violations;
        std::cout << "[AUDIT C++] Перевірка проєкту: " << project_name << '\n';
        std::cout << "------------------------------------------------------------\n";

        for (const auto& dep : dependencies) {
            const bool compatible = is_compatible(target_license, dep.type, dep.linkage);
            const std::string_view link_str = (dep.linkage == Linkage::Static) ? "STATIC" :
                                              (dep.linkage == Linkage::Dynamic) ? "DYNAMIC (.so)" : "IPC";

            if (compatible) {
                std::cout << std::format("  [PASS] {:<15} | SPDX: {:<15} | Link: {:<12}\n",
                                         dep.name, dep.spdx_id, link_str);
            } else {
                std::cout << std::format("  [FAIL] {:<15} | SPDX: {:<15} | Link: {:<12}  <-- ЮРИДИЧНИЙ КОНФЛІКТ!\n",
                                         dep.name, dep.spdx_id, link_str);
                violations.push_back({
                    dep.name,
                    dep.spdx_id,
                    "Неприпустимий тип зв'язування або взаємна несумісність ліцензійних вимог"
                });
            }
        }

        std::cout << "------------------------------------------------------------\n";
        if (!violations.empty()) {
            return std::unexpected(violations);
        }
        return {};
    }
};

} // namespace license_audit

int main() {
    using namespace license_audit;

    const std::vector<Dependency> deps = {
        {"cJSON",       "MIT",                 LicenseType::Permissive,    Linkage::Static},
        {"mbedTLS",     "Apache-2.0",          LicenseType::Apache2,       Linkage::Static},
        {"libmodbus",   "LGPL-2.1-or-later",   LicenseType::WeakCopyleft,  Linkage::Dynamic},
        {"busybox",     "GPL-2.0-only",        LicenseType::Gpl2Only,      Linkage::IpcBoundary},
        {"libgpl_math", "GPL-2.0-only",        LicenseType::Gpl2Only,      Linkage::Static} // Порушення!
    };

    auto result = ComplianceEngine::audit("EdgeGateway-Daemon (Proprietary)", LicenseType::Proprietary, deps);

    if (!result) {
        std::cout << std::format("[ВИСНОВОК] Збірку заблоковано! Виявлено {} ліцензійних конфліктів.\n",
                                 result.error().size());
        return 1;
    }

    std::cout << "[ВИСНОВОК] Аудит пройдено успішно. Всі компоненти сумісні.\n";
    return 0;
}
```
:::

## Інженерні пастки при інтеграції аудитора в CI/CD

Під час розгортання автоматизованого ліцензійного аудиту в промислових конвеєрах інженери стикаються з чотирма типовими підводними каменями:

1. **Неявні транзитивні залежності через динамічні плагіни (`dlopen`):**
   Головний застосунок може бути зібраний виключно з дозвільними бібліотеками, проте під час завантаження стороннього модуля через `dlopen()` плагін підтягує системну бібліотеку під ліцензією `GPL-2.0-only`. Якщо плагін працює в єдиному адресному просторі з комерційним кодом і викликає спільні структури C++, за версією FSF це створює комбінований твір і інфікує весь бінарний образ.
2. **Розбіжність декларованої та фактичної ліцензії (Declared vs Concluded):**
   У маніфесті пакунка (`package.json`, `CMakeLists.txt` або `conanfile.py`) автор може вказати ліцензію `MIT`, проте всередині окремих `.c` або `.h` файлів містяться заголовки `SPDX-License-Identifier: GPL-3.0-or-later`. Автоматизовані сканери типу ScanCode або Fossology повинні виконувати пофайловий аналіз AST і текстових коментарів, а не покладатися лише на верхньорівневі декларації.
3. **Заголовкові бібліотеки та шаблони (Header-Only C++ Libraries):**
   Використання C++ шаблонів призводить до того, що машинні інструкції сторонньої бібліотеки компілюються безпосередньо в об'єктні файли `.o` застосунку. Якщо така бібліотека ліцензована під `GPL` без явного винятку (наприклад, `LLVM Exception` або `GCC Runtime Library Exception`), результуючий об'єктний код стає юридично похідним твором від копілефтної бібліотеки.
4. **Використання винятку Classpath у середовищах JVM та Native Image:**
   Бібліотеки Java часто постачаються під ліцензією `GPL-2.0 WITH Classpath-exception-2.0`. У традиційному рантаймі JVM динамічне завантаження байткоду `.jar` захищене винятком. Проте під час компіляції застосунку в монолітний нативний бінарник через GraalVM Native Image весь байткод ініціалізується та склеюється статично в один образ ELF. Інженери повинні перевіряти, чи зберігає виняток чинність для монолітних нативних AOT-образів (Ahead-of-Time).
