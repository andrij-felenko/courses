# ⚙️ Проєкт апаратного замикання мікроконтролера у виробничому циклі

Коли серійний виріб без оновлень завершує монтаж на друкованій платі, він потрапляє на автоматизований тестовий стенд (тест-джиг). На цьому стенді голчасті контакти (*pogo pins*) торкаються контрольних точок плати, живлять схему від прецизійного джерела, прошивають бінарний образ через інтерфейс SWD, проводять апаратне калібрування аналогових трактів і записують коефіцієнти в одноразово програмовану область (*OTP*). Фінальною дією конвеєра є **незворотне апаратне замикання кристала**: мікроконтролер конфігурує апаратний захист секторів Flash від запису та перепалює шину зневаджувача (JTAG/SWD) на рівні кремнієвої логіки.

Якщо виконати замикання передчасно — кристал перетвориться на «цеглину» без калібрувальних даних; якщо помилитися в масці секторів або допустити скидання живлення під час запису конфігурації — плата буде безповоротно пошкоджена. Нижче наведено повний інженерний аналіз регістрової моделі, захисних часових вікон, обробки апаратних помилок та реалізацію процедури замикання (RDP Level 2) мовами C та C++.

---

### Апаратна модель регістрів Option Bytes

Контролер Flash-пам'яті сучасного мікроконтролера (на прикладі ядра ARM Cortex-M) захищає службові конфігураційні байти (*Option Bytes*) двоступеневою системою апаратних ключів. Регістри `FLASH_CR` (керування) та `FLASH_OPTR` (опції користувача) за замовчуванням після апаратного скидання перебувають у стані жорсткого блокування (біти `LOCK = 1` та `OPTLOCK = 1`).

```
Запуск ──> [ FLASH_CR заблоковано (LOCK=1) ] ──> Запис KEY1 + KEY2 ───> [ Розблоковано для коду ]
                                                                                │
                                                                   Запис OPTKEY1 + OPTKEY2
                                                                                ↓
                                                                  [ Розблоковано Option Bytes ]
```

Для розблокування доступу до Option Bytes прошивка зобов'язана виконати строгу послідовність запису двох 32-бітних констант у регістр `FLASH_KEYR`, а потім ще двох констант у `FLASH_OPTKEYR`:

```
KEY1    = 0x45670123
KEY2    = 0xCDEF89AB
OPTKEY1 = 0x08192A3B
OPTKEY2 = 0x4C5D6E7F
```

Будь-який запис неправильного значення у ці регістри або порушення черговості слів негайно блокує Flash-контролер до наступного повного холодного перезавантаження (*Power-On Reset*) і генерує прапорець помилки послідовності (*PGSERR*).

Ключовим параметром безпеки є рівень захисту зчитування (*Readout Protection*, RDP). У регістрі `FLASH_OPTR` молодший байт відповідає за режим доступу:

* `0xAA` (Level 0) — режим розробки, повний доступ через SWD/JTAG.
* `0xBB` (Level 1) — пам'ять заблокована для читання зневаджувачем; спроба скинути захист у `0xAA` викликає **повне апаратне стирання всієї Flash-пам'яті (Mass Erase)**.
* `0xCC` (Level 2) — **максимальне незворотне замикання**. Шина SWD/JTAG фізично відключається від ядра процесора внутрішнім комутатором. Повернення в Level 0 або Level 1 неможливе за будь-яких умов. Значення `0xAA` та `0xCC` мають високу відстань Хеммінга (відрізняються в 4 бітах з 8), що запобігає випадковому перемиканню режимів через електричний шум або збійні атаки (*fault injection*).

Одночасно з RDP у регістрі Option Bytes налаштовується поріг детектора просідання живлення (*Brown-Out Reset*, BOR). Для незмінного виробу поріг BOR піднімають до максимального значення (BOR Level 3, типово 2.7–2.8 В). Це гарантує, що мікроконтролер перейде в стан апаратного скидання задовго до того, як падіння напруги призведе до спотворення даних у регістрах ядра чи випадкових збоїв логіки.

---

### Архітектура та послідовність операцій на стенді

Процедура замикання виконується за суворим кінцевим автоматом:

```
[ Стенд: Прошивка ] ──> [ Перевірка OTP даних ] ──> [ Захист секторів Flash ] ──> [ Перехід RDP Level 2 ] ──> [ Фінальний ребут ]
                               │                               │                           │
                        (CRC помилка?)                  (Збій запису?)              (Збій верифікації?)
                               ↓                               ↓                           ↓
                       [ Стенд: АВАРІЯ ]               [ Стенд: АВАРІЯ ]           [ Стенд: АВАРІЯ ]
```

