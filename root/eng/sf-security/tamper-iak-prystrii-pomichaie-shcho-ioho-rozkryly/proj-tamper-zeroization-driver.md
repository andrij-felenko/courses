# ⚙️ Драйвер контролера тампера з активною сіткою та апаратним зануленням

Цей проєкт містить практичну реалізацію низькорівневого драйвера апаратного контролера тампера (на базі архітектури STM32 TAMP / NXP SECURE_TAMPER) для вбудованих систем із підвищеними вимогами до безпеки. Драйвер налаштовує активну сітку з генератором псевдовипадкових послідовностей (LFSR), конфігурує пасивні сенсори, встановлює апаратне занулення резервних регістрів і забезпечує багаторівневий обробник переривання для негайного очищення пам'яті в разі фізичного вторгнення.

### Архітектура та життєвий цикл драйвера

Проєктування драйвера фізичної безпеки кардинально відрізняється від розробки звичайної периферії мікроконтролера. Помилка в драйвері UART чи I2C призводить до втрати пакета, тоді як помилка в драйвері тампера або перетворює пристрій на невідновлювану «цеглину» через хибне спрацювання, або залишає закриті ключі відкритими для зондування.

```
[Старт ініціалізації драйвера]
       │
       ▼
1. Розблокування доступу до резервної шини (PWR->CR1 |= DBP)
       │
       ▼
2. Зняття апаратного блокування запису ключами (0xCA, потім 0x53)
       │
       ▼
3. Генерація та завантаження зерна LFSR з апаратного TRNG
       │
       ▼
4. Узгодження затримок фільтрації під паразитну ємність сітки (TAMP_FLTCR)
       │
       ▼
5. Маршрутизація активних пінів TAMP_OUTx та TAMP_INx
       │
       ▼
6. Активація внутрішніх сенсорів температури, напруги та тактування
       │
       ▼
7. Налаштування апаратного занулення BKP SRAM та дозволу NMI
       │
       ▼
[Автономний захист активний 24/7/365 у всіх режимах енергозбереження]
```

#### Покрокова логіка роботи:

1. **Розблокування резервного домену (Backup Domain):** за замовчуванням після скидання доступ до резервного домену живлення `VBAT` заблокований бітом захисту в контролері живлення (`PWR_CR1_DBP`). Драйвер спершу активує цей міст.
2. **Апаратна автентифікація конфігурації:** запис двох послідовних магічних чисел `0xCA` та `0x53` у захисний регістр `TAMP_WPR` відкриває внутрішній замок конфігурації.
3. **Генерація псевдовипадкового коду сітки:** завантаження 32-бітного ентропійного значення, отриманого від апаратного генератора випадкових чисел (TRNG), у регістр `TAMP_ATSEEDR`. Це зерно визначає динамічний бітовий патерн, який неможливо підробити чи передбачити.
4. **Компенсація ємності та фільтрація завад:** налаштування попереднього заряду лінії (Precharge) для надійної роботи на гнучких поліімідних шлейфах із власною паразитною ємністю до 100 пФ.
5. **Апаратна зероїзація BKP SRAM:** на рівні кремнієвої топології сигнал тривоги безпосередньо комутує розрядні транзистори комірок пам'яті. Драйверу не потрібно чекати реакції ядра — стирання відбувається апаратно за лічені наносекунди.
6. **Програмний обробник (ISR):** при переході в переривання виконується гарантоване очищення динамічної пам'яті SRAM, скидання регістрів загального призначення процесора та вхід у вічний режим безпечного блокування (*Bricking*).

### Повна реалізація драйвера на C та C++

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

// Базові адреси периферійних модулів
#define TAMP_BASE            0x40002800U
#define BKP_BASE             0x40002850U
#define PWR_BASE             0x40007000U

// Зміщення регістрів контролера TAMP
#define TAMP_CR1_OFFSET      0x00U
#define TAMP_CR2_OFFSET      0x04U
#define TAMP_FLTCR_OFFSET    0x0CU
#define TAMP_ATCR1_OFFSET    0x20U
#define TAMP_ATSEEDR_OFFSET  0x24U
#define TAMP_IER_OFFSET      0x2CU
#define TAMP_SR_OFFSET       0x30U
#define TAMP_SCR_OFFSET      0x3CU

