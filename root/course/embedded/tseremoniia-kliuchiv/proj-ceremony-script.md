# ⚙️ Сценарій церемонії ключів: генерація, розщеплення Шаміра та протокол верифікації

Церемонія створення кореневих ключів вимагає детермінованого, повторюваного та математично верифікованого інструментарію, який працює в повністю ізольованій офлайн-системі без зовнішніх бібліотечних залежностей. Якщо алгоритм розділення секрету містить похибки в арифметиці скінченних полів, використовує нестійке джерело ентропії або залишає копії закритого ключа у незатертому динамічному ОЗП, безпека всього подальшого виробництва анулюється.

У цьому проєкті наведено повну реалізацію схеми розділення секрету Шаміра `(k, n)` над полем Галуа `GF(256)` мовами C та ідіоматичною C++20, детальний розбір механізмів захисту від атак через побічні канали пам'яті, систему формування та підписання протоколу церемонії (транскрипту) з обчисленням криптографічних хешів SHA-256, а також автономний сценарій для незалежної верифікації часток свідками.

![Послідовність виконання операцій церемонії ключів](/root/course/embedded/tseremoniia-kliuchiv/img/ceremony-transcript-flow.svg)
*Послідовність дій під час церемонії: від завантаження ізольованої системи до запечатування згенерованих часток секрету в сейф-пакети та підписання аудиторського протоколу.*

## Архітектура розщеплення секрету в полі GF(256)

Арифметика над скінченним полем `GF(2⁸) = GF(256)` базується на операціях над поліномами за модулем незвідного многочлена `x⁸ + x⁴ + x³ + x + 1` (шістнадцяткове значення `0x11B`). Кожен байт вхідного закритого ключа розглядається як незалежний елемент поля.

Головна перевага побайтового розщеплення над `GF(256)` полягає в тому, що довжина кожної частки залишається рівно такою ж, як і довжина вихідного секрету (32 байти для криптографічного ключа Ed25519 або AES-256), додається лише один байт координати `x`. Для представлення часток не потрібні громіздкі бібліотеки довгої арифметики (англ. *bignum libraries*), що критично для автономних систем без динамічного лінкування.

### Механіка алгоритму

1. **Ініціалізація генератора поля:** Обчислюються таблиці експонент (`gf_exp`) та дискретних логарифмів (`gf_log`) за базовим генератором `g = 0x03`. Це дозволяє замінити дороге ділення многочленів на додавання логарифмів за модулем 255.
2. **Побудова полінома:** Для кожного байта секрету `S` генеруються `k − 1` випадкових байтів коефіцієнтів `a₁, a₂, …, aₖ₋₁`. Поліном має вигляд `P(x) = S ⊕ a₁·x ⊕ a₂·x² ⊕ … ⊕ aₖ₋₁·xᵏ⁻¹`.
3. **Обчислення точок:** Для кожного з `n` учасників обчислюється значення `yᵢ = P(xᵢ)` при `xᵢ ∈ {1, 2, …, n}`.
4. **Відновлення через інтерполяцію Лагранжа:** Коли надано будь-які `k` часток `(xⱼ, yⱼ)`, обчислюються базисні коефіцієнти Лагранжа `ℓⱼ(0) = ∏ [m≠j] xₘ / (xⱼ ⊕ xₘ)`. Секрет відновлюється як лінійна комбінація `S = ⨁ [j=1..k] yⱼ · ℓⱼ(0)`.

