# ⚙️ Алгоритми когортного джитера, детермінованого гешування та автоматичного відкату

Керування оновленням тисячі вбудованих пристроїв вимагає детермінованого розбиття парку на когорти без збереження списків на сервері, згладжування пікового мережевого навантаження за допомогою випадкового джитера та надійного механізму випробувального терміну з апаратним відкатом. Нижче наведено реалізацію ключових алгоритмів клієнтського вузла прошивки.

## 1. Детерміноване розбиття на когорти (Bucket Hashing)

Кожен пристрій повинен самостійно і детерміновано визначити свій номер когорти в діапазоні `0..99`, не запитуючи індивідуального дозволу в сервера для кожного кроку. При цьому розподіл пристроїв за когортами має бути рівномірним, а для різних релізів — декоррельованим (щоб одні й ті самі вузли не були вічними «піддослідними кроликами» на фазі 1%).

Для цього використовується криптографічний хеш від конкатенації унікального апаратного ідентифікатора (MAC-адреси чи UUID чипа) та випадкової солі кампанії (`campaign_salt`), яка публікується в маніфесті:

```
cohort_bucket = SHA-256(hardware_id || campaign_salt) % 100
```

У мікроконтролерах без апаратного прискорювача криптографії для розрахунку номера когорти допустимо використовувати швидкі некриптографічні хеш-функції з високим лавинним ефектом (наприклад, FNV-1a або MurmurHash3), за умови, що якість розподілу залишку від ділення на 100 перевірена на всій множині серійних номерів парку.

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define HW_ID_LEN 16
#define SALT_LEN  16

/* Спрощена ілюстративна хеш-функція типу FNV-1a для MCU
   У промислових виробах використовується апаратний SHA-256 */
static uint32_t compute_hash32(const uint8_t *data, size_t len) {
    uint32_t hash = 2166136261u;
    for (size_t i = 0; i < len; ++i) {
        hash ^= data[i];
        hash *= 16777619u;
    }
    return hash;
}

uint8_t calculate_device_cohort(const uint8_t hw_id[HW_ID_LEN],
                                const uint8_t salt[SALT_LEN]) {
    uint8_t buffer[HW_ID_LEN + SALT_LEN];
    memcpy(buffer, hw_id, HW_ID_LEN);
    memcpy(buffer + HW_ID_LEN, salt, SALT_LEN);

    uint32_t digest = compute_hash32(buffer, sizeof(buffer));
    return (uint8_t)(digest % 100u);
}

bool is_device_eligible_for_stage(uint8_t device_cohort, uint8_t stage_cutoff_percent) {
    return device_cohort < stage_cutoff_percent;
}
```
```cpp
#pragma once
#include <cstdint>
#include <cstddef>
#include <span>
#include <array>
#include <algorithm>

namespace fleet {

class CohortClassifier {
public:
    static constexpr size_t kIdLen = 16;
    static constexpr size_t kSaltLen = 16;

    static uint8_t calculate_bucket(std::span<const uint8_t, kIdLen> hw_id,
                                    std::span<const uint8_t, kSaltLen> salt) noexcept {
        std::array<uint8_t, kIdLen + kSaltLen> buffer{};
        std::copy(hw_id.begin(), hw_id.end(), buffer.begin());
        std::copy(salt.begin(), salt.end(), buffer.begin() + kIdLen);

        uint32_t hash = 2166136261u;
        for (uint8_t byte : buffer) {
            hash ^= byte;
            hash *= 16777619u;
        }
        return static_cast<uint8_t>(hash % 100u);
    }

    static constexpr bool is_eligible(uint8_t cohort, uint8_t cutoff_percent) noexcept {
        return cohort < cutoff_percent;
    }
};

} // namespace fleet
```
:::

## 2. Згладжування навантаження: рівномірний джитер і Decorrelated Jitter

Коли чергова фаза (наприклад, 25% = 250 пристроїв) активується на сервері, всі 250 вузлів не повинні одночасно звертатися до CDN. Кожен вузол обирає початкову випадкову затримку в інтервалі `[0, jitter_window]`. Це перетворює дискретний пік навантаження на рівномірний потік запитів.

Якщо під час завантаження сесія обривається через нестабільний радіосигнал або таймаут шлюзу, повторні спроби плануються за алгоритмом Decorrelated Jitter:

```
t_retry = min(T_max, Uniform(T_base, t_previous · 3))
```

Такий підхід запобігає виникненню фазової синхронізації між пристроями, коли група вузлів циклічно повторює запити в один і той самий момент.

:::tabs
```c
#include <stdint.h>
#include <stdlib.h>

typedef struct {
    uint32_t base_delay_ms;
    uint32_t max_delay_ms;
    uint32_t current_delay_ms;
} retry_backoff_t;

void retry_backoff_init(retry_backoff_t *b, uint32_t base_ms, uint32_t max_ms) {
    b->base_delay_ms = base_ms;
    b->max_delay_ms = max_ms;
    b->current_delay_ms = base_ms;
}