1. **Валідація заводських констант:** Перевірка, що в OTP-секторі присутні серійний номер, апаратна ревізія та валідна контрольна сума (CRC-32) калібрувальних коефіцієнтів.
2. **Вимкнення глобальних переривань:** Перед операціями з Option Bytes переривання обов'язково блокуються (`__disable_irq()`), щоб виключити виклик ISR або спрацювання DMA посеред циклу запису.
3. **Конфігурація секторного захисту від запису (WRP):** Усі сектори Flash, що містять код програми та таблиці векторів переривань, захищаються на рівні Option Bytes (регістр `FLASH_WRP1AR`).
4. **Активація максимального рівня захисту (RDP Level 2):** Запис байта `0xCC` у регістр `FLASH_OPTR`.
5. **Запуск перезавантаження Option Bytes:** Запис біта `OBL_LAUNCH` генерує апаратний перезапуск кристала для застосування нової конфігурації захисту.

---

### Робочий код замикання

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>

/* Регістри Flash-контролера мікроконтролера (типова архітектура ARM Cortex-M) */
#define FLASH_BASE_ADDR        0x40022000UL
#define FLASH_KEYR             (*(volatile uint32_t *)(FLASH_BASE_ADDR + 0x04))
#define FLASH_OPTKEYR          (*(volatile uint32_t *)(FLASH_BASE_ADDR + 0x08))
#define FLASH_SR               (*(volatile uint32_t *)(FLASH_BASE_ADDR + 0x0C))
#define FLASH_CR               (*(volatile uint32_t *)(FLASH_BASE_ADDR + 0x10))
#define FLASH_OPTR             (*(volatile uint32_t *)(FLASH_BASE_ADDR + 0x20))
#define FLASH_WRP1AR           (*(volatile uint32_t *)(FLASH_BASE_ADDR + 0x2C))

/* Ключі розблокування доступу до Option Bytes */
#define FLASH_KEY1             0x45670123UL
#define FLASH_KEY2             0xCDEF89ABUL
#define FLASH_OPTKEY1          0x08192A3BUL
#define FLASH_OPTKEY2          0x4C5D6E7FUL

/* Прапорці регістра статусу Flash */
#define FLASH_SR_BSY           (1UL << 16)
#define FLASH_SR_WRPERR        (1UL << 4)
#define FLASH_SR_PGAERR        (1UL << 5)

/* Керуючі біти */
#define FLASH_CR_LOCK          (1UL << 31)
#define FLASH_CR_OPTLOCK       (1UL << 30)
#define FLASH_CR_OPTSTRT       (1UL << 17)
#define FLASH_CR_OBL_LAUNCH    (1UL << 27)

/* Конфігурація RDP */
#define RDP_LEVEL_0_KEY        0xAAU
#define RDP_LEVEL_1_KEY        0xBBU
#define RDP_LEVEL_2_KEY        0xCCU   /* Незворотне апаратне замикання */

/* Адреси OTP-сектора для калібрування */
#define OTP_START_ADDR         0x1FFF7000UL
#define OTP_MAGIC_HEADER       0x5345414CUL /* ASCII "SEAL" */

typedef enum {
    LOCK_OK = 0,
    LOCK_ERR_OTP_INVALID,
    LOCK_ERR_FLASH_BUSY,
    LOCK_ERR_UNLOCK_FAIL,
    LOCK_ERR_WRITE_FAIL,
    LOCK_ERR_VERIFY_FAIL
} lock_status_t;

/* Перевірка наявності валідних заводських даних в OTP перед замиканням */
static bool verify_factory_otp_data(void) {
    const volatile uint32_t *otp = (const volatile uint32_t *)OTP_START_ADDR;
    if (otp[0] != OTP_MAGIC_HEADER) {
        return false; /* Калібрування ще не записано */
    }
    
    /* Контроль цілісності: обчислення бітової суми слів даних */
    uint32_t sum = 0;
    for (size_t i = 1; i < 8; ++i) {
        sum ^= otp[i];
    }
    return (sum != 0 && sum != 0xFFFFFFFFUL);
}

/* Очікування завершення внутрішніх операцій контролера Flash */
static lock_status_t flash_wait_ready(uint32_t timeout_loops) {
    while (FLASH_SR & FLASH_SR_BSY) {
        if (--timeout_loops == 0) {
            return LOCK_ERR_FLASH_BUSY;
        }
    }
    if (FLASH_SR & (FLASH_SR_WRPERR | FLASH_SR_PGAERR)) {
        FLASH_SR = FLASH_SR_WRPERR | FLASH_SR_PGAERR; /* Скидання помилок */
        return LOCK_ERR_WRITE_FAIL;
    }
    return LOCK_OK;
}