:::tabs
```c
#include <stdint.h>
#include <stddef.h>
#include <string.h>
#include <stdbool.h>

#define GF256_POLY 0x11B

static uint8_t gf_exp[512];
static uint8_t gf_log[256];
static bool gf_initialized = false;

/* Ініціалізація таблиць логарифмів та експонент для GF(256) */
static void gf256_init(void) {
    if (gf_initialized) return;
    uint32_t val = 1;
    for (int i = 0; i < 255; i++) {
        gf_exp[i] = (uint8_t)val;
        gf_exp[i + 255] = (uint8_t)val;
        gf_log[val] = (uint8_t)i;
        val <<= 1;
        if (val & 0x100) {
            val ^= GF256_POLY;
        }
    }
    gf_log[0] = 0;
    gf_initialized = true;
}

/* Множення у полі GF(256) з захистом від нульових множників */
static inline uint8_t gf256_mul(uint8_t a, uint8_t b) {
    if (a == 0 || b == 0) return 0;
    return gf_exp[gf_log[a] + gf_log[b]];
}

/* Ділення a / b у полі GF(256) */
static inline uint8_t gf256_div(uint8_t a, uint8_t b) {
    if (a == 0) return 0;
    if (b == 0) return 0; /* Неприпустима операція в математиці */
    return gf_exp[(gf_log[a] + 255 - gf_log[b]) % 255];
}

/* Структура однієї частки секрету */
typedef struct {
    uint8_t x;                      /* Індекс частки (1..n) */
    uint8_t data[64];               /* Байти частки */
    size_t len;                     /* Довжина даних у байтах */
} shamir_share_t;

/* Безпечне затирання конфіденційної пам'яті */
static void secure_memzero(void *v, size_t n) {
    volatile uint8_t *p = (volatile uint8_t *)v;
    while (n--) *p++ = 0;
}

/*
 * Розщеплення секрету на n часток з порогом k.
 * random_bytes: буфер випадкових чисел розміром (k - 1) * len байтів.
 */
int shamir_split(const uint8_t *secret, size_t len,
                 uint8_t k, uint8_t n,
                 const uint8_t *random_bytes,
                 shamir_share_t *shares_out) {
    if (k < 2 || k > n || n > 255 || len > 64) return -1;
    gf256_init();

    for (uint8_t i = 0; i < n; i++) {
        shares_out[i].x = (uint8_t)(i + 1);
        shares_out[i].len = len;
        memset(shares_out[i].data, 0, sizeof(shares_out[i].data));
    }

    /* Побайтове обчислення полінома степеня k - 1 */
    for (size_t byte_idx = 0; byte_idx < len; byte_idx++) {
        uint8_t secret_byte = secret[byte_idx];
        
        for (uint8_t i = 0; i < n; i++) {
            uint8_t x = shares_out[i].x;
            uint8_t y = secret_byte; /* a_0 */
            uint8_t x_pow = x;

            for (uint8_t deg = 1; deg < k; deg++) {
                uint8_t coef = random_bytes[(deg - 1) * len + byte_idx];
                y ^= gf256_mul(coef, x_pow);
                x_pow = gf256_mul(x_pow, x);
            }
            shares_out[i].data[byte_idx] = y;
        }
    }
    return 0;
}

/*
 * Відновлення секрету з k наданих часток через інтерполяцію Лагранжа в точці x = 0.
 */
int shamir_combine(const shamir_share_t *shares_in, uint8_t k,
                   uint8_t *secret_out, size_t len) {
    if (k < 2 || len > 64) return -1;
    gf256_init();

    /* Перевірка унікальності точок x */
    for (uint8_t i = 0; i < k; i++) {
        if (shares_in[i].x == 0) return -2;
        for (uint8_t j = i + 1; j < k; j++) {
            if (shares_in[i].x == shares_in[j].x) return -2;
        }
    }

    /* Обчислення коефіцієнтів Лагранжа L_j(0) */
    uint8_t lagrange_weights[256];
    for (uint8_t j = 0; j < k; j++) {
        uint8_t num = 1;
        uint8_t den = 1;
        uint8_t xj = shares_in[j].x;

        for (uint8_t m = 0; m < k; m++) {
            if (m == j) continue;
            uint8_t xm = shares_in[m].x;
            num = gf256_mul(num, xm);            /* 0 - xm у полі характеристики 2 дорівнює xm */
            den = gf256_mul(den, xj ^ xm);       /* xj - xm у полі характеристики 2 дорівнює xj ^ xm */
        }
        lagrange_weights[j] = gf256_div(num, den);
    }

    /* Відновлення байтів секрету */
    for (size_t byte_idx = 0; byte_idx < len; byte_idx++) {
        uint8_t s = 0;
        for (uint8_t j = 0; j < k; j++) {
            s ^= gf256_mul(shares_in[j].data[byte_idx], lagrange_weights[j]);
        }
        secret_out[byte_idx] = s;
    }
    return 0;
}
```
```cpp
#include <cstdint>
#include <cstddef>
#include <span>
#include <vector>
#include <array>
#include <algorithm>
#include <stdexcept>
#include <expected>

namespace ceremony {

class GaloisField256 {
public:
    constexpr GaloisField256() noexcept {
        init();
    }

    [[nodiscard]] uint8_t mul(uint8_t a, uint8_t b) const noexcept {
        if (a == 0 || b == 0) return 0;
        return exp_[log_[a] + log_[b]];
    }

    [[nodiscard]] uint8_t div(uint8_t a, uint8_t b) const {
        if (b == 0) throw std::invalid_argument("Ділення на нуль у GF(256)");
        if (a == 0) return 0;
        return exp_[(log_[a] + 255 - log_[b]) % 255];
    }

private:
    std::array<uint8_t, 512> exp_{};
    std::array<uint8_t, 256> log_{};

    void init() noexcept {
        uint32_t val = 1;
        for (int i = 0; i < 255; ++i) {
            exp_[i] = static_cast<uint8_t>(val);
            exp_[i + 255] = static_cast<uint8_t>(val);
            log_[val] = static_cast<uint8_t>(i);
            val <<= 1;
            if (val & 0x100) {
                val ^= 0x11B; // x^8 + x^4 + x^3 + x + 1
            }
        }
        log_[0] = 0;
    }
};

static const GaloisField256 gf{};

/* Структура частки із захищеним очищенням деструктором RAII */
struct SecretShare {
    uint8_t index{0};
    std::vector<uint8_t> data{};

    ~SecretShare() {
        std::ranges::fill(data, 0);
    }

    SecretShare() = default;
    SecretShare(uint8_t idx, std::vector<uint8_t> bytes)
        : index(idx), data(std::move(bytes)) {}
    SecretShare(const SecretShare&) = default;
    SecretShare& operator=(const SecretShare&) = default;
    SecretShare(SecretShare&&) noexcept = default;
    SecretShare& operator=(SecretShare&&) noexcept = default;
};

enum class SplitError {
    InvalidThreshold,
    InsufficientRandomBytes,
    SecretEmpty
};

enum class CombineError {
    InsufficientShares,
    DuplicateIndices,
    InconsistentShareLengths
};

/* Розщеплення секрету на n часток із порогом k */
std::expected<std::vector<SecretShare>, SplitError>
split_secret(std::span<const uint8_t> secret,
             uint8_t k, uint8_t n,
             std::span<const uint8_t> random_bytes) {
    if (k < 2 || k > n) return std::unexpected(SplitError::InvalidThreshold);
    if (secret.empty()) return std::unexpected(SplitError::SecretEmpty);
    if (random_bytes.size() < static_cast<size_t>(k - 1) * secret.size()) {
        return std::unexpected(SplitError::InsufficientRandomBytes);
    }

    std::vector<SecretShare> shares;
    shares.reserve(n);
    for (uint8_t i = 1; i <= n; ++i) {
        shares.emplace_back(i, std::vector<uint8_t>(secret.size(), 0));
    }

    for (size_t byte_idx = 0; byte_idx < secret.size(); ++byte_idx) {
        const uint8_t s_byte = secret[byte_idx];
        
        for (auto& share : shares) {
            uint8_t x = share.index;
            uint8_t y = s_byte;
            uint8_t x_pow = x;

            for (uint8_t deg = 1; deg < k; ++deg) {
                uint8_t coef = random_bytes[(deg - 1) * secret.size() + byte_idx];
                y ^= gf.mul(coef, x_pow);
                x_pow = gf.mul(x_pow, x);
            }
            share.data[byte_idx] = y;
        }
    }
    return shares;
}

/* Відновлення секрету за наданими частками */
std::expected<std::vector<uint8_t>, CombineError>
combine_shares(std::span<const SecretShare> shares, uint8_t k) {
    if (shares.size() < k || k < 2) {
        return std::unexpected(CombineError::InsufficientShares);
    }

    const size_t len = shares[0].data.size();
    for (const auto& sh : shares) {
        if (sh.data.size() != len) return std::unexpected(CombineError::InconsistentShareLengths);
    }

    // Перевірка унікальності індексів
    for (size_t i = 0; i < k; ++i) {
        for (size_t j = i + 1; j < k; ++j) {
            if (shares[i].index == shares[j].index) {
                return std::unexpected(CombineError::DuplicateIndices);
            }
        }
    }

    // Ваги Лагранжа
    std::vector<uint8_t> lagrange_weights(k);
    for (size_t j = 0; j < k; ++j) {
        uint8_t num = 1;
        uint8_t den = 1;
        uint8_t xj = shares[j].index;

        for (size_t m = 0; m < k; ++m) {
            if (m == j) continue;
            uint8_t xm = shares[m].index;
            num = gf.mul(num, xm);
            den = gf.mul(den, xj ^ xm);
        }
        lagrange_weights[j] = gf.div(num, den);
    }

    std::vector<uint8_t> recovered(len, 0);
    for (size_t byte_idx = 0; byte_idx < len; ++byte_idx) {
        uint8_t s = 0;
        for (size_t j = 0; j < k; ++j) {
            s ^= gf.mul(shares[j].data[byte_idx], lagrange_weights[j]);
        }
        recovered[byte_idx] = s;
    }
    return recovered;
}

} // namespace ceremony
```
:::

