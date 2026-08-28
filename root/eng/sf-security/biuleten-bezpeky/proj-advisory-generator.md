# ⚙️ Складання та перевірка бюлетеня безпеки CSAF 2.0

Автоматизоване зіставлення встановленого програмного забезпечення зі стрічками безпекових бюлетенів — основа сучасного моніторингу вразливостей. Якщо системний адміністратор перевіряє тисячі серверів вручну, затримка між виходом бюлетеня та застосуванням виправлення вимірюється днями. Програма автоматичної перевірки повинна розібрати машинночитний документ бюлетеня, перевірити криптографічний підпис, зіставити версію локального пакета з оголошеними діапазонами та видати точний висновок: чи вразлива система, який рівень небезпеки за шкалою CVSS та який тимчасовий захід (workaround) необхідно застосувати, якщо негайний перезапуск сервісу неможливий.

Головна технічна складність полягає в надійному зіставленні версій. Лексикографічне порівняння рядків призводить до катастрофічних помилок: рядок `"2.10.0"` лексично менший за `"2.2.0"`, хоча версія `2.10.0` є значно новішою. Програма зобов'язана розбирати компоненти версії на числові складові (Major, Minor, Patch) за стандартом семантичного версіонування SemVer та коректно обробляти включні й виключні межі вразливих інтервалів.

Нижче наведено робочу реалізацію парсера та верифікатора бюлетенів безпеки. Програма аналізує структуру вразливості, порівнює версії з урахуванням семантичного версіонування та формує інженерний звіт про необхідні дії.

## Реалізація зіставлення версій та аналізу бюлетеня

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>

typedef struct {
    int major;
    int minor;
    int patch;
} SemVer;

typedef enum {
    REMEDIATION_VENDOR_FIX = 0,
    REMEDIATION_WORKAROUND = 1,
    REMEDIATION_MITIGATION = 2
} RemediationType;

typedef struct {
    RemediationType type;
    char details[256];
    char fixed_version[32];
} Remediation;

typedef struct {
    char cve_id[32];
    char cwe_id[32];
    double cvss_base_score;
    char cvss_vector[96];
    SemVer min_affected;
    SemVer max_affected;
    Remediation remediation;
} SecurityAdvisory;

bool parse_semver(const char* str, SemVer* out) {
    if (!str || !out) return false;
    return sscanf(str, "%d.%d.%d", &out->major, &out->minor, &out->patch) == 3;
}

int compare_semver(const SemVer* a, const SemVer* b) {
    if (a->major != b->major) return a->major - b->major;
    if (a->minor != b->minor) return a->minor - b->minor;
    return a->patch - b->patch;
}

bool is_version_vulnerable(const SemVer* current, const SemVer* min_aff, const SemVer* max_aff) {
    if (!current || !min_aff || !max_aff) return false;
    return (compare_semver(current, min_aff) >= 0 && compare_semver(current, max_aff) <= 0);
}

void evaluate_advisory(const SecurityAdvisory* adv, const char* installed_ver_str) {
    SemVer installed;
    if (!parse_semver(installed_ver_str, &installed)) {
        fprintf(stderr, "Помилка: некоректний формат версії встановленого пакета: %s\n", installed_ver_str);
        return;
    }

    printf("=== Аналіз бюлетеня: %s ===\n", adv->cve_id);
    printf("Клас дефекту: %s | CVSS: %.1f [%s]\n", adv->cwe_id, adv->cvss_base_score, adv->cvss_vector);
    printf("Перевірка версії: %s\n", installed_ver_str);

    if (is_version_vulnerable(&installed, &adv->min_affected, &adv->max_affected)) {
        printf("[УВАГА] Система ВРАЗЛИВА! Встановлена версія підпадає під дію загрози.\n");
        if (adv->remediation.type == REMEDIATION_VENDOR_FIX) {
            printf("Рекомендована дія: Оновити пакет до версії >= %s\n", adv->remediation.fixed_version);
            printf("Деталі: %s\n", adv->remediation.details);
        } else if (adv->remediation.type == REMEDIATION_WORKAROUND) {
            printf("Рекомендована дія: Застосувати тимчасовий захід (Workaround)\n");
            printf("Інструкція: %s\n", adv->remediation.details);
        }
    } else {
        printf("[OK] Встановлена версія безпечна (не зачеплена цією вадою).\n");
    }
    printf("\n");
}

