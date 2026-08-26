# ⚙️ Контролер анти-темпер захисту та процедура гарантованого стирання на C/C++

У захищених вбудованих системах криптографічний ключ або конфіденційний токен у відкритому вигляді має існувати в оперативній пам'яті лише на час виконання конкретної криптографічної операції. При виникненні будь-якої нештатної ситуації — спрацюванні апаратного датчика відкриття корпусу (тампера), критичної помилки перевірки цілісності або отримання зовнішньої команди аварійного очищення — прошивка зобов'язана негайно запустити процедуру **гарантованого стирання** (англ. *Zeroization*, де *zeroize* — довести до нульового стану).

Цей проєкт демонструє повноцінний, апаратно-незалежний модуль контролера безпеки та гарантованого очищення конфіденційної пам'яті мовами C та C++.

---

## 1. Архітектурна задача та пастки реалізації

При створенні модуля аварійного самоочищення інженер стикається з трьома критичними пастками:

1. **Оптимізація мертвого коду (Dead Store Elimination).** Якщо написати звичайний `memset(key_buffer, 0, key_len)`, а після цього функція повертає керування і буфер більше не читається, оптимізуючий компілятор (GCC або Clang із прапорцями `-O2` чи `-O3`) **повністю викине** виклик `memset`, вважаючи його непотрібною витратою процесорних тактів. У результаті ключ залишиться у відкритому вигляді в стеку або динамічній пам'яті.
2. **Асинхронне виконання в обробнику переривань (ISR).** Подія тампера надходить як апаратне переривання з найвищим пріоритетом. Обробник не має права викликати блокуючі функції ОС (м'ютекси, виділення динамічної пам'яті, повільне стирання Flash через SPI). Він зобов'язаний за наносекунди очистити швидкі регістраційні сховища (Backup SRAM, регістри ядра, кеші ключів) і лише потім ініціювати фоновий процес стирання енергонезалежної пам'яті.
3. **Витік через тимчасові копії у стеку.** Під час копіювання, передачі за значенням або форматування секретів у пам'яті залишаються тимчасові фрейми функцій. Модуль повинен забезпечувати автоматичне стирання кожного буфера в мить виходу з області видимості за принципом RAII.
4. **Конкурентний доступ через канали DMA.** Якщо в мить спрацювання тампера контролер прямого доступу до пам'яті (DMA) виконує передачу шифротексту або завантаження ключа, просте програмне занулення буфера в SRAM буде перезаписане апаратним каналом DMA. Тому перший крок аварійної процедури вимагає негайного вимкнення всіх потоків DMA та очищення їхніх внутрішніх FIFO-буферів.

---

## 2. Реалізація захищеного контролера мовами C та C++

У мові C для запобігання оптимізації компілятора використовується покажчик із кваліфікатором `volatile` разом із вбудованим інструкційним бар'єром пам'яті (`__asm__ __volatile__`). У мові C++ реалізовано шаблонний RAII-контейнер `SecureKeyBuffer`, який автоматично викликає безпечне занулення пам'яті в деструкторі та використовує `std::atomic_signal_fence` для гарантованого фізичного запису нулів у шину:

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

#define MASTER_KEY_SIZE_BYTES   32U
#define FLASH_SECTOR_SIZE_BYTES 4096U
#define TAMPER_MAGIC_TOKEN      0xDEADBEEFU

typedef enum {
    SECURITY_STATE_LOCKED = 0,
    SECURITY_STATE_UNLOCKED,
    SECURITY_STATE_TAMPERED,
    SECURITY_STATE_ZEROIZED
} SecurityState;

typedef struct {
    SecurityState state;
    uint8_t master_key[MASTER_KEY_SIZE_BYTES];
    volatile bool tamper_detected;
} SecurityController;

// Апаратні абстракції для взаємодії з периферією кристала
extern void hw_backup_sram_wipe(void);
extern void hw_dma_abort_all_transfers(void);
extern void hw_flash_erase_sector(uint32_t sector_addr);
extern void hw_efuse_burn_security_lock(void);
extern void hw_disable_all_peripherals(void);
extern void hw_trigger_system_reset(void);

/**
 * Гарантоване занулення пам'яті, яке ніколи не викидається оптимізатором
 */
void secure_memzero(void *ptr, size_t len) {
    if (ptr == NULL || len == 0) {
        return;
    }
    volatile uint8_t *vptr = (volatile uint8_t *)ptr;
    while (len--) {
        *vptr++ = 0x00U;
    }
    // Бар'єр пам'яті для запобігання перестановок інструкцій компілятором
    __asm__ __volatile__("" : : "r"(ptr) : "memory");
}

void security_controller_init(SecurityController *ctrl) {
    if (!ctrl) return;
    ctrl->state = SECURITY_STATE_LOCKED;
    ctrl->tamper_detected = false;
    secure_memzero(ctrl->master_key, MASTER_KEY_SIZE_BYTES);
}

