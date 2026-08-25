# ⚙️ Реалізація конвеєра токенізації та динамічного маскування на C та C++

Обробка чутливих структур даних у високопродуктивних сервісах (брокерах повідомлень Kafka, шлюзах API та потокових процесорах ETL) вимагає розділення полів за таксономією приватності безпосередньо в оперативній пам'яті до їх запису в персистентне сховище або передачі зовнішнім споживачам.

Якщо обробка приватності реалізується на рівні важких високорівневих фреймворків із динамічною типізацією, постійне копіювання рядків та алокації в купі спричиняють значну деградацію пропускної здатності та ризик витоку сирих даних через зліпки пам'яті (Core Dumps). Низькорівневий конвеєр на C та C++ розв'язує цю задачу за фіксований час без динамічних алокацій на гарячому шляху виконання.

## Архітектурні компоненти конвеєра

Конвеєр виконує три операції над кожним полем запису:
1. **Детермінована токенізація (Pseudonymization):** обчислення стійкого криптографічного токена через геш-функцію з секретною сіллю (HMAC-SHA256). Це дозволяє зберегти можливість реляційного зведення (`JOIN`) та групування в аналітичних сховищах без розкриття вихідного PII.
2. **Динамічне маскування (Dynamic Data Masking, DDM):** трансформація рядка під час читання залежно від контексту безпеки запитувача (`ADMIN`, `ANALYST`, `AUDITOR`).
3. **Бакетізація та генералізація (Bucketing):** перетворення неперервних квазі-ідентифікаторів (віку, координат, поштових індексів) у дискретні діапазони для збереження `k`-анонімності вибірки.

Нижче наведено робочу реалізацію ядра класифікації та трансформації полів для потокового конвеєра даних на мовах C та C++.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <stdbool.h>

#define MAX_FIELD_LEN 128
#define TOKEN_HEX_LEN 65

typedef enum {
    ROLE_ADMIN,
    ROLE_ANALYST,
    ROLE_AUDITOR
} UserRole;

typedef enum {
    CLASS_PUBLIC,
    CLASS_DIRECT_PII,
    CLASS_QUASI_ID,
    CLASS_SENSITIVE
} DataClassification;

typedef struct {
    char raw_email[MAX_FIELD_LEN];
    char raw_card[MAX_FIELD_LEN];
    uint32_t age;
    char raw_zip[16];
    char diagnosis[MAX_FIELD_LEN];
} UserRecord;

typedef struct {
    char email_display[MAX_FIELD_LEN];
    char card_display[MAX_FIELD_LEN];
    char age_display[32];
    char zip_display[16];
    char diagnosis_display[MAX_FIELD_LEN];
} TransformedRecord;

/* Спрощена реалізація FNV-1a з сіллю для детермінованого HMAC-подібного токена */
static void generate_pseudonym_token(const char *input, const char *salt, char *out_hex) {
    uint64_t hash = 0xcbf29ce484222325ULL;
    const uint64_t prime = 0x100000001b3ULL;
    
    for (const char *p = salt; *p; p++) {
        hash ^= (uint64_t)(unsigned char)(*p);
        hash *= prime;
    }
    for (const char *p = input; *p; p++) {
        hash ^= (uint64_t)(unsigned char)(*p);
        hash *= prime;
    }
    snprintf(out_hex, TOKEN_HEX_LEN, "tok_%016llx", (unsigned long long)hash);
}

/* Маскування email: user.name@domain.com -> u***e@domain.com */
static void mask_email(const char *src, char *dst, size_t dst_size) {
    const char *at = strchr(src, '@');
    if (!at || at == src) {
        snprintf(dst, dst_size, "******");
        return;
    }
    size_t local_len = (size_t)(at - src);
    if (local_len <= 2) {
        snprintf(dst, dst_size, "*%s", at);
    } else {
        snprintf(dst, dst_size, "%c***%c%s", src[0], src[local_len - 1], at);
    }
}

/* Маскування картки: 4111222233334444 -> ****-****-****-4444 */
static void mask_card(const char *src, char *dst, size_t dst_size) {
    size_t len = strlen(src);
    if (len < 4) {
        snprintf(dst, dst_size, "****");
        return;
    }
    snprintf(dst, dst_size, "****-****-****-%s", src + len - 4);
}