int main(void) {
    SecurityAdvisory adv = {
        .cve_id = "CVE-2024-38856",
        .cwe_id = "CWE-787",
        .cvss_base_score = 9.8,
        .cvss_vector = "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H",
        .min_affected = { .major = 2, .minor = 1, .patch = 0 },
        .max_affected = { .major = 2, .minor = 4, .patch = 3 },
        .remediation = {
            .type = REMEDIATION_VENDOR_FIX,
            .fixed_version = "2.4.4",
            .details = "Встановіть оновлений пакет з репозиторію безпеки або вимкніть TLS-сесії."
        }
    };

    evaluate_advisory(&adv, "2.4.1");
    evaluate_advisory(&adv, "2.4.4");
    evaluate_advisory(&adv, "2.0.9");

    return 0;
}
```
```cpp
#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <optional>
#include <sstream>

struct SemVer {
    int major = 0;
    int minor = 0;
    int patch = 0;

    auto operator<=>(const SemVer&) const = default;

    static std::optional<SemVer> parse(std::string_view str) {
        SemVer v;
        char dot1 = 0, dot2 = 0;
        std::stringstream ss{std::string(str)};
        if ((ss >> v.major >> dot1 >> v.minor >> dot2 >> v.patch) && dot1 == '.' && dot2 == '.') {
            return v;
        }
        return std::nullopt;
    }
};

enum class RemediationType {
    VendorFix,
    Workaround,
    Mitigation
};

struct Remediation {
    RemediationType type;
    std::string details;
    std::string fixed_version;
};

struct SecurityAdvisory {
    std::string cve_id;
    std::string cwe_id;
    double cvss_base_score = 0.0;
    std::string cvss_vector;
    SemVer min_affected;
    SemVer max_affected;
    Remediation remediation;

    [[nodiscard]] bool is_vulnerable(const SemVer& current) const noexcept {
        return (current >= min_affected && current <= max_affected);
    }
};

class AdvisoryEvaluator {
public:
    static void evaluate(const SecurityAdvisory& adv, std::string_view installed_ver_str) {
        const auto installed = SemVer::parse(installed_ver_str);
        if (!installed) {
            std::cerr << "Помилка: некоректний формат версії: " << installed_ver_str << "\n";
            return;
        }

        std::cout << "=== Аналіз бюлетеня: " << adv.cve_id << " ===\n";
        std::cout << "Клас дефекту: " << adv.cwe_id << " | CVSS: " << adv.cvss_base_score 
                  << " [" << adv.cvss_vector << "]\n";
        std::cout << "Перевірка версії: " << installed_ver_str << "\n";

        if (adv.is_vulnerable(*installed)) {
            std::cout << "[УВАГА] Система ВРАЗЛИВА! Встановлена версія підпадає під дію загрози.\n";
            if (adv.remediation.type == RemediationType::VendorFix) {
                std::cout << "Рекомендована дія: Оновити пакет до версії >= " << adv.remediation.fixed_version << "\n";
                std::cout << "Деталі: " << adv.remediation.details << "\n";
            } else if (adv.remediation.type == RemediationType::Workaround) {
                std::cout << "Рекомендована дія: Застосувати тимчасовий захід (Workaround)\n";
                std::cout << "Інструкція: " << adv.remediation.details << "\n";
            }
        } else {
            std::cout << "[OK] Встановлена версія безпечна (не зачеплена цією вадою).\n";
        }
        std::cout << "\n";
    }
};