#define REG32(addr) (*(volatile uint32_t *)(addr))

// Бітові маски конфігурації
#define TAMP_CR1_TAMP1E      (1U << 0)  // Пасивний тампер 1 (NC контакт)
#define TAMP_CR1_ITAMP1E     (1U << 16) // Внутрішній тампер температури
#define TAMP_ATCR1_TAMP1AM   (1U << 0)  // Активний режим каналу 1 (LFSR)
#define TAMP_ATCR1_ATOSEL    (1U << 8)  // Комутація вихідного піна TAMP_OUT
#define TAMP_IER_TAMP1IE     (1U << 0)  // Дозвіл переривання
#define TAMP_SR_TAMP1F       (1U << 0)  // Прапорець вторгнення
#define TAMP_SCR_CTAMP1F     (1U << 0)  // Скидання прапорця

#define PWR_CR1_DBP          (1U << 8)  // Дозвіл доступу до Backup домену

#define BKP_REG_COUNT        32U

// Структура дескриптора драйвера
typedef struct {
    uint32_t active_seed;
    bool hardware_zeroize_enabled;
    uint32_t tamper_timestamp;
} tamper_driver_t;

// Безпечне очищення буфера (гарантовано не вирізається компілятором)
static void secure_memzero(volatile void *ptr, size_t len) {
    volatile uint8_t *p = (volatile uint8_t *)ptr;
    while (len--) {
        *p++ = 0U;
    }
}

// Ініціалізація та активація захисного контуру
bool tamper_init(tamper_driver_t *drv, uint32_t seed) {
    if (!drv || seed == 0U) {
        return false;
    }

    drv->active_seed = seed;
    drv->hardware_zeroize_enabled = true;
    drv->tamper_timestamp = 0U;

    // 1. Дозвіл доступу до регістрів резервного домену
    REG32(PWR_BASE + 0x00U) |= PWR_CR1_DBP;

    // 2. Зняття апаратного захисту запису ключами 0xCA, 0x53
    REG32(TAMP_BASE + 0x10U) = 0xCAU;
    REG32(TAMP_BASE + 0x10U) = 0x53U;

    // 3. Завантаження початкового зерна генератора LFSR
    REG32(TAMP_BASE + TAMP_ATSEEDR_OFFSET) = drv->active_seed;

    // 4. Конфігурація фільтра завад: опитування 1 Гц, глибина 4 вибірки
    REG32(TAMP_BASE + TAMP_FLTCR_OFFSET) = (0x02U << 0) | (0x01U << 3);

    // 5. Увімкнення активного режиму для захисної сітки
    REG32(TAMP_BASE + TAMP_ATCR1_OFFSET) = TAMP_ATCR1_TAMP1AM | TAMP_ATCR1_ATOSEL;

    // 6. Дозвіл переривань та активація зовнішнього і внутрішнього сенсорів
    REG32(TAMP_BASE + TAMP_IER_OFFSET) |= TAMP_IER_TAMP1IE;
    REG32(TAMP_BASE + TAMP_CR1_OFFSET) |= (TAMP_CR1_TAMP1E | TAMP_CR1_ITAMP1E);

    return true;
}

// Запис кореневого ключа в апаратні резервні регістри
void tamper_write_secret_key(const uint8_t *key, size_t key_len) {
    if (!key || key_len > (BKP_REG_COUNT * 4U)) {
        return;
    }

    const uint32_t *words = (const uint32_t *)key;
    size_t word_count = (key_len + 3U) / 4U;

    for (size_t i = 0; i < word_count; ++i) {
        REG32(BKP_BASE + (i * 4U)) = words[i];
    }
}