/* Генералізація віку в діапазони k-анонімності */
static void bucket_age(uint32_t age, char *dst, size_t dst_size) {
    uint32_t lower = (age / 10) * 10;
    uint32_t upper = lower + 9;
    snprintf(dst, dst_size, "%u–%u", lower, upper);
}

/* Генералізація індексу: 02138 -> 021** */
static void bucket_zip(const char *src, char *dst, size_t dst_size) {
    size_t len = strlen(src);
    if (len <= 2) {
        snprintf(dst, dst_size, "***");
    } else {
        snprintf(dst, dst_size, "%.3s**", src);
    }
}

void transform_record(const UserRecord *in, UserRole role, const char *salt, TransformedRecord *out) {
    if (role == ROLE_ADMIN) {
        /* Адміністратор: повний прямий доступ для обслуговування */
        strncpy(out->email_display, in->raw_email, sizeof(out->email_display) - 1);
        strncpy(out->card_display, in->raw_card, sizeof(out->card_display) - 1);
        snprintf(out->age_display, sizeof(out->age_display), "%u", in->age);
        strncpy(out->zip_display, in->raw_zip, sizeof(out->zip_display) - 1);
        strncpy(out->diagnosis_display, in->diagnosis, sizeof(out->diagnosis_display) - 1);
    } else if (role == ROLE_ANALYST) {
        /* Аналітик: динамічне маскування PII + генералізація квазі-ID */
        mask_email(in->raw_email, out->email_display, sizeof(out->email_display));
        mask_card(in->raw_card, out->card_display, sizeof(out->card_display));
        bucket_age(in->age, out->age_display, sizeof(out->age_display));
        bucket_zip(in->raw_zip, out->zip_display, sizeof(out->zip_display));
        strncpy(out->diagnosis_display, in->diagnosis, sizeof(out->diagnosis_display) - 1);
    } else {
        /* Аудитор: детерміновані псевдоніми та супресія чутливих станів */
        generate_pseudonym_token(in->raw_email, salt, out->email_display);
        generate_pseudonym_token(in->raw_card, salt, out->card_display);
        snprintf(out->age_display, sizeof(out->age_display), "[SUPPRESSED]");
        bucket_zip(in->raw_zip, out->zip_display, sizeof(out->zip_display));
        snprintf(out->diagnosis_display, sizeof(out->diagnosis_display), "[PROTECTED]");
    }
}

int main(void) {
    UserRecord user = {
        .raw_email = "william.weld@mass.gov",
        .raw_card = "4111555588880213",
        .age = 48,
        .raw_zip = "02138",
        .diagnosis = "Type-2 Diabetes"
    };
    const char *secret_salt = "k9_vault_pepper_2026";
    TransformedRecord result;

    printf("=== РОЛЬ: ANALYST ===\n");
    transform_record(&user, ROLE_ANALYST, secret_salt, &result);
    printf("Email: %s\nCard:  %s\nAge:   %s\nZIP:   %s\nDiag:  %s\n\n",
           result.email_display, result.card_display, result.age_display,
           result.zip_display, result.diagnosis_display);

    printf("=== РОЛЬ: AUDITOR ===\n");
    transform_record(&user, ROLE_AUDITOR, secret_salt, &result);
    printf("Email: %s\nCard:  %s\nAge:   %s\nZIP:   %s\nDiag:  %s\n",
           result.email_display, result.card_display, result.age_display,
           result.zip_display, result.diagnosis_display);

    return 0;
}
```
```cpp
#include <iostream>
#include <string>
#include <string_view>
#include <format>
#include <sstream>
#include <cstdint>

enum class UserRole {
    Admin,
    Analyst,
    Auditor
};

enum class DataClassification {
    Public,
    DirectPii,
    QuasiIdentifier,
    Sensitive
};

struct UserRecord {
    std::string email;
    std::string card_number;
    uint32_t age{};
    std::string zip_code;
    std::string diagnosis;
};

struct TransformedRecord {
    std::string email;
    std::string card_number;
    std::string age;
    std::string zip_code;
    std::string diagnosis;
};