bool security_controller_load_key(SecurityController *ctrl, const uint8_t *key_in, size_t len) {
    if (!ctrl || !key_in || len != MASTER_KEY_SIZE_BYTES) {
        return false;
    }
    if (ctrl->state == SECURITY_STATE_TAMPERED || ctrl->tamper_detected) {
        return false;
    }

    for (size_t i = 0; i < MASTER_KEY_SIZE_BYTES; ++i) {
        ctrl->master_key[i] = key_in[i];
    }
    ctrl->state = SECURITY_STATE_UNLOCKED;
    return true;
}

/**
 * Асинхронний обробник переривання апаратного тампера (Tamper ISR).
 * Виконується з найвищим пріоритетом (час виконання < 10 мкс).
 */
void Security_Tamper_IRQHandler(SecurityController *ctrl) {
    if (!ctrl) return;

    // 1. Зупинка всіх каналів DMA для запобігання перезапису пам'яті
    hw_dma_abort_all_transfers();

    // 2. Миттєвий апаратний скид регістрів Backup SRAM
    hw_backup_sram_wipe();

    // 3. Гарантоване занулення ключів у RAM ядра
    secure_memzero(ctrl->master_key, MASTER_KEY_SIZE_BYTES);
    ctrl->state = SECURITY_STATE_TAMPERED;
    ctrl->tamper_detected = true;

    // 4. Запуск повного циклу стирання Flash
    for (uint32_t addr = 0; addr < (1024U * 1024U); addr += FLASH_SECTOR_SIZE_BYTES) {
        hw_flash_erase_sector(addr);
    }

    // 5. Спалювання eFuse та блокування SWD/JTAG
    hw_efuse_burn_security_lock();

    // 6. Повне відключення та апаратний перезапуск у стан блокування
    hw_disable_all_peripherals();
    hw_trigger_system_reset();
}
```
```cpp
#include <cstdint>
#include <cstddef>
#include <span>
#include <concepts>
#include <atomic>
#include <utility>

namespace security {

enum class State : uint8_t {
    Locked = 0,
    Unlocked,
    Tampered,
    Zeroized
};

template <size_t KeySize>
class alignas(uint32_t) SecureKeyBuffer {
public:
    constexpr SecureKeyBuffer() noexcept {
        clear();
    }

    explicit SecureKeyBuffer(std::span<const uint8_t, KeySize> source) noexcept {
        assign(source);
    }

    ~SecureKeyBuffer() noexcept {
        clear();
    }

    // Забороняємо неявне копіювання, щоб уникнути витоку дублікатів у стек
    SecureKeyBuffer(const SecureKeyBuffer&) = delete;
    SecureKeyBuffer& operator=(const SecureKeyBuffer&) = delete;

    SecureKeyBuffer(SecureKeyBuffer&& other) noexcept {
        assign(std::span<const uint8_t, KeySize>(other.data_, KeySize));
        other.clear();
    }

    SecureKeyBuffer& operator=(SecureKeyBuffer&& other) noexcept {
        if (this != &other) {
            clear();
            assign(std::span<const uint8_t, KeySize>(other.data_, KeySize));
            other.clear();
        }
        return *this;
    }

    void assign(std::span<const uint8_t, KeySize> source) noexcept {
        clear();
        for (size_t i = 0; i < KeySize; ++i) {
            data_[i] = source[i];
        }
    }

    void clear() noexcept {
        volatile uint8_t* p = data_;
        for (size_t i = 0; i < KeySize; ++i) {
            p[i] = 0x00U;
        }
        std::atomic_signal_fence(std::memory_order_seq_cst);
    }

    [[nodiscard]] std::span<const uint8_t, KeySize> view() const noexcept {
        return std::span<const uint8_t, KeySize>(data_, KeySize);
    }

private:
    uint8_t data_[KeySize]{};
};

template <typename HardwareInterface>
class TamperGuard {
public:
    static constexpr size_t MasterKeyBytes = 32;

    explicit TamperGuard(HardwareInterface& hw) noexcept
        : hw_(hw), state_(State::Locked), tamperActive_(false) {}

    ~TamperGuard() noexcept {
        emergencyZeroize();
    }

    [[nodiscard]] bool loadMasterKey(std::span<const uint8_t, MasterKeyBytes> key) noexcept {
        if (tamperActive_.load(std::memory_order_relaxed) || state_ == State::Tampered) {
            return false;
        }
        keyBuffer_.assign(key);
        state_ = State::Unlocked;
        return true;
    }

    void handleTamperInterrupt() noexcept {
        tamperActive_.store(true, std::memory_order_seq_cst);
        emergencyZeroize();
    }

    void emergencyZeroize() noexcept {
        // 1. Аварійна зупинка передач DMA
        hw_.abortDmaTransfers();

        // 2. Миттєве скидання апаратного сховища Backup SRAM
        hw_.wipeBackupSram();

        // 3. Гарантоване затирання оперативної пам'яті через RAII-буфер
        keyBuffer_.clear();
        state_ = State::Zeroized;

        // 4. Повне стирання Flash-пам'яті
        hw_.eraseAllFlashPartitions();

        // 5. Перепалювання eFuse захисту та перезавантаження
        hw_.burnPermanentSecurityLock();
        hw_.systemReset();
    }