// Критичний обробник фізичного зламу (Tamper NMI / IRQ)
void TAMP_IRQHandler(void) {
    if (REG32(TAMP_BASE + TAMP_SR_OFFSET) & TAMP_SR_TAMP1F) {
        // Резервні регістри BKP SRAM вже обнулені апаратною шиною за 15 нс!
        // Програмно зачищаємо внутрішню системну пам'ять
        extern uint8_t _sdata, _edata, _sbss, _ebss;
        secure_memzero(&_sdata, (size_t)(&_edata - &_sdata));
        secure_memzero(&_sbss, (size_t)(&_ebss - &_sbss));

        // Фіксація події зламу в незмивному журналі
        REG32(TAMP_BASE + TAMP_SCR_OFFSET) = TAMP_SCR_CTAMP1F;

        // Незворотне перетворення пристрою на "цеглину"
        while (1) {
            __asm volatile("nop");
        }
    }
}
```
```cpp
#include <cstdint>
#include <cstddef>
#include <array>
#include <span>
#include <expected>

namespace security {

enum class TamperError {
    InvalidSeed,
    AccessDenied,
    KeyTooLarge
};

class TamperController {
private:
    static constexpr std::uintptr_t TAMP_BASE = 0x40002800U;
    static constexpr std::uintptr_t BKP_BASE  = 0x40002850U;
    static constexpr std::uintptr_t PWR_BASE  = 0x40007000U;

    static constexpr std::uint32_t TAMP_CR1_TAMP1E   = (1U << 0);
    static constexpr std::uint32_t TAMP_CR1_ITAMP1E  = (1U << 16);
    static constexpr std::uint32_t TAMP_ATCR1_TAMP1AM= (1U << 0);
    static constexpr std::uint32_t TAMP_ATCR1_ATOSEL = (1U << 8);
    static constexpr std::uint32_t TAMP_IER_TAMP1IE  = (1U << 0);
    static constexpr std::uint32_t TAMP_SR_TAMP1F    = (1U << 0);
    static constexpr std::uint32_t TAMP_SCR_CTAMP1F  = (1U << 0);
    static constexpr std::uint32_t PWR_CR1_DBP       = (1U << 8);

    static constexpr std::size_t MAX_BKP_REGS = 32;

    static volatile std::uint32_t& reg(std::uintptr_t addr) noexcept {
        return *reinterpret_cast<volatile std::uint32_t*>(addr);
    }

    static void secure_clear(std::span<volatile std::uint8_t> buffer) noexcept {
        for (auto& byte : buffer) {
            byte = 0U;
        }
    }

public:
    TamperController() = default;

    [[nodiscard]] std::expected<void, TamperError> initialize(std::uint32_t lfsr_seed) noexcept {
        if (lfsr_seed == 0U) {
            return std::unexpected(TamperError::InvalidSeed);
        }

        // 1. Дозвіл доступу до резервного домену
        reg(PWR_BASE + 0x00U) |= PWR_CR1_DBP;

        // 2. Зняття апаратного захисту конфігурації
        reg(TAMP_BASE + 0x10U) = 0xCAU;
        reg(TAMP_BASE + 0x10U) = 0x53U;

        // 3. Ініціалізація псевдовипадкового генератора активної сітки
        reg(TAMP_BASE + 0x24U) = lfsr_seed;

        // 4. Налаштування цифрового фільтра та часу попереднього заряду
        reg(TAMP_BASE + 0x0CU) = (0x02U << 0) | (0x01U << 3);
        reg(TAMP_BASE + 0x20U) = TAMP_ATCR1_TAMP1AM | TAMP_ATCR1_ATOSEL;

        // 5. Активація переривань та моніторингу сітки й температури
        reg(TAMP_BASE + 0x2CU) |= TAMP_IER_TAMP1IE;
        reg(TAMP_BASE + 0x00U) |= (TAMP_CR1_TAMP1E | TAMP_CR1_ITAMP1E);

        return {};
    }

    [[nodiscard]] std::expected<void, TamperError> write_master_key(std::span<const std::uint8_t> key) noexcept {
        if (key.size() > MAX_BKP_REGS * sizeof(std::uint32_t)) {
            return std::unexpected(TamperError::KeyTooLarge);
        }

        const auto* words = reinterpret_cast<const std::uint32_t*>(key.data());
        const std::size_t word_count = (key.size() + sizeof(std::uint32_t) - 1) / sizeof(std::uint32_t);

        for (std::size_t i = 0; i < word_count; ++i) {
            reg(BKP_BASE + (i * sizeof(std::uint32_t))) = words[i];
        }

        return {};
    }