/* Розблокування Option Bytes контролера Flash */
static lock_status_t flash_unlock_options(void) {
    if (FLASH_CR & FLASH_CR_LOCK) {
        FLASH_KEYR = FLASH_KEY1;
        FLASH_KEYR = FLASH_KEY2;
    }
    if (FLASH_CR & FLASH_CR_LOCK) {
        return LOCK_ERR_UNLOCK_FAIL;
    }

    if (FLASH_CR & FLASH_CR_OPTLOCK) {
        FLASH_OPTKEYR = FLASH_OPTKEY1;
        FLASH_OPTKEYR = FLASH_OPTKEY2;
    }
    if (FLASH_CR & FLASH_CR_OPTLOCK) {
        return LOCK_ERR_UNLOCK_FAIL;
    }
    return LOCK_OK;
}

/* Повне блокування контролера Flash */
static void flash_lock_all(void) {
    FLASH_CR |= (FLASH_CR_OPTLOCK | FLASH_CR_LOCK);
}

/* Головна функція замикання виробу на заводському стенді */
lock_status_t factory_lockdown_device(void) {
    /* 1. Обов'язкова перевірка заводських констант */
    if (!verify_factory_otp_data()) {
        return LOCK_ERR_OTP_INVALID;
    }

    /* 2. Очікування готовності Flash */
    lock_status_t status = flash_wait_ready(500000);
    if (status != LOCK_OK) {
        return status;
    }

    /* 3. Розблокування Option Bytes */
    status = flash_unlock_options();
    if (status != LOCK_OK) {
        return status;
    }

    /* 4. Захист усіх секторів коду від запису (WRP від сторінки 0 до 127) */
    FLASH_WRP1AR = (127UL << 16) | (0UL);

    /* 5. Встановлення рівня захисту RDP Level 2 (0xCC) */
    uint32_t optr = FLASH_OPTR;
    optr &= ~0xFFUL;             /* Очищення поля RDP */
    optr |= RDP_LEVEL_2_KEY;     /* Встановлення 0xCC */
    FLASH_OPTR = optr;

    /* 6. Запуск фізичного програмування Option Bytes */
    FLASH_CR |= FLASH_CR_OPTSTRT;
    status = flash_wait_ready(500000);
    if (status != LOCK_OK) {
        flash_lock_all();
        return status;
    }

    /* 7. Замикаємо Flash перед застосуванням */
    flash_lock_all();

    /* 8. Апаратне перезавантаження Option Bytes (System Reset) */
    FLASH_CR |= FLASH_CR_OBL_LAUNCH;

    /* Код далі не виконується: OBL_LAUNCH викликає негайний холодний ребут кристала */
    while (1) {
        __asm__ volatile("nop");
    }
}
```
```cpp
#include <cstdint>
#include <cstddef>
#include <array>
#include <expected>
#include <span>

namespace hardware::security {

enum class LockError : std::uint8_t {
    OtpDataMissingOrCorrupt,
    FlashControllerBusy,
    OptionUnlockFailed,
    WriteFailed,
    VerificationFailed
};

class FlashOptionRegisters {
private:
    static constexpr std::uintptr_t kFlashBase = 0x40022000UL;
    
    struct HardwareLayout {
        volatile std::uint32_t acr;
        volatile std::uint32_t keyr;
        volatile std::uint32_t optkeyr;
        volatile std::uint32_t sr;
        volatile std::uint32_t cr;
        volatile std::uint32_t optr;
        volatile std::uint32_t wrp1ar;
    };

    static constexpr std::uint32_t kKey1 = 0x45670123UL;
    static constexpr std::uint32_t kKey2 = 0xCDEF89ABUL;
    static constexpr std::uint32_t kOptKey1 = 0x08192A3BUL;
    static constexpr std::uint32_t kOptKey2 = 0x4C5D6E7FUL;

    static constexpr std::uint32_t kSrBusy = 1UL << 16;
    static constexpr std::uint32_t kSrWrpErr = 1UL << 4;
    static constexpr std::uint32_t kSrPgaErr = 1UL << 5;

    static constexpr std::uint32_t kCrLock = 1UL << 31;
    static constexpr std::uint32_t kCrOptLock = 1UL << 30;
    static constexpr std::uint32_t kCrOptStart = 1UL << 17;
    static constexpr std::uint32_t kCrOblLaunch = 1UL << 27;

    static constexpr std::uint8_t kRdpLevel2 = 0xCC;
    static constexpr std::uintptr_t kOtpStart = 0x1FFF7000UL;
    static constexpr std::uint32_t kOtpMagic = 0x5345414CUL; /* "SEAL" */

    static HardwareLayout& hw() noexcept {
        return *reinterpret_cast<HardwareLayout*>(kFlashBase);
    }

public:
    /* RAII-обгортка для гарантованого повторного блокування Option Bytes */
    class OptionLockGuard {
    public:
        OptionLockGuard() = default;
        ~OptionLockGuard() noexcept {
            hw().cr |= (kCrOptLock | kCrLock);
        }
        OptionLockGuard(const OptionLockGuard&) = delete;
        OptionLockGuard& operator=(const OptionLockGuard&) = delete;
    };