class PrivacyEngine {
public:
    explicit PrivacyEngine(std::string_view salt) : salt_(salt) {}

    [[nodiscard]] std::string tokenize(std::string_view input) const {
        uint64_t hash = 0xcbf29ce484222325ULL;
        constexpr uint64_t prime = 0x100000001b3ULL;

        for (char c : salt_) {
            hash ^= static_cast<uint64_t>(static_cast<unsigned char>(c));
            hash *= prime;
        }
        for (char c : input) {
            hash ^= static_cast<uint64_t>(static_cast<unsigned char>(c));
            hash *= prime;
        }
        std::stringstream ss;
        ss << "tok_" << std::hex << hash;
        return ss.str();
    }

    [[nodiscard]] static std::string mask_email(std::string_view email) {
        const auto at_pos = email.find('@');
        if (at_pos == std::string_view::npos || at_pos == 0) {
            return "******";
        }
        if (at_pos <= 2) {
            return std::string("*") + std::string(email.substr(at_pos));
        }
        return std::string(1, email.front()) + "***" + 
               std::string(1, email[at_pos - 1]) + 
               std::string(email.substr(at_pos));
    }

    [[nodiscard]] static std::string mask_card(std::string_view card) {
        if (card.length() < 4) {
            return "****";
        }
        return "****-****-****-" + std::string(card.substr(card.length() - 4));
    }

    [[nodiscard]] static std::string bucket_age(uint32_t age) {
        const uint32_t lower = (age / 10) * 10;
        const uint32_t upper = lower + 9;
        return std::to_string(lower) + "–" + std::to_string(upper);
    }

    [[nodiscard]] static std::string bucket_zip(std::string_view zip) {
        if (zip.length() <= 2) {
            return "***";
        }
        return std::string(zip.substr(0, 3)) + "**";
    }

    [[nodiscard]] TransformedRecord process(const UserRecord& in, UserRole role) const {
        TransformedRecord out;
        switch (role) {
            case UserRole::Admin:
                out.email = in.email;
                out.card_number = in.card_number;
                out.age = std::to_string(in.age);
                out.zip_code = in.zip_code;
                out.diagnosis = in.diagnosis;
                break;

            case UserRole::Analyst:
                out.email = mask_email(in.email);
                out.card_number = mask_card(in.card_number);
                out.age = bucket_age(in.age);
                out.zip_code = bucket_zip(in.zip_code);
                out.diagnosis = in.diagnosis;
                break;

            case UserRole::Auditor:
                out.email = tokenize(in.email);
                out.card_number = tokenize(in.card_number);
                out.age = "[SUPPRESSED]";
                out.zip_code = bucket_zip(in.zip_code);
                out.diagnosis = "[PROTECTED]";
                break;
        }
        return out;
    }

private:
    std::string salt_;
};