## Протокол верифікації та обчислення контрольних відбитків

Під час проведення церемонії свідки повинні мати можливість незалежно верифікувати коректність часток, контрольні суми файлів та відповідність відкритих ключів без передачі секретної інформації через незахищені канали.

Сценарій перевірки (транскрипт) передбачає таку послідовність дій для свідків:
1. Отримання відкритого сертифіката Root CA та обчислення його контрольного SHA-256 хешу на екрані.
2. Перевірка контрольної суми кожного запечатаного сейф-пакета, в якому міститься окрема частка.
3. Фіксація серійного номера кожного пакета у друкованому реєстрі.

Нижче наведено верифікаційний сценарій мовою Python, призначений для запуску свідками на незалежних комп'ютерах під час очного аудиту.

```python
#!/usr/bin/env python3
import hashlib
import binascii
import sys

def sha256_hex(data: bytes) -> str:
    """Обчислення стандартизованого SHA-256 хешу."""
    return hashlib.sha256(data).hexdigest()

def verify_transcript_entry(role: str, name: str, share_index: int, share_hex: str, expected_bag_id: str):
    """
    Звірка параметрів частки крипто-офіцера свідком церемонії.
    """
    share_bytes = binascii.unhexlify(share_hex)
    fingerprint = sha256_hex(share_bytes)
    
    print(f"=== ЗВІРКА ЧАСТКИ #{share_index} ===")
    print(f"Володар частки  : {role} ({name})")
    print(f"Сейф-пакет ID   : {expected_bag_id}")
    print(f"Довжина частки  : {len(share_bytes)} байтів")
    print(f"SHA-256 відбиток: {fingerprint}")
    print(f"Підпис аудитора : [ ______________________ ]\n")

if __name__ == "__main__":
    print("--- ПРОТОКОЛ ЦЕРЕМОНІЇ ГЕНЕРАЦІЇ КОРЕНЕВИХ КЛЮЧІВ ---")
    print("Дата й час: 2026-08-28 10:00 UTC")
    print("Конфігурація: Поріг 3 з 5 (Shamir Secret Sharing GF(256))\n")
    
    # Приклад перевірки відбитків трьох часток кворуму
    verify_transcript_entry("CTO", "Олександр К.", 1, "4a8f9c112233445566778899aabbccddeeff00112233445566778899aabbccdd", "BAG-UA-2026-001")
    verify_transcript_entry("CISO", "Марія В.", 2, "9b2c3d4e5f60718293a4b5c6d7e8f90112233445566778899aabbccddeeff001", "BAG-UA-2026-002")
    verify_transcript_entry("Bank Vault", "Сейф №402", 3, "112233445566778899aabbccddeeff00112233445566778899aabbccddeeff00", "BAG-UA-2026-003")
```