uint32_t retry_backoff_next(retry_backoff_t *b, uint32_t random_seed) {
    /* Рівномірний псевдовипадковий коефіцієнт [0.0 .. 1.0] */
    uint32_t range = (b->current_delay_ms * 3u) - b->base_delay_ms;
    if (range == 0) range = 1;
    
    uint32_t jittered = b->base_delay_ms + (random_seed % range);
    if (jittered > b->max_delay_ms) {
        jittered = b->max_delay_ms;
    }
    b->current_delay_ms = jittered;
    return jittered;
}

uint32_t calculate_initial_jitter(uint32_t window_seconds, uint32_t random_val) {
    if (window_seconds == 0) return 0;
    return (random_val % window_seconds);
}
```
```cpp
#pragma once
#include <cstdint>
#include <algorithm>
#include <random>
#include <chrono>

namespace fleet {

class BackoffManager {
public:
    using Milliseconds = std::chrono::milliseconds;

    constexpr BackoffManager(Milliseconds base, Milliseconds max) noexcept
        : base_(base), max_(max), current_(base) {}

    template <typename UniformRng>
    Milliseconds next_delay(UniformRng& rng) noexcept {
        const auto high = std::min(max_, current_ * 3);
        if (high <= base_) {
            current_ = base_;
            return base_;
        }
        std::uniform_int_distribution<uint32_t> dist(
            static_cast<uint32_t>(base_.count()),
            static_cast<uint32_t>(high.count())
        );
        current_ = Milliseconds(dist(rng));
        return current_;
    }

    void reset() noexcept {
        current_ = base_;
    }

    static std::chrono::seconds calculate_initial_jitter(
        std::chrono::seconds window, uint32_t raw_random) noexcept {
        if (window.count() == 0) return std::chrono::seconds(0);
        return std::chrono::seconds(raw_random % window.count());
    }

private:
    Milliseconds base_;
    Milliseconds max_;
    Milliseconds current_;
};

} // namespace fleet
```
:::

## 3. Автомат випробувального терміну (Health Watchdog) та тригер відкату

Після завантаження образу в неактивний Bank B та успішного перезавантаження мікроконтролер переходить у стан випробувального терміну. Якщо протягом заданого часу (наприклад, 1800 секунд) прошивка не підтвердила власну життєздатність або зафіксувала аномалії сенсорних шин / паніку ядра, сторожовий таймер або функція контролю відкату відновлює попередній стабільний завантажувальний Bank A.

Архітектура пам'яті передбачає збереження стану випробування в незалежній пам'яті (RTC Backup Registers або окремому секторі EEPROM):
- `active_bank`: поточний вибраний банк завантаження (`BOOT_BANK_A` або `BOOT_BANK_B`).
- `trial_boot_pending`: прапорець, який вказує завантажувачу, що прошивка ще не підтвердила стабільність.
- `boot_failures_count`: лічильник аварійних перезапусків нової версії. Якщо значення сягає `MAX_ALLOWED_CRASHES`, завантажувач примусово повертає покажчик на попередній перевірений банк.

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>

typedef enum {
    BOOT_BANK_A = 0,
    BOOT_BANK_B = 1
} boot_bank_t;

typedef struct {
    boot_bank_t active_bank;
    uint32_t    health_timeout_sec;
    uint32_t    elapsed_healthy_sec;
    uint8_t     reboot_failures_count;
    bool        is_confirmed_stable;
} trial_boot_controller_t;

#define MAX_ALLOWED_CRASHES 3

void trial_boot_init(trial_boot_controller_t *c, boot_bank_t bank, uint32_t timeout_sec) {
    c->active_bank = bank;
    c->health_timeout_sec = timeout_sec;
    c->elapsed_healthy_sec = 0;
    c->reboot_failures_count = 0;
    c->is_confirmed_stable = false;
}

/* Викликається періодично з головного циклу (наприклад, кожні 10 секунд) */
bool trial_boot_step(trial_boot_controller_t *c, uint32_t dt_sec, bool hardware_self_test_ok) {
    if (c->is_confirmed_stable) {
        return true; /* Образ уже остаточно прийнятий */
    }

    if (!hardware_self_test_ok) {
        /* Критичний дефект периферії -> негайний відкат */
        c->active_bank = (c->active_bank == BOOT_BANK_B) ? BOOT_BANK_A : BOOT_BANK_B;
        return false;
    }

    c->elapsed_healthy_sec += dt_sec;
    if (c->elapsed_healthy_sec >= c->health_timeout_sec) {
        c->is_confirmed_stable = true;
        c->reboot_failures_count = 0;
        return true;
    }

    return true;
}

boot_bank_t trial_boot_get_safe_bank(const trial_boot_controller_t *c) {
    return c->active_bank;
}
```
```cpp
#pragma once
#include <cstdint>
#include <chrono>
#include <optional>

namespace fleet {

enum class BootBank : uint8_t {
    BankA = 0,
    BankB = 1
};

class TrialBootController {
public:
    using Seconds = std::chrono::seconds;

    constexpr TrialBootController(BootBank active, Seconds timeout) noexcept
        : active_bank_(active), timeout_(timeout), elapsed_(0), confirmed_(false) {}

    [[nodiscard]] bool process_heartbeat(Seconds dt, bool sensors_ok, bool network_ok) noexcept {
        if (confirmed_) {
            return true;
        }

        if (!sensors_ok || !network_ok) {
            trigger_rollback();
            return false;
        }

        elapsed_ += dt;
        if (elapsed_ >= timeout_) {
            confirmed_ = true;
            return true;
        }
        return true;
    }

    [[nodiscard]] constexpr bool is_stable() const noexcept { return confirmed_; }
    [[nodiscard]] constexpr BootBank active_bank() const noexcept { return active_bank_; }

    void trigger_rollback() noexcept {
        active_bank_ = (active_bank_ == BootBank::BankB) ? BootBank::BankA : BootBank::BankB;
        confirmed_ = false;
    }

private:
    BootBank active_bank_;
    Seconds timeout_;
    Seconds elapsed_;
    bool confirmed_;
};

} // namespace fleet
```
:::

