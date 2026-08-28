# ⚙️ Реалізація криптографічного розблокування завантажувача за схемою Challenge-Response

На серійному виробництві мікроконтролери замикають механізмом безпечного завантаження (Secure Boot): у комірки одноразово програмованої пам'яті (eFuse / OTP) записують хеш закритого кореневого ключа виробника, а інтерфейси апаратного зневадження (JTAG/SWD) незворотно блокують. Це надійно захищає кінцевого користувача від підміни коду зловмисником у процесі транспортування чи експлуатації.

Проте коли життєвий цикл виробу добігає кінця (EOL), комерційний бекенд вимикається, а виробник припиняє випуск оновлень безпеки. Якщо пристрій залишиться замкненим, користувач не зможе виправити критичні вразливості або адаптувати апаратну платформу під локальні відкриті системи керування (наприклад, ESPHome чи OpenWrt). З іншого боку, відкриття завантажувача не повинно перетворюватися на вразливість: простий спільний пароль чи глобальний бінарний патч дозволив би зловмиснику отримати фізичний доступ до чужого викинутого пристрою та витягти з Flash-пам'яті приватні ключі, токени авторизації чи паролі домашньої мережі Wi-Fi попереднього власника.

Архітектурно правильне інженерне розв'язання — криптографічна схема «запит-відповідь» (Challenge-Response), яка вимагає підтвердження права розблокування цифровим підписом виробника та супроводжується обов'язковим апаратним знищенням усіх чутливих даних (Secure Zeroization).

---

### Архітектура протоколу та послідовність станів

Протокол взаємодії між сервісною утилітою розблокування на комп'ютері користувача та мікроконтролером розгортається у кілька послідовних кроків із контролем тайм-аутів та перевіркою стану живлення:

```
[ Хост / EOL-утиліта ]                           [ Вбудований завантажувач MCU ]
         |                                                       |
         | -------- 1. Команда CMD_GET_CHALLENGE --------------->|
         |                                                       |
         | <------- 2. Відповідь (Nonce || Chip_UUID) ---------- | (TRNG генерує 32 байти Nonce)
         |                                                       | (Таймер активності 120 с)
         |                                                       |
[ Офлайн-генератор EOL ]                                         |
(Підпис закритим ключем)                                         |
         |                                                       |
         | -------- 3. Команда CMD_UNLOCK_EXECUTE -------------->|
         |             + Підпис Sig_Ed25519                      |
         |                                                       | (Верифікація підпису PK_master)
         |                                                       | (Secure Zeroization NVS/Flash)
         |                                                       | (Запис статусу UNLOCKED в OTP)
         | <------- 4. Відповідь: СТАТУС УСПІХУ -----------------|
```

1. **Генерація одноразового запиту (Challenge):** Завантажувач зчитує фабричний апаратний номер мікроконтролера (`Chip_UUID`), зашитий на кремнієвій пластині заводом-виробником чіпа. Далі апаратний генератор справжніх випадкових чисел (TRNG, True Random Number Generator) збирає ентропію з теплового шуму кремнієвих переходів та генерує 256-бітний одноразовий вектор (`Nonce`). Значення `Nonce` записується виключно в оперативну пам'ять (SRAM), а внутрішній таймер обмежує час життя сесії розблокування (типово 120 секунд).
2. **Накладання цифрового підпису:** Користувач вводить згенеровані пристроєм дані у відкриту локальну утиліту або веб-форму, опубліковану виробником на момент виведення продукту з експлуатації. Генератор підписує бінарну склейку `(Nonce || Chip_UUID)` закритим ключем розблокування (Master EOL Private Key) за асиметричним алгоритмом Ed25519 (RFC 8032) або ECDSA secp256r1.
3. **Верифікація та безпечне стирання:** Завантажувач отримує 64-байтний підпис, відновлює повідомлення зі збереженого в SRAM `Nonce` та апаратного `Chip_UUID` і перевіряє підпис відносно відкритого ключа виробника (`EOL_ROOT_PUBLIC_KEY`), що зашитий у захищеній пам'яті Mask ROM.
4. **Знищення ключів і зміна апаратного прапорця:** Якщо підпис валідний, завантажувач переходить у захищений режим стирання: сектори енергонезалежного сховища NVS затираються нульовими байтами у два проходи, після чого перепалюється спеціальна комірка eFuse (або оновлюється прапорець у закритому конфігураційному секторі Flash). Пристрій перезавантажується й надалі дозволяє запис будь-якого неподписаного бінарного коду.