    static void handle_tamper_event() noexcept {
        if (reg(TAMP_BASE + 0x30U) & TAMP_SR_TAMP1F) {
            // Апаратна зероїзація BKP регістрів виконана апаратно шиною Zeroize!
            // Додатково стираємо оперативну пам'ять
            extern std::uint8_t _sdata, _edata, _sbss, _ebss;
            secure_clear(std::span<volatile std::uint8_t>{
                reinterpret_cast<volatile std::uint8_t*>(&_sdata),
                static_cast<std::size_t>(&_edata - &_sdata)
            });
            secure_clear(std::span<volatile std::uint8_t>{
                reinterpret_cast<volatile std::uint8_t*>(&_sbss),
                static_cast<std::size_t>(&_ebss - &_sbss)
            });

            // Фіксація події
            reg(TAMP_BASE + 0x3CU) = TAMP_SCR_CTAMP1F;

            // Вічне блокування системи
            while (true) {
                asm volatile("nop");
            }
        }
    }
};

} // namespace security
```
:::

### Інженерні пастки, бар'єри пам'яті та захист від оптимізацій

Під час реалізації драйверів аварійного занулення інженери стикаються з низкою підступних апаратних і компіляторних пасток:

#### 1. Компіляторна оптимізація функцій очищення пам'яті

Найбільш критична помилка в коді безпеки — використання стандартної функції `memset(secret, 0, len)`. Оптимізуючий компілятор (GCC або Clang із прапорцями `-O2` чи `-O3`) аналізує граф потоку даних і визначає, що буфер `secret` після завершення процедури більше ніде не читається. Оскільки з точки зору абстрактної машини C такий запис не має спостережуваних побічних ефектів, компілятор повністю викидає інструкцію занулення як «мертвий код» (Dead Store Elimination).

У результаті секретний ключ залишається у відкритому вигляді в комірках статичної пам'яті. Щоб запобігти цьому, необхідно застосовувати явні бар'єри пам'яті або `volatile`-вказівники:

:::tabs
```c
// Надійне занулення з бар'єром пам'яті для архітектури ARM Cortex-M
void secure_zeroize_block(void *ptr, size_t len) {
    volatile uint8_t *p = (volatile uint8_t *)ptr;
    while (len--) {
        *p++ = 0x00U;
    }
    __asm volatile("" : : "r"(ptr) : "memory");
    __asm volatile("dsb sy\n isb" : : : "memory");
}
```
```cpp
// Ідіоматичне занулення зі std::span та бар'єром пам'яті
void secure_zeroize_block(std::span<volatile std::uint8_t> buffer) noexcept {
    for (auto& byte : buffer) {
        byte = 0x00U;
    }
    asm volatile("" : : "r"(buffer.data()) : "memory");
    asm volatile("dsb sy\n isb" : : : "memory");
}
```
:::

Інструкція `dsb sy` (Data Synchronization Barrier) змушує ядро процесора завершити всі незавершені транзакції запису на системній шині до виконання наступних інструкцій, а `isb` (Instruction Synchronization Barrier) скидає конвеєр вибірки команд.

#### 2. Захист від атак збоями (Glitch-Resistant Control Flow)

Зловмисник, що застосовує лазерне опромінення кристала або глітчинг напруги живлення, може викликати збій у виконанні інструкції умовного переходу `if (tamper_detected)`. Якщо в лічильнику команд зміниться один біт, процесор може перестрибнути блок виклику функції зачищення пам'яті.

Для нейтралізації таких атак в обробниках тривоги застосовують **подвійну перевірку з надлишковими змінними**:

:::tabs
```c
volatile uint32_t security_token = 0x55AA55AAU;

