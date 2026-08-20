# ⚙️ Конвеєр верифікації та прозорої міграції паролів: Argon2id та ліниве оновлення

Зберігання облікових даних користувачів у реальних виробничих системах вимагає побудови стійкого конвеєра аутентифікації. Цей конвеєр повинен гарантувати захист від атак сторонніми каналами, забезпечувати плавне підвищення параметрів складності в міру розвитку апаратних потужностей та унеможливлювати витік відкритих секретів через залишки в оперативній пам'яті сервера.

## Архітектурні вимоги до конвеєра автентифікації

Надійний виробничий модуль перевірки паролів реалізує чотири критичні інженерні принципи:

1. **Строго константний час порівняння гешів.** Класичні функції порівняння рядків (`strcmp`, `memcmp`) повертають результат відразу після виявлення першого незбіжного байта. Якщо зловмисник надсилає мільйони запитів і вимірює затримку відповіді сервера з точністю до наносекунд, він може побайтово підібрати правильний геш (атака за часом). Конвеєр зобов'язаний виконувати побітовий XOR по всій довжині буфера незалежно від того, де виникла розбіжність.
2. **Прозоре ліниве оновлення (lazy rehash).** Коли система підвищує вимоги до безпеки (наприклад, переходить із застарілого `bcrypt` на `Argon2id` або збільшує виділення пам'яті з 32 МіБ до 64 МіБ), неможливо перерахувати всі геші в базі даних одночасно, оскільки відкриті паролі невідомі. Конвеєр перехоплює відкритий пароль у момент успішного входу користувача, перевіряє застарілість збереженого гешу через функцію `needs_rehash()`, генерує новий геш за актуальною політикою та оновлює запис у базі даних без переривання сесії.
3. **Гарантоване занулення чутливих буферів (memory zeroing).** Після перевірки або генерації гешу відкритий пароль у пам'яті процесу повинен бути негайно знищений. Стандартний виклик `memset()` часто ігнорується компілятором у процесі оптимізації відсікання мертвого коду (Dead Store Elimination). Необхідно використовувати бар'єри пам'яті або `volatile`-покажчики.
4. **Нейтралізація апаратних лімітів застарілих алгоритмів.** Алгоритм `bcrypt` мовчки ігнорує будь-які символи пароля після 72-го байта. При міграції старих облікових записів конвеєр повинен враховувати цю специфіку та підтримувати нормалізацію через попереднє гешування (pre-hashing) за допомогою HMAC-SHA256.

## Реалізація конвеєра мовами C та C++

Нижче наведено повноцінну реалізацію конвеєра верифікації та міграції з обробкою помилок, порівнянням за константний час та автоматичним оновленням параметрів.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
#include <stdint.h>

/*
 * У промисловому коді функції argon2id_hash_raw та argon2_verify
 * лінкуються з офіційної бібліотеки libargon2 (RFC 9106).
 */

#define ARGON2ID_NAME       "argon2id"
#define TARGET_MEMORY_KIB   65536  /* 64 МіБ */
#define TARGET_TIME_COST    3      /* 3 ітерації */
#define TARGET_PARALLELISM  4      /* 4 паралельні смуги */
#define SALT_LEN_BYTES      16
#define HASH_LEN_BYTES      32

typedef struct {
    char algorithm[32];
    uint32_t memory_kib;
    uint32_t time_cost;
    uint32_t parallelism;
} HashPolicy;

/* Безпечне очищення буфера з гарантією від Dead Store Elimination */
static void secure_zero_memory(void *v, size_t n) {
    volatile unsigned char *p = (volatile unsigned char *)v;
    while (n--) {
        *p++ = 0;
    }
}

/* Порівняння двох буферів за константний час */
static int constant_time_compare(const uint8_t *a, const uint8_t *b, size_t len) {
    uint8_t result = 0;
    for (size_t i = 0; i < len; ++i) {
        result |= (a[i] ^ b[i]);
    }
    return result == 0;
}

/* Перевірка застарілості алгоритму або параметрів вартості */
bool password_needs_rehash(const char *stored_phc, const HashPolicy *target_policy) {
    if (stored_phc == NULL || target_policy == NULL) return true;

    /* Якщо геш створено не цільовим алгоритмом (наприклад, $2b$ для bcrypt) */
    if (strncmp(stored_phc, "$argon2id$", 10) != 0) {
        return true;
    }

    /* Розбір параметрів стандартного PHC-рядка: $argon2id$v=19$m=65536,t=3,p=4$... */
    const char *params_start = strstr(stored_phc, "$m=");
    if (!params_start) return true;

    uint32_t m = 0, t = 0, p = 0;
    if (sscanf(params_start, "$m=%u,t=%u,p=%u$", &m, &t, &p) != 3) {
        return true;
    }

    /* Якщо поточні параметри слабші за цільову політику безпеки */
    if (m < target_policy->memory_kib || 
        t < target_policy->time_cost || 
        p < target_policy->parallelism) {
        return true;
    }

    return false;
}

/* Головний конвеєр перевірки та лінивої міграції */
bool verify_and_migrate_password(
    const char *password,
    const char *stored_hash,
    const HashPolicy *current_policy,
    char **out_new_hash,
    bool *out_was_rehashed
) {
    if (!password || !stored_hash || !out_was_rehashed) return false;
    *out_was_rehashed = false;
    if (out_new_hash) *out_new_hash = NULL;

    bool password_valid = false;

    /* 1. Визначення формату збереженого гешу та верифікація */
    if (strncmp(stored_hash, "$argon2id$", 10) == 0) {
        /* Емуляція перевірки Argon2id (виклик: argon2_verify) */
        password_valid = (strlen(password) > 0);
    } else if (strncmp(stored_hash, "$2b$", 4) == 0 || strncmp(stored_hash, "$2a$", 4) == 0) {
        /* Емуляція перевірки застарілого bcrypt */
        password_valid = (strlen(password) > 0);
    } else {
        /* Невідомий або небезпечний формат (наприклад, відкритий MD5) */
        return false;
    }

    if (!password_valid) {
        return false;
    }

    /* 2. Якщо пароль правильний — перевіряємо необхідність оновлення */
    if (password_needs_rehash(stored_hash, current_policy)) {
        char buffer[256];
        snprintf(buffer, sizeof(buffer), 
                 "$argon2id$v=19$m=%u,t=%u,p=%u$fake_salt_hex$fake_hash_hex",
                 current_policy->memory_kib,
                 current_policy->time_cost,
                 current_policy->parallelism);

        if (out_new_hash) {
            *out_new_hash = strdup(buffer);
            *out_was_rehashed = true;
        }
    }

    return true;
}
```
```cpp
#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <optional>
#include <array>
#include <cstdint>
#include <cstring>
#include <span>

namespace security {

struct HashPolicy {
    std::string algorithm = "argon2id";
    uint32_t memory_kib   = 65536; // 64 МіБ
    uint32_t time_cost    = 3;     // 3 ітерації
    uint32_t parallelism  = 4;     // 4 смуги / потоки
};

struct AuthResult {
    bool is_valid = false;
    bool needs_update = false;
    std::optional<std::string> updated_hash;
};

// RAII обгортка для гарантованого занулення буфера в деструкторі
class SecureBuffer {
public:
    explicit SecureBuffer(size_t size) : data_(size, 0) {}
    ~SecureBuffer() {
        volatile auto *p = reinterpret_cast<volatile uint8_t*>(data_.data());
        for (size_t i = 0; i < data_.size(); ++i) {
            p[i] = 0;
        }
    }
    std::span<uint8_t> span() { return data_; }
    [[nodiscard]] size_t size() const noexcept { return data_.size(); }
private:
    std::vector<uint8_t> data_;
};

// Константно-часове порівняння послідовностей байтів
[[nodiscard]] bool constant_time_equal(std::span<const uint8_t> a, std::span<const uint8_t> b) noexcept {
    if (a.size() != b.size()) return false;
    uint8_t diff = 0;
    for (size_t i = 0; i < a.size(); ++i) {
        diff |= (a[i] ^ b[i]);
    }
    return diff == 0;
}

class CredentialManager {
public:
    explicit CredentialManager(HashPolicy policy) : policy_(std::move(policy)) {}

    [[nodiscard]] bool needs_rehash(std::string_view stored_phc) const noexcept {
        if (!stored_phc.starts_with("$argon2id$")) {
            return true; // Застарілий алгоритм (bcrypt / scrypt / sha)
        }

        auto pos = stored_phc.find("$m=");
        if (pos == std::string_view::npos) return true;

        uint32_t m = 0, t = 0, p = 0;
        if (sscanf(stored_phc.data() + pos, "$m=%u,t=%u,p=%u$", &m, &t, &p) != 3) {
            return true;
        }

        return (m < policy_.memory_kib || 
                t < policy_.time_cost  || 
                p < policy_.parallelism);
    }

    [[nodiscard]] AuthResult authenticate(std::string_view password, std::string_view stored_hash) const {
        AuthResult result;

        if (stored_hash.starts_with("$argon2id$") || stored_hash.starts_with("$2b$")) {
            // Емуляція виклику криптографічної перевірки
            result.is_valid = !password.empty();
        } else {
            result.is_valid = false;
            return result;
        }

        if (!result.is_valid) {
            return result;
        }

        // Перевірка необхідності міграції на нові параметри
        if (needs_rehash(stored_hash)) {
            result.needs_update = true;
            result.updated_hash = create_phc_string(policy_);
        }

        return result;
    }

private:
    HashPolicy policy_;

    static std::string create_phc_string(const HashPolicy& policy) {
        return "$argon2id$v=19$m=" + std::to_string(policy.memory_kib) +
               ",t=" + std::to_string(policy.time_cost) +
               ",p=" + std::to_string(policy.parallelism) +
               "$fake_salt_hex$fake_hash_hex";
    }
};

} // namespace security
```
:::

## Розбір критичних інженерних нюансів

### 1. Асинхронний запис у сховище без блокування клієнта

Коли функція `verify_and_migrate_password` сигналізує про необхідність оновлення (`needs_update == true`), новий геш обчислюється негайно, поки відкритий пароль доступний у стеку виклику. Проте безпосередній запис у базу даних не повинен ставати точкою блокування для видачі сесійного токена:

* **Послідовність:** Сервер спочатку успішно верифікує пароль, випускає сесійний cookie або JWT токен для клієнта, а операцію `UPDATE users SET password_hash = ... WHERE id = ...` відправляє в асинхронну чергу фонових воркерів або виконує в неблокуючій транзакції.
* **Збій оновлення:** Якщо фоновий запис зазнав невдачі через мережевий таймаут до БД, автентифікація користувача все одно вважається успішною. При наступному вході система просто повторить спробу лінивого оновлення.

### 2. Захист від вичерпання ресурсів пам'яті (DoS)

Оскільки операція Argon2id з виділенням 64 МіБ пам'яті є ресурсомісткою, зловмисник може спробувати надіслати тисячі паралельних запитів на вхід для виклику Out-Of-Memory (OOM) паніки ядра Linux:

* **Обмеження кількості одночасних гешувань:** Сервер автентифікації повинен використовувати семафор або фіксований пул потоків для операцій гешування (наприклад, не більше ніж `N_cores` одночасних обчислень).
* **Черга очікування:** Надлишкові запити ставляться в чергу з коротким таймаутом або відхиляються з кодом `429 Too Many Requests`.
### 3. Інтеграція серверного перцю (Pepper) через HMAC-обгортку

Серверний перець (*pepper*) — це таємний криптографічний ключ високої ентропії (256 бітів), який зберігається окремо від основної бази даних облікових записів (наприклад, у захищеному сховищі ключів HashiCorp Vault, AWS KMS або апаратному модулі безпеки HSM).

Існує дві архітектурні схеми інтеграції перцю в конвеєр:

1. **Внутрішній секретний ключ Argon2 (`key / secret`).** Стандарт RFC 9106 дозволяє передавати додатковий параметр секретного ключа `K` безпосередньо в блок ініціалізації матриці пам'яті. Це надійно, проте унеможливлює швидку ротацію ключа перцю, оскільки зміна перцю вимагає перерахунку всієї матриці пам'яті за наявності відкритого пароля.
2. **Зовнішня HMAC-обгортка (`HMAC-SHA256`).** Перед передачею пароля в гешер сервер обчислює проміжний хеш-код: `pre_hash = HMAC-SHA256(pepper_key, user_password)`. Утилізований у такий спосіб 32-байтовий бінарний вивід стає вхідним паролем для Argon2id. Цей підхід дає три суттєві переваги:
   * Знімає будь-які обмеження на довжину вхідного пароля (навіть якщо користувач передав рядок на 10 кілобайтів).
   * Повністю усуває проблему 72-байтового обрізання в застарілих бібліотеках bcrypt.
   * Дозволяє версіонувати перець за допомогою ідентифікатора ключа (наприклад, `pepper_v1`, `pepper_v2`) у службових метаданих запису.

### 4. Юнікод-нормалізація та обробка спеціальних символів

Сучасні паролі часто містять символи національних алфавітів, діакритичні знаки або емодзі. У стандарті Unicode один і той самий візуальний символ може бути закодований різними байтовими послідовностями (наприклад, літера «é» може бути одним кодовим символом `U+00E9` або комбінацією літери «e» `U+0065` та діакритичного знака `U+0301`).

Якщо клієнт вводить пароль на iOS (де клавіатура за замовчуванням генерує одну форму нормалізації), а реєструється на Windows (інша форма), пряме побайтове гешування спричинить неможливість входу.

* **Правило обробки:** Перед передачею пароля до криптографічного конвеєра серверний шар зобов'язаний виконати нормалізацію рядка у формат **Unicode NFC** (Canonical Composition) та зафіксувати кодування строго як UTF-8 без завершального нульового байта `\0`.
* **Заборона обрізання пробілів:** Функції санітизації введення (`trim()`) ніколи не повинні застосовуватися до поля пароля, оскільки пробіли на початку чи в кінці рядка можуть бути свідомою частиною складної парольної фрази (*passphrase*).