int main() {
    const UserRecord user{
        .email = "william.weld@mass.gov",
        .card_number = "4111555588880213",
        .age = 48,
        .zip_code = "02138",
        .diagnosis = "Type-2 Diabetes"
    };

    const PrivacyEngine engine("k9_vault_pepper_2026");

    const auto analyst_view = engine.process(user, UserRole::Analyst);
    std::cout << "=== РОЛЬ: ANALYST ===\n"
              << "Email: " << analyst_view.email << "\n"
              << "Card:  " << analyst_view.card_number << "\n"
              << "Age:   " << analyst_view.age << "\n"
              << "ZIP:   " << analyst_view.zip_code << "\n"
              << "Diag:  " << analyst_view.diagnosis << "\n\n";

    const auto auditor_view = engine.process(user, UserRole::Auditor);
    std::cout << "=== РОЛЬ: AUDITOR ===\n"
              << "Email: " << auditor_view.email << "\n"
              << "Card:  " << auditor_view.card_number << "\n"
              << "Age:   " << auditor_view.age << "\n"
              << "ZIP:   " << auditor_view.zip_code << "\n"
              << "Diag:  " << auditor_view.diagnosis << "\n";

    return 0;
}
```
:::

## Інженерний аналіз та пастки практичної експлуатації

При інтеграції конвеєра трансформації чутливих полів у реальні сервіси необхідно враховувати шість критичних інженерних факторів:

### 1. Витік через варіативність довжини (Length-based Information Leakage)
Якщо під час маскування або токенізації довжина результату корелює з довжиною вхідного значення, зловмисник може звузити простір пошуку. Наприклад, рідкісні діагнози або унікальні прізвища мають специфічну довжину символів. Якщо маскування залишає кількість зірочок рівною довжині вихідного імені, ентропія захисту суттєво деградує. Токенізатор повинен завжди генерувати результат фіксованої довжини блоку (Fixed-width Hex Digest), незалежно від розміру вхідного PII.

### 2. Керування перцем, сіллю та періодична ротація (Pepper & Key Lifecycle)
Детермінована токенізація без використання секретного системного перцю (`pepper`) є вразливою до атак за попередньо скомпільованими словниками та райдужними таблицями (Rainbow Tables). Для доменів із невеликою кількістю комбінацій (наприклад, 10-значні номери мобільних телефонів мають простір усього `10⁷–10⁹` значень) зловмисник може згенерувати повну таблицю хешів за кілька хвилин.

Секретний перець повинен відповідати наступним інженерним вимогам:
- Зберігатися виключно в ізольованому менеджері секретів або апаратному модулі безпеки (Hardware Security Module, HSM).
- Ніколи не записуватися в таблиці бази даних поруч із токенами.
- Підтримувати двоетапну схему ротації: при переході на нову версію перцю (`Pepper_v2`) конвеєр підтримує верифікацію за `Pepper_v1` під час пільгового періоду міграції даних.

### 3. Гарантоване очищення оперативної пам'яті (Memory Sanitization)
Після обробки запису `UserRecord` буфери, що містили відкритий текст (номери карток, адреси email), повинні негайно занулятися. Звичайний виклик `memset()` може бути оптимізований і викинутий компілятором як «мертвий код» (Dead Store Elimination), якщо після цього буфер більше не читається.

Для гарантованого занулення пам'яті необхідно застосовувати бар'єри пам'яті:
- У стандарті C: функція `explicit_bzero()` (або `memset_s` з ISO C11 Annex K).
- У C++: створення захищених контейнерів-обгорток (Secure Allocator), чий деструктор використовує `volatile`-покажчики для гарантованого стирання байтів перед поверненням пам'яті в пул.

### 4. Продуктивність та багатопотоковість (Concurrency & Lock-Free Caching)
Операція обчислення HMAC-SHA256 займає в середньому `120–250` наносекунд на одне поле на сучасному процесорі x86_64 із підтримкою векторних інструкцій SHA-NI. Для потоку в `100 000` подій на секунду накладні витрати на токенізацію кількох полів становлять лише кілька мілісекунд сумарного процесорного часу одного ядра.

У багатопотокових сервісах повторне обчислення токенів для частих клієнтів створює зайве навантаження. Для усунення затримок використовують безблокувальний (lock-free) LRU-кеш токенів із шардуванням за атомарними лічильниками, що знижує час відповіді до менш ніж `15` наносекунд на запит при 95% попадань у кеш.

### 5. Детермінована токенізація проти токенізації зі сховищем (Vault-based Tradeoff)
Вибір між HMAC-псевдонімізацією та сховищем випадкових UUID визначається профілем навантаження:
- Детермінований HMAC не потребує централізованої бази даних стану (State-free), легко масштабується горизонтально на сотні вузлів, але потенційно відкритий до частотного аналізу у великих вибірках.
- Сховище токенів (Token Vault) забезпечує повний захист від частотного аналізу, але створює вузьке горло при масовому паралельному записі (Distributed Key-Value bottleneck).

### 6. Захист від атак підробки та вибірки за шаблоном
Якщо клієнтський додаток передає частково масковане значення назад на сервер під час операції оновлення профілю (наприклад, надсилає рядок `al***@cyber.ua`), серверний валідатор повинен відхиляти такі запити або розпізнавати маску як незмінний маркер. Інакше виникає ризик випадкового перезапису реального ідентифікатора маскованим літералом у базі даних.