## 4. Схема розбиття внутрішньої пам'яті (Flash Partitioning)

Для забезпечення безперервної працездатності мікроконтролера адресний простір Flash-пам'яті розбивається на симетричні ізольовані розділи. Нижче наведено типову карту пам'яті для мікроконтролера Cortex-M з 1 МБ Flash-пам'яті:

```
Адресний діапазон        Розмір    Призначення розділу
─────────────────────────────────────────────────────────────────────────────
0x08000000 - 0x0800FFFF   64 КБ    Захищений завантажувач (Secure Bootloader)
0x08010000 - 0x08013FFF   16 КБ    Сектор конфігурації та ключів OTA (NVRAM)
0x08014000 - 0x0807FFFF  432 КБ    Основний розділ виконання (Bank A)
0x08080000 - 0x080EBFFF  432 КБ    Резервний розділ оновлення (Bank B)
0x080EC000 - 0x080FFFFF   80 КБ    Енергонезалежне сховище налаштувань (NVS)
```

Завантажувач розміщується за базовою адресою вектору скидання `0x08000000` і блокується від запису бітами захисту Option Bytes. Під час старту процесора завантажувач аналізує статусний сектор NVRAM:
- Якщо `trial_boot_pending == 0`, завантажувач перевіряє цілісність активного банку за контрольною сумою й передає керування на адресу його таблиці векторів `SCB->VTOR = Bank_Address`.
- Якщо встановлено `trial_boot_pending == 1`, завантажувач інкрементує лічильник збоїв `boot_failures_count`. Якщо лічильник перевищує поріг `MAX_ALLOWED_CRASHES`, завантажувач автоматично скидає активний банк на попередній стабільний, очищає прапорець спроби та запускає робочий розділ Bank A.

## 5. Типові пастки реалізації вбудованого коду

Під час розгортання оновлень на тисячу польових пристроїв інженери найчастіше стикаються з трьома критичними вразливостями реалізації:

1. **Несправжні випадкові числа (PRNG Trap).** Якщо генератор випадкових чисел ініціалізується фіксованим сідом (або нулем після кожного скидання процесора), всі 1000 пристроїв згенерують однаковий псевдовипадковий зсув джитера. В результаті вся когорта звернеться до сервера в одну й ту саму мілісекунду. Для ініціалізації PRNG слід використовувати справжні джерела апаратної ентропії: блок TRNG мікроконтролера, шум молодших бітів непідключеного аналогового входу АЦП або мікросекундні коливання таймера між подіями переривань.
2. **Передчасне підтвердження (Premature Commit).** Поширена помилка — встановлення прапорця постійного образу одразу після успішного старту функції `main()`. Якщо прошивка падає під час першої спроби підключення до TLS або опитування шини I2C через 20 секунд після ввімкнення, пристрій буде заблоковано назавжди. Підтвердження образу (`commit`) має відбуватися лише після проходження повного циклу самодіагностики та успішного обміну даними з бекендом.
3. **Циклічні відкати без збереження стану (Reboot Loop Amnesia).** Лічильник збоїв нової прошивки має обов'язково записуватися в незалежну пам'ять (RTC backup registers, FRAM або спеціальний сектор Flash). Якщо при кожному перезапуску лічильник ініціалізується нулем у стеку RAM, пристрій потрапить у нескінченну петлю перезавантажень, повністю розрядивши автономну батарею.
4. **Блокування Flash під час читання (Read-While-Write Stall).** У багатьох сімействах мікроконтролерів (наприклад, деяких версіях STM32F4) запис або стирання одного сектора Flash блокує зчитування інструкцій з усієї пам'яті Flash. Якщо переривання ISR виконується з пам'яті Flash під час операції запису блоку OTA, ядро зависає у стані блокування шини. Процедура запису блоків повинна або виконуватися з оперативної пам'яті RAM (атрибут `__RAM_FUNC`), або використовувати розділені фізичні банки пам'яті Dual-Bank Flash.