---

### Криптографічні обмеження на мікроконтролерах

Вибір алгоритму підпису для завантажувача визначається обмеженнями обчислювальної складності та розміру оперативної пам'яті:

- **Ed25519 (Curve25519, SHA-512):** Забезпечує детермінований підпис, стійкість до атак за часом виконання та не потребує генерації якісної ентропії на стороні перевірки. Реалізація верифікатора займає близько 4 КБ коду Flash і потребує менше 1 КБ стека RAM, що дозволяє виконувати її навіть на базових ядрах ARM Cortex-M0+ із тактовою частотою 48 МГц за 85–120 мілісекунд.
- **ECDSA secp256r1 (NIST P-256):** Потребує наявності апаратного криптографічного прискорювача (Public Key Accelerator, PKA) для швидкого виконання операцій скалярного множення на точці кривої. За відсутності PKA програмна верифікація вимагає значно більше пам'яті під математичні бібліотеки великих чисел (BIGNUM) і створює ризик вразливостей через побічні канали випромінювання.

---

### Програмна реалізація завантажувача

Нижче наведено модульну реалізацію логіки перевірки розблокування та гарантованого стирання користувацьких параметрів для мікроконтролера.

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define CHALLENGE_NONCE_LEN   32
#define CHIP_UUID_LEN         16
#define SIGNATURE_LEN         64
#define PUBLIC_KEY_LEN        32
#define NVS_FLASH_SECTOR_SIZE 4096
#define NVS_FLASH_SECTORS_NUM 8

/* Коди результатів виконання операцій */
typedef enum {
    UNLOCK_OK                 = 0,
    UNLOCK_ERR_INVALID_NONCE  = 1,
    UNLOCK_ERR_SIGNATURE_FAIL = 2,
    UNLOCK_ERR_TIMEOUT        = 3,
    UNLOCK_ERR_FLASH_FAILURE  = 4
} unlock_status_t;

/* Структура запиту на розблокування */
typedef struct {
    uint8_t nonce[CHALLENGE_NONCE_LEN];
    uint8_t chip_uuid[CHIP_UUID_LEN];
    uint32_t timestamp_ms;
    bool     is_active;
} challenge_state_t;

/* Відкритий кореневий ключ розблокування виробника (зашитий у ROM) */
static const uint8_t EOL_ROOT_PUBLIC_KEY[PUBLIC_KEY_LEN] = {
    0x3b, 0x6a, 0x27, 0xbc, 0xce, 0xb6, 0xa4, 0x2d,
    0x68, 0x7a, 0xa5, 0x65, 0x84, 0x88, 0xdd, 0x4d,
    0x9c, 0x86, 0x45, 0x40, 0x07, 0x69, 0x66, 0x04,
    0x69, 0x62, 0x0d, 0xa4, 0x63, 0xa5, 0x72, 0x8b
};

static challenge_state_t g_challenge_state;

/* Прототипи апаратних функцій HAL */
extern void hal_trng_fill(uint8_t *dest, size_t len);
extern void hal_get_chip_uuid(uint8_t *dest);
extern uint32_t hal_get_tick_ms(void);
extern bool hal_flash_erase_sector(uint32_t sector_addr);
extern bool hal_flash_write(uint32_t addr, const uint8_t *data, size_t len);
extern bool hal_efuse_burn_unlocked_flag(void);
extern bool crypto_ed25519_verify(const uint8_t *sig, const uint8_t *msg, 
                                  size_t msg_len, const uint8_t *pub_key);

/* Безпечне очищення буфера (гарантоване компілятором без оптимізації) */
static void secure_memzero(void *v, size_t n) {
    volatile uint8_t *p = (volatile uint8_t *)v;
    while (n--) {
        *p++ = 0x00;
    }
}