int main() {
    const SecurityAdvisory adv{
        .cve_id = "CVE-2024-38856",
        .cwe_id = "CWE-787",
        .cvss_base_score = 9.8,
        .cvss_vector = "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H",
        .min_affected = SemVer{2, 1, 0},
        .max_affected = SemVer{2, 4, 3},
        .remediation = Remediation{
            .type = RemediationType::VendorFix,
            .details = "Встановіть оновлений пакет з репозиторію безпеки або вимкніть TLS-сесії.",
            .fixed_version = "2.4.4"
        }
    };

    AdvisoryEvaluator::evaluate(adv, "2.4.1");
    AdvisoryEvaluator::evaluate(adv, "2.4.4");
    AdvisoryEvaluator::evaluate(adv, "2.0.9");

    return 0;
}
```
:::

## Архітектурний розбір реалізації

Реалізація демонструє два принципові підходи до організації системних обчислень:

1. **У версії на мові C** застосовано концепцію нульового динамічного виділення пам'яті (Zero Heap Allocation). Усі структури даних мають фіксовані розміри буферів, а парсинг версій виконується через пряме зчитування цілих чисел у `sscanf()`. Функція `compare_semver()` реалізує класичну трихотомію: спочатку порівнюються мажорні версії, за їхньої рівності — мінорні, і в останню чергу — номери патчів. Цей підхід ідеально підходить для низькорівневих агентів безпеки, які функціонують у середовищі вбудованих Linux-шлюзів, де фрагментація оперативної пам'яті неприпустима.
2. **У версії на C++20** архітектура спирається на сучасні виразні засоби мови: тристоронній оператор порівняння `operator<=>` (Spaceship Operator), який компілятор автоматично транслює у повний набір відношень порядку (`<`, `<=`, `>`, `>=`), строгі перерахування `enum class`, що виключають неявне приведення типів, тип `std::optional` для безпечного повернення результату парсингу без винятків та `std::string_view` для роботи з рядковими зрізами без алокацій у купі.

## Обробка складних діапазонів та бекпортованих патчів

У виробничих середовищах вразливість рідко описується єдиним неперервним інтервалом. Реальні безпекові бюлетені містять об'єднання кількох незв'язних діапазонів, що відповідають різним гілкам підтримки (LTS-релізам). Наприклад, дефект може зачіпати версії від `1.2.0` до `1.2.8` у старій гілці та від `2.0.0` до `2.4.3` у поточній.

Окрему інженерну проблему становлять дистрибутивні бекпорти (Backported Fixes). Команди супроводу операційних систем корпоративного рівня (Debian, Red Hat, Ubuntu) рідко оновлюють мажорну версію пакета, щоб не порушити бінарну сумісність ABI. Замість переходу з версії `2.4.1` на `2.4.4` вони переносять ізольований патч у вихідний код версії `2.4.1`, формуючи реліз виду `2.4.1-1ubuntu4.2`.

Для коректного аналізу таких систем наївного порівняння SemVer недостатньо:
- Програма повинна звертатися до дистрибутивного дерева продуктів CSAF (`product_tree`), де вказано точний рядок збірки операційної системи.
- Якщо бюлетень випущено апстрім-розробником (Upstream Vendor), а в системі використовується пакет із дистрибутивного репозиторію, локальний сканер зобов'язаний зіставляти не номер версії програми, а номер випуску дистрибутивного пакета через аналіз бази даних DPKG або RPM.

## Інженерні пастки під час аналізу бюлетенів

Під час розробки автоматизованих парсерів та генераторів бюлетенів безпеки виникають чотири типові помилки:

1. **Нелінійні схеми версіонування (Non-SemVer versions).** Багато системних пакетів використовують дату або специфічні суфікси дистрибутива (наприклад, `1.2.3-1ubuntu4.2` або `2024.1b`). Наївне розбиття рядка за крапками призводить до помилкового визначення вразливості. Для таких пакетів необхідно застосовувати нормалізовані парсери екосистем (DPKG, RPM або Package URL).
2. **Неврахування пререлізних збірок (Pre-release tags).** Версія `2.4.4-rc1` у стандарті SemVer є меншою за `2.4.4`. Якщо вразливість виправлена лише у фінальному релізі `2.4.4`, кандидати на реліз залишаються вразливими і не повинні пропускатися сканером.
3. **Хибне відчуття безпеки через неповний Workaround.** Якщо бюлетень пропонує тимчасовий захід (наприклад, блокування певного заголовка на рівні зворотної проксі), автоматика не повинна позначати проблему як остаточно вирішену (`fixed`). Стан повинен мати статус `mitigated` з обов'язковим нагадуванням про необхідність встановлення повноцінного бінарного патча під час наступного регламентного вікна обслуговування.
4. **Ігнорування контрольних сум та підписів.** Завантаження оновлень за посиланням з бюлетеня без автоматичної звірки гешу SHA-256 та перевірки підпису OpenPGP відкриває можливість атаки типу «людина посередині» (MitM) на етапі доставки виправлення.

## Інтеграція у виробничий конвеєр

У реальній інфраструктурі такий модуль верифікації вбудовується як крок попередньої перевірки у пайплайн розгортання:
- Перед викачуванням нової версії контейнера у виробниче середовище агент завантажує актуальний CSAF-фід вендора за адресою `.well-known/csaf/provider-metadata.json`.
- Перевіряється цифровий підпис OpenPGP отриманого JSON-файлу.
- Зіставляється локальна специфікація SBOM зі списком `known_affected`.
- Якщо виявлено критичну вразливість без готового `vendor_fix`, автоматично активується модуль ін'єкції `workaround` у конфігураційні файли (наприклад, через Ansible або Kubernetes ConfigMaps).
- У разі успішного застосування бінарного виправлення статус оновлюється на `fixed`, а подія фіксується у захищеному журналі аудиту.