## Інженерний аналіз підводних каменів та загрози безпеці

При створенні та експлуатації систем розділення секретів інженери часто припускаються неочевидних помилок, які повністю нівелюють теоретичну стійкість схеми:

### 1. Оптимізація та «мертвий код» при очищенні пам'яті
Якщо після завершення процедури відновлення секрету викликати стандартний `memset(secret, 0, len)`, сучасні компілятори із прапорцями оптимізації `-O2` або `-O3` виявляють, що буфер `secret` більше не читається в поточній області видимості, і **повністю видаляють інструкцію затирання** як надлишкову (англ. *dead store elimination*). У результаті сирі байти закритого ключа залишаються у вільному ОЗП до перезавантаження машини.
Щоб запобігти цьому, у C слід використовувати системні виклики `explicit_bzero()` чи `memset_s()`, або звертатися через покажчик `volatile uint8_t *`. У C++ найкращою практикою є загортання конфіденційних масивів у RAII-обгортки з гарантованим деструктором `std::ranges::fill(data, 0)`.

### 2. Захист від пошкоджених та підроблених часток
Класична схема Шаміра не має вбудованої перевірки автентичності часток. Якщо один із крипто-офіцерів під час відновлення надасть пошкоджену або навмисно спотворену частку `y'ⱼ ≠ yⱼ`, поліном Лагранжа все одно обчислиться, але видасть неправильне сміттєве значення `S'`, причому без додаткових засобів неможливо визначити, хто саме з учасників надав хибну частку.
Для захисту від цієї вразливості в транскрипт церемонії обов'язково заносяться окремі SHA-256 хеші кожної згенерованої частки або застосовується схема верифікованого розділення секрету Фельдмана (англ. *Feldman's Verifiable Secret Sharing*), де разом із частками публікуються гомоморфні відкриті зобов'язання `g^{aᵢ}`.