/* Генерація одноразового виклику (Challenge) */
void bootloader_create_challenge(uint8_t *out_nonce, uint8_t *out_uuid) {
    hal_trng_fill(g_challenge_state.nonce, CHALLENGE_NONCE_LEN);
    hal_get_chip_uuid(g_challenge_state.chip_uuid);
    
    g_challenge_state.timestamp_ms = hal_get_tick_ms();
    g_challenge_state.is_active = true;
    
    memcpy(out_nonce, g_challenge_state.nonce, CHALLENGE_NONCE_LEN);
    memcpy(out_uuid, g_challenge_state.chip_uuid, CHIP_UUID_LEN);
}

/* Безпечне знищення даних користувача у Flash (Secure Zeroization) */
static bool bootloader_zeroize_user_data(void) {
    uint8_t zero_buf[256];
    secure_memzero(zero_buf, sizeof(zero_buf));

    /* Сектори NVS сховища параметрів (Wi-Fi паролі, сертифікати, токени) */
    const uint32_t nvs_base_addr = 0x08040000;
    
    for (uint32_t i = 0; i < NVS_FLASH_SECTORS_NUM; i++) {
        uint32_t addr = nvs_base_addr + (i * NVS_FLASH_SECTOR_SIZE);
        
        /* 1. Стираємо сектор (переведення всіх бітів у 0xFF) */
        if (!hal_flash_erase_sector(addr)) {
            return false;
        }
        
        /* 2. Записуємо нулі для запобігання відновленню залишків заряду */
        for (uint32_t offset = 0; offset < NVS_FLASH_SECTOR_SIZE; offset += sizeof(zero_buf)) {
            if (!hal_flash_write(addr + offset, zero_buf, sizeof(zero_buf))) {
                return false;
            }
        }
    }
    return true;
}

/* Обробка та верифікація токена розблокування */
unlock_status_t bootloader_process_unlock(const uint8_t *signature, uint32_t current_time_ms) {
    if (!g_challenge_state.is_active) {
        return UNLOCK_ERR_TIMEOUT;
    }
    
    /* Перевірка тайм-ауту активності виклику (120 секунд) */
    if ((current_time_ms - g_challenge_state.timestamp_ms) > 120000) {
        secure_memzero(&g_challenge_state, sizeof(g_challenge_state));
        return UNLOCK_ERR_TIMEOUT;
    }
    
    /* Формуємо повідомлення: Nonce || Chip_UUID */
    uint8_t message[CHALLENGE_NONCE_LEN + CHIP_UUID_LEN];
    memcpy(message, g_challenge_state.nonce, CHALLENGE_NONCE_LEN);
    memcpy(message + CHALLENGE_NONCE_LEN, g_challenge_state.chip_uuid, CHIP_UUID_LEN);
    
    /* Верифікація криптографічного підпису */
    bool valid = crypto_ed25519_verify(signature, message, sizeof(message), EOL_ROOT_PUBLIC_KEY);
    
    /* Негайне стирання повідомлення та виклику з оперативної пам'яті */
    secure_memzero(message, sizeof(message));
    secure_memzero(&g_challenge_state, sizeof(g_challenge_state));
    
    if (!valid) {
        return UNLOCK_ERR_SIGNATURE_FAIL;
    }
    
    /* Підпис валідний -> виконуємо стирання конфіденційних даних */
    if (!bootloader_zeroize_user_data()) {
        return UNLOCK_ERR_FLASH_FAILURE;
    }
    
    /* Перепалюємо апаратний біт статусу розблокування */
    if (!hal_efuse_burn_unlocked_flag()) {
        return UNLOCK_ERR_FLASH_FAILURE;
    }
    
    return UNLOCK_OK;
}
```
```cpp
#include <array>
#include <span>
#include <cstdint>
#include <expected>
#include <algorithm>