    [[nodiscard]] State getState() const noexcept { return state_; }

private:
    HardwareInterface& hw_;
    SecureKeyBuffer<MasterKeyBytes> keyBuffer_{};
    State state_;
    std::atomic<bool> tamperActive_{false};
};

} // namespace security
```
:::

---

## 3. Регістрова послідовність на кристалах STM32 та ESP32

Щоб захист працював на фізичному рівні, прошивка повинна налаштувати апаратну периферію TAMP мікроконтролера під час запуску в завантажувачі:

### Налаштування периферії STM32 TAMP:

1. **Активація тактування домену живлення Backup (PWR_CR1.DBP = 1):** Зняття захисту від запису в регістри резервного домену RTC і TAMP.
2. **Конфігурація активного рівня виводів (TAMP_CR1 / TAMP_CR2):** Призначення пінів `TAMP1` (кнопка кришки) та `TAMP2` (активна сітка) з налаштуванням полярності (спрацювання по спадному фронту при розриві петлі).
3. **Увімкнення апаратного самоочищення (TAMP_IER.TAMP1IE = 1):** Активація режиму, в якому апаратний блок автоматично очищає всі 32 регістри `RTC_BKPxR` і Backup SRAM без участі процесорного ядра.
4. **Призначення переривання TAMP_STAMP_IRQHandler:** Встановлення найвищого пріоритету (NVIC Priority 0) для виклику аварійного обробника ядра.

### Налаштування домену ESP32 RTC IO:

1. **Конфігурація пінів RTC GPIO:** Переведення пінів `GPIO0` / `GPIO4` у режим RTC IO під керуванням копроцесора низького енергоспоживання ULP.
2. **Встановлення функції пробудження (ext0 / ext1 wakeup):** Налаштування спрацювання при зміні логічного рівня на тампер-піні під час глибокого сну (Deep Sleep).
3. **Очищення RTC Fast/Slow SRAM:** При виявленні розмикання ULP копроцесор виконує циклічний запис нулів у масив `RTC_SLOW_MEM` ще до повного пробудження головних ядер Xtensa/RISC-V.

---

## 4. Перевірка стійкості до оптимізацій через асемблерний аналіз

Щоб перевірити, що процедура занулення пам'яті не була викинута компілятором, інженер зобов'язаний переглянути результуючий асемблерний лістинг (через `arm-none-eabi-objdump -d`):

```asm
# Асемблерний вивід ARM Cortex-M для secure_memzero
secure_memzero:
    cbz     r1, .L_exit        @ якщо довжина len == 0, негайно виходимо
.L_loop:
    movs    r2, #0             @ завантажуємо константу 0x00 у регістр r2
    strb    r2, [r0], #1       @ записуємо 0 у пам'ять за адресою r0 з автоінкрементом
    subs    r1, r1, #1         @ зменшуємо лічильник байтів: len = len - 1
    bne     .L_loop            @ якщо не нуль, переходимо на наступну ітерацію циклу
    dmb     sy                 @ повний системний бар'єр пам'яті (Data Memory Barrier)
.L_exit:
    bx      lr                 @ повернення з функції
```

Інструкція `strb r2, [r0], #1` у тісному циклі разом із системним бар'єром пам'яті `dmb sy` гарантує, що компілятор не проігнорує жодного запису. Процесор виконає реальні цикли транзакцій запису по шині AHB/AXI у фізичні комірки пам'яті SRAM, унеможливлюючи відновлення залишків криптографічних ключів чи сесійних токенів.

---

## 5. Методологія тестування та валідації надійності (Fault Injection Testing)

Для сертифікації модуля безпеки розробник проводить серію стрес-тестів на випробувальному стенді:

1. **Тест раптового знеструмлення (Power Cutoff Verification):** Плата вмикається, завантажує ключ у пам'ять, після чого імітується спрацювання тампера і рівно через `200 мкс` силове живлення `VDD` примусово відключається ключем на польовому транзисторі. Плата живиться лише від батарейки `VBAT`. Після повторного запуску діагностична утиліта зчитує дамп Backup SRAM і перевіряє, що всі байти містять виключно `0x00`.
2. **Атака тепловим градієнтом (Cryogenic Freeze Simulation):** Модуль охолоджується в кліматичній камері до `-40 °C`. Ініціюється подія тампера, після чого кристал досліджується за допомогою JTAG-емулятора для підтвердження того, що залишковий заряд у замерзлих комірках пам'яті було примусово розряджено внутрішньою схемою заземлення шин.
3. **Валідація незворотності eFuse:** Перевірка зчитування регістрів стану контролера одноразової пам'яті, що підтверджує фізичне перепалювання плавких перемичок та блокування ліній SWDIO і SWCLK на рівні вхідних логічних вентилів процесора.