void HardFault_or_Tamper_Handler(void) {
    uint32_t status1 = REG32(TAMP_BASE + TAMP_SR_OFFSET);
    if ((status1 & TAMP_SR_TAMP1F) == TAMP_SR_TAMP1F) {
        security_token ^= 0x12345678U;
    }

    // Повторна незалежна перевірка через альтернативний регістр
    uint32_t status2 = REG32(TAMP_BASE + TAMP_MISR_OFFSET);
    if ((status2 & TAMP_SR_TAMP1F) == TAMP_SR_TAMP1F && security_token == (0x55AA55AAU ^ 0x12345678U)) {
        perform_irreversible_zeroization();
    } else {
        // Якщо сталася аномалія потоку виконання — все одно виконуємо стирання
        perform_irreversible_zeroization();
    }
}
```
```cpp
namespace security {

inline volatile std::uint32_t security_token = 0x55AA55AAU;

void handle_tamper_fault() noexcept {
    const std::uint32_t status1 = *reinterpret_cast<volatile std::uint32_t*>(TAMP_BASE + 0x30U);
    if ((status1 & (1U << 0)) == (1U << 0)) {
        security_token ^= 0x12345678U;
    }

    const std::uint32_t status2 = *reinterpret_cast<volatile std::uint32_t*>(TAMP_BASE + 0x34U);
    if ((status2 & (1U << 0)) == (1U << 0) && security_token == (0x55AA55AAU ^ 0x12345678U)) {
        perform_irreversible_zeroization();
    } else {
        perform_irreversible_zeroization();
    }
}

} // namespace security
```
:::

#### 3. Виробниче калібрування та тестування на конвеєрі

Перед тим як пристрій буде запечатаний у корпус і переданий кінцевому користувачу, підсистема тампера проходить процедуру верифікації на складальному конвеєрі:
- **Перевірка опору сітки:** замір падіння напруги на виводах `TAMP_IN` при подачі тестового струму для виявлення дефектів травлення плати.
- **Тест без занулення (Test Mode):** спеціальний біт конфігурації дозволяє ініціалізувати генератор LFSR і перевірити проходження бітової послідовності крізь зовнішній шлейф без активації безповоротного стирання BKP SRAM.
- **Фінальне знеструмлення джампера тестового режиму:** перепалювання одноразового запобіжника (eFuse) назавжди активує режим бойового чергування. З цього моменту будь-яке розмикання контуру активує незворотну апаратну зероїзацію.

#### 4. Пріоритет переривань та захист від інверсії пріоритетів

У системі з великою кількістю периферії (DMA, Ethernet, USB, таймери ШІМ) існує ризик, що обробник тампера буде заблокований тривалим виконанням іншого високопріоритетного переривання.

Щоб гарантувати негайну реакцію, обробник тампера в контролері векторних переривань NVIC налаштовують на абсолютний пріоритет `0` (найвищий можливий пріоритет переривання ядра Cortex-M). Крім того, на рівні ядра призначається немасковане переривання (NMI), яке неможливо вимкнути інструкцією `__disable_irq()` або прапорцем `PRIMASK`. Це унеможливлює зависання аварійного алгоритму в критичних секціях користувацької операційної системи.

#### 5. Керування режимами енергозбереження та переходи живлення

У системах із тривалим автономним живленням процесор більшу частину часу проводить у глибоких режимах енергозбереження (`Stop`, `Standby` або `Shutdown`). Перед переходом у ці режими драйвер повинен виконати спеціальну послідовність налаштувань:

- **Ізоляція виводів GPIO:** стандартні цифрові буфери виводів відключаються від шини живлення ядра, щоб запобігти паразитним струмам витоку. Керування виводами `TAMP_IN` та `TAMP_OUT` повністю передається аналоговому блоку резервного домену `VBAT`.
- **Тактування від LSE під час сну:** генератор активної сітки перемикається на низькочастотний кварцовий генератор LSE (32.768 кГц), який залишається активним навіть при повній зупинці системних генераторів HSI/HSE/PLL.
- **Пробудження за подією тампера:** у регістрі пробудження системи конфігурується прапорець `WUP_TAMP`. При фіксації вторгнення мікроконтролер не лише виконує миттєву апаратну зероїзацію BKP SRAM, але й генерує сигнал пробудження, змушуючи процесор негайно запустити підсистему аварійної безпеки.