namespace bootloader {

inline constexpr std::size_t ChallengeNonceLen = 32;
inline constexpr std::size_t ChipUuidLen = 16;
inline constexpr std::size_t SignatureLen = 64;
inline constexpr std::size_t PublicKeyLen = 32;
inline constexpr std::size_t NvsSectorSize = 4096;
inline constexpr std::size_t NvsSectorsCount = 8;
inline constexpr uint32_t ChallengeTimeoutMs = 120'000;

enum class UnlockError : uint8_t {
    InvalidNonce,
    SignatureVerificationFailed,
    ChallengeTimedOut,
    FlashEraseFailed,
    EfuseBurnFailed
};

/* RAII-обгортка для гарантованого стирання чутливих даних у пам'яті */
template <std::size_t N>
struct SecureBuffer {
    std::array<uint8_t, N> data{};

    ~SecureBuffer() noexcept {
        volatile uint8_t* ptr = data.data();
        std::fill_n(ptr, N, 0x00);
    }
};

/* Апаратний інтерфейс мікроконтролера */
class HalDriver {
public:
    virtual ~HalDriver() = default;
    virtual void fill_trng(std::span<uint8_t> dest) = 0;
    virtual void read_chip_uuid(std::span<uint8_t, ChipUuidLen> dest) = 0;
    virtual uint32_t get_tick_ms() const noexcept = 0;
    virtual bool erase_flash_sector(uint32_t address) = 0;
    virtual bool write_flash(uint32_t address, std::span<const uint8_t> buffer) = 0;
    virtual bool burn_unlocked_efuse() = 0;
    virtual bool verify_ed25519(std::span<const uint8_t, SignatureLen> sig,
                                std::span<const uint8_t> msg,
                                std::span<const uint8_t, PublicKeyLen> pubkey) const noexcept = 0;
};

class UnlockController {
public:
    explicit UnlockController(HalDriver& hal, std::span<const uint8_t, PublicKeyLen> root_pubkey) noexcept
        : hal_(hal), root_pubkey_(root_pubkey) {}

    struct Challenge {
        std::array<uint8_t, ChallengeNonceLen> nonce;
        std::array<uint8_t, ChipUuidLen> uuid;
    };

    [[nodiscard]] Challenge generate_challenge() {
        hal_.fill_trng(active_challenge_.nonce);
        hal_.read_chip_uuid(active_challenge_.uuid);
        challenge_created_at_ms_ = hal_.get_tick_ms();
        has_active_challenge_ = true;

        return {active_challenge_.nonce, active_challenge_.uuid};
    }

    [[nodiscard]] std::expected<void, UnlockError> process_unlock(
        std::span<const uint8_t, SignatureLen> signature, uint32_t now_ms) noexcept {
        
        if (!has_active_challenge_) {
            return std::unexpected(UnlockError::ChallengeTimedOut);
        }

        if (now_ms - challenge_created_at_ms_ > ChallengeTimeoutMs) {
            reset_challenge();
            return std::unexpected(UnlockError::ChallengeTimedOut);
        }

        SecureBuffer<ChallengeNonceLen + ChipUuidLen> msg_buf;
        std::copy(active_challenge_.nonce.begin(), active_challenge_.nonce.end(), msg_buf.data.begin());
        std::copy(active_challenge_.uuid.begin(), active_challenge_.uuid.end(), msg_buf.data.begin() + ChallengeNonceLen);

        const bool is_valid = hal_.verify_ed25519(signature, msg_buf.data, root_pubkey_);
        reset_challenge();

        if (!is_valid) {
            return std::unexpected(UnlockError::SignatureVerificationFailed);
        }

        if (!zeroize_user_data()) {
            return std::unexpected(UnlockError::FlashEraseFailed);
        }

        if (!hal_.burn_unlocked_efuse()) {
            return std::unexpected(UnlockError::EfuseBurnFailed);
        }

        return {};
    }

private:
    void reset_challenge() noexcept {
        volatile uint8_t* ptr = reinterpret_cast<volatile uint8_t*>(&active_challenge_);
        std::fill_n(ptr, sizeof(active_challenge_), 0x00);
        has_active_challenge_ = false;
    }