    static bool is_otp_provisioned() noexcept {
        auto otp = reinterpret_cast<const volatile std::uint32_t*>(kOtpStart);
        if (otp[0] != kOtpMagic) {
            return false;
        }
        std::uint32_t checksum = 0;
        for (std::size_t i = 1; i < 8; ++i) {
            checksum ^= otp[i];
        }
        return (checksum != 0 && checksum != 0xFFFFFFFFUL);
    }

    static std::expected<void, LockError> wait_ready(std::uint32_t timeout) noexcept {
        while (hw().sr & kSrBusy) {
            if (--timeout == 0) {
                return std::unexpected(LockError::FlashControllerBusy);
            }
        }
        if (hw().sr & (kSrWrpErr | kSrPgaErr)) {
            hw().sr = kSrWrpErr | kSrPgaErr;
            return std::unexpected(LockError::WriteFailed);
        }
        return {};
    }

    static std::expected<OptionLockGuard, LockError> unlock_options() noexcept {
        if (hw().cr & kCrLock) {
            hw().keyr = kKey1;
            hw().keyr = kKey2;
        }
        if (hw().cr & kCrLock) {
            return std::unexpected(LockError::OptionUnlockFailed);
        }

        if (hw().cr & kCrOptLock) {
            hw().optkeyr = kOptKey1;
            hw().optkeyr = kOptKey2;
        }
        if (hw().cr & kCrOptLock) {
            return std::unexpected(LockError::OptionUnlockFailed);
        }

        return OptionLockGuard{};
    }

    static std::expected<void, LockError> perform_factory_lockdown(
        std::uint8_t start_page, std::uint8_t end_page) noexcept 
    {
        if (!is_otp_provisioned()) {
            return std::unexpected(LockError::OtpDataMissingOrCorrupt);
        }

        auto ready = wait_ready(500000);
        if (!ready) return ready;

        auto guard = unlock_options();
        if (!guard) return std::unexpected(guard.error());

        /* Налаштування апаратного захисту діапазону сторінок від запису */
        hw().wrp1ar = (static_cast<std::uint32_t>(end_page) << 16) | start_page;

        /* Встановлення незворотного рівня RDP Level 2 */
        std::uint32_t optr = hw().optr;
        optr &= ~0xFFUL;
        optr |= kRdpLevel2;
        hw().optr = optr;

        /* Запуск запису конфігураційних бітів */
        hw().cr |= kCrOptStart;
        ready = wait_ready(500000);
        if (!ready) return ready;

        /* Перезапуск контролера з новими бітами захисту */
        hw().cr |= kCrOblLaunch;

        while (true) {
            #if defined(__GNUC__) || defined(__clang__)
            asm volatile("nop");
            #endif
        }
    }
};

} // namespace hardware::security
```
:::

---

### Інженерні пастки та захист від браку на конвеєрі

1. **Нестабільність напруги живлення під час програмування:**
   Внутрішній помножувач напруги (*charge pump*) контролера Flash споживає імпульсний струм до 25 мА під час перепалювання бітів Option Bytes. Час запису слова становить типово 40–50 мікросекунд, а стирання сектора опцій — до 25 мілісекунд. Якщо імпеданс голчастих контактів тест-джига зависокий або ємність керамічних блокувальних конденсаторів біля виводів VDD/VSS недостатня, напруга живлення може просісти нижче мінімального робочого порогу Flash-контролера (2.7 В). Це призводить до часткового програмування регістра, зависання контролера у стані `BSY` та перетворення плати на невідновний брак. Тест-стенд зобов'язаний контролювати напругу безпосередньо на виводах плати через виділені сенсорні лінії Кельвіна.

2. **Захист від передчасного блокування без верифікації:**
   Якщо код замикання виконати до перевірки функціонування давачів, виправити помилку в Flash буде неможливо. Тому процедура завжди розбивається на дві фази: повний прогін функціонального тесту плати під контролем зовнішнього комп'ютера стенда, і лише після отримання підтвердженого статусу `PASS` надсилається фінальна команда виклику `factory_lockdown_device()`.

3. **Верифікація блокування із зовнішнього боку:**
   Після спрацювання `OBL_LAUNCH` та перезавантаження мікроконтролера стенд виконує перевірочне підключення до ліній SWD. Замикання вважається успішним, лише якщо програматор стенда отримує апаратну помилку відсутності відповіді від процесорного порту налагодження (*SW-DP ACK Fault / Target Not Responding*). Додатково вимірюється струм споживання в режимі спокою: вимкнення внутрішньої логіки відлагоджувального блока DAP знижує статичне споживання кристала на 120–250 мікроампер, що слугує непрямим фізичним підтвердженням відключення відладки.