### 3. Запобігання витоку через кеш-лінії процесора
У наведеній вище табличній реалізації множення через `gf_log` індекси звернення до масиву залежать від секретних коефіцієнтів. На процесорах зі спільною кеш-пам'яттю L1/L2 це потенційно створює ризик атак за часом доступу до кеш-ліній (англ. *cache-timing attack*). Для середовищ найвищого рівня критичності (FIPS 140-3 Level 4) множення в полі `GF(256)` замінюють на побітове множення у стовпчик без використання таблиць із постійним часом виконання для будь-яких вхідних операндів.

### 4. Фіксація сторінок пам'яті в ОЗП (mlock) та заборона скидання дампів
У середовищах POSIX під час роботи з конфіденційними частками обов'язково викликається системний виклик `mlock(secret, len)` (або `mlockall(MCL_CURRENT | MCL_FUTURE)`). Цей виклик гарантує ядру операційної системи, що сторінки віртуальної пам'яті, де тимчасово розміщено закритий ключ чи коефіцієнти полінома, ніколи не будуть вивантажені на диск у розділ підкачування (swap). Додатково процес блокує створення дампів аварійного завершення через виклик `setrlimit(RLIMIT_CORE, &rlim)` зі значенням ліміту `0`, що унеможливлює запис вмісту ОЗП у файл `core` у разі виникнення винятку або помилки сегментації (`SIGSEGV`).