    bool zeroize_user_data() noexcept {
        constexpr uint32_t NvsBaseAddr = 0x08040000;
        const std::array<uint8_t, 256> zeros{};

        for (std::size_t i = 0; i < NvsSectorsCount; ++i) {
            const uint32_t sector_addr = NvsBaseAddr + static_cast<uint32_t>(i * NvsSectorSize);
            if (!hal_.erase_flash_sector(sector_addr)) {
                return false;
            }
            for (uint32_t offset = 0; offset < NvsSectorSize; offset += zeros.size()) {
                if (!hal_.write_flash(sector_addr + offset, zeros)) {
                    return false;
                }
            }
        }
        return true;
    }

    HalDriver& hal_;
    std::span<const uint8_t, PublicKeyLen> root_pubkey_;
    struct {
        std::array<uint8_t, ChallengeNonceLen> nonce{};
        std::array<uint8_t, ChipUuidLen> uuid{};
    } active_challenge_;
    uint32_t challenge_created_at_ms_{0};
    bool has_active_challenge_{false};
};

} // namespace bootloader
```
:::

---

### Трасування та перевірка через діагностичний порт

Під час реального сеансу розблокування через серійний інтерфейс UART або USB CDC поведінка системи простежується за допомогою діагностичних логів завантажувача:

```text
[BOOT] Device UUID: 7A 1F 8C 33 09 B2 44 1E 88 C0 11 2A 9F 04 E5 71
[BOOT] Mode: SECURE_BOOT_LOCKED
[BOOT] CMD_GET_CHALLENGE received
[BOOT] TRNG entropy pool ready. Nonce generated (32 bytes).
[BOOT] Challenge session started. Timeout: 120000 ms.
[BOOT] CMD_UNLOCK_EXECUTE received. Signature len: 64 bytes.
[BOOT] Verifying Ed25519 signature against ROM EOL_ROOT_PUBLIC_KEY...
[BOOT] Signature OK. Proceeding to Secure Zeroization.
[BOOT] Erasing NVS sector 0x08040000... [OK] Overwriting zeros... [OK]
[BOOT] Erasing NVS sector 0x08041000... [OK] Overwriting zeros... [OK]
...
[BOOT] Zeroization completed (32 KB sanitized).
[BOOT] Burning UNLOCKED eFuse bit... [OK]
[BOOT] System status changed: UNLOCKED_DEV_MODE.
[BOOT] Rebooting into open bootloader...
```

---

### Пастки та крайові випадки реалізації

1. **Атака повторного відтворення (Replay Attack):** Якщо `Nonce` не генерується апаратно перед кожною спробою або залишається статичним, зловмисник зможе перехопити один раз виданий токен і розблокувати будь-який чужий пристрій із таким самим типом чипу. Наявність `Chip_UUID` у підписаному повідомленні зв'язує токен із конкретним фізичним кристалом, а одноразовий `Nonce` — з конкретною сесією у часі.
2. **Оптимізація компілятора при стиранні пам'яті:** Звичайний виклик `memset(buf, 0, len)` часто викидається оптимізатором GCC/Clang (`-O2` / `-Os`), якщо змінна `buf` надалі не читається в коді програми (Dead Store Elimination). Це призводить до того, що ключі шифрування та паролі залишаються у Flash або RAM після завершення процедури. Застосування `volatile`-покажчиків, виклику `explicit_bzero()` або деструкторів RAII є строго обов'язковим.
3. **Обрив живлення під час стирання:** Якщо живлення приладу буде перервано посеред процедури затирання Flash, пристрій не повинен опинитися розблокованим із наполовину вцілілими секретами користувача. Апаратний біт статусу `UNLOCKED` у eFuse перепалюється **виключно після** успішного завершення операції повного перезаписування всіх секторів.
4. **Залишкова намагніченість і пастки напівпровідникової пам'яті:** Звичайне стирання секторів Flash (Erase) переводить усі біти у стан логічної одиниці `0xFF`. Проте у зношених комірках плаваючого затвора (Floating Gate) залишковий заряд може бути відновлений лабораторними методами аналізу напруги відкриття транзистора. Подвійний цикл «Erase -> Write Zeros» гарантує надійне фізичне розсіювання заряду перед відкриттям доступу до шини завантажувача.
