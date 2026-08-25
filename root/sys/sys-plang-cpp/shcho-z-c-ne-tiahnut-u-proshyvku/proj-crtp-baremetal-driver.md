# ⚙️ Драйвер периферії без купи й vtable: CRTP та обробка помилок

Під час розробки прошивок для мікроконтролерів (наприклад, лінійок ARM Cortex-M або RISC-V) виникає потреба створити єдиний протокольний рівень для взаємодії з різними послідовними інтерфейсами (UART, SPI, I2C). Класичне об'єктно-орієнтоване проектування на базі динамічного поліморфізму вимагає створення базового абстрактного класу з віртуальними функціями (`virtual`). Однак у вбудованих системах цей підхід спричиняє відчутні втрати продуктивності та пам'яті: кожен об'єкт отримує додатковий прихований покажчик на таблицю методів (`vptr`), виклики функцій перетворюються на непрямі переходи через регістри процесора (`BLX`), а компілятор втрачає можливість виконувати підстановку тіла функцій (інлайнінг) та міжпроцедурну оптимізацію бітових масок.

Нижче розібрано повний інженерний процес побудови нуль-оверхедного драйвера пакетної передачі даних із розрахунком контрольної суми CRC. Реалізація виконана повністю без динамічної пам'яті (купи), без винятків та без віртуальних таблиць, опираючись на статичний поліморфізм CRTP (англ. *Curiously Recurring Template Pattern*) та сучасну семантику обробки помилок через значення `std::expected`.

---

## 1. Архітектурне протистояння: чому vtable шкодить периферійним драйверам

Щоб зрозуміти, чому віртуальні таблиці є небажаними для низькорівневих драйверів, розглянемо шлях машинної інструкції при виклику поліморфного методу на мікроконтролері ARM Cortex-M4.

Коли процесор виконує виклик `interface->send_byte(0x55)`, відбуваються такі операції:
1. Завантаження адреси таблиці віртуальних методів (`vtable`) із пам'яті об'єкта в регістр процесора через зміщення `offsetof(vptr)` (інструкція `LDR R3, [R0, #0]`).
2. Завантаження адреси цільової функції з потрібного слота `vtable` у Flash-пам'яті (інструкція `LDR R3, [R3, #4]`).
3. Непрямий перехід за завантаженою адресою (інструкція `BLX R3`).

У мікроконтролерах із три- або п'ятиступеневим конвеєром (Pipeline) непрямий перехід `BLX` призводить до очищення конвеєра інструкцій, оскільки блок передвибірки (Prefetch Unit) не може завчасно вгадати адресу переходу без блоку динамічного передбачення розгалужень (Branch Target Buffer). Це додає від 2 до 4 тактів простою процесора на кожен відправлений байт.

```
┌─────────────────────────────────────────────────────────────┐
│                 PacketTransceiver<Derived>                  │
│       Базовий протокольний рівень (форматування, CRC)       │
└──────────────────────────────┬──────────────────────────────┘
                               │ Статичний зв'язок (CRTP)
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                     Stm32UartDriver                         │
│           Прямий запис у регістри периферії MCU             │
└─────────────────────────────────────────────────────────────┘
```

Статичний поліморфізм CRTP вирішує цю проблему принципово інакше. Базовий клас є шаблоном, який приймає тип похідного класу як шаблонний аргумент: `class Stm32UartDriver : public PacketTransceiver<Stm32UartDriver>`. Всередині базового класу доступ до апаратних методів здійснюється через приведення `static_cast<Derived*>(this)->send_byte(...)`. 

Оскільки компілятор на етапі збирання точно знає кінцевий тип об'єкта, непрямий виклик взагалі не генерується. Замість цього тіло методу запису в регістр підставляється безпосередньо в протокольний цикл, усуваючи будь-які накладні витрати часу виконання.

---

## 2. Реалізація драйвера: C проти сучасного C++ (CRTP + std::expected)

Порівняємо дві закінчені реалізації протокольного драйвера: процедурний підхід мовою C (із передачею покажчика на структуру стану) та типізовану реалізацію мовою C++20 зі статичним поліморфізмом та захистом від помилок через `std::expected`.

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

/* Коди результату виконання операцій */
typedef enum {
    DRIVER_OK = 0,
    DRIVER_ERR_BUFFER_OVERFLOW,
    DRIVER_ERR_HARDWARE_TIMEOUT,
    DRIVER_ERR_BUSY
} DriverStatus;

/* Структура апаратних регістрів UART (відповідає адресній карті мікроконтролера) */
typedef struct {
    volatile uint32_t ISR; /* Регістр прапорців стану та переривань */
    volatile uint32_t RDR; /* Регістр прийому вхідних даних */
    volatile uint32_t TDR; /* Регістр передачі вихідних даних */
} HardwareUartRegs;

#define UART_ISR_TXE  (1U << 7) /* Прапорець: буфер передавача готовий до запису */

/* Структура драйвера в процедурному стилі C */
typedef struct {
    HardwareUartRegs* regs;
    uint32_t timeout_cycles;
} UartDriverC;

/* Обчислення контрольної суми CRC-8 (поліном 0x07) */
static inline uint8_t calculate_crc8(const uint8_t* data, size_t len) {
    uint8_t crc = 0x00;
    for (size_t i = 0; i < len; ++i) {
        crc ^= data[i];
        for (uint8_t b = 0; b < 8; ++b) {
            if (crc & 0x80) {
                crc = (uint8_t)((crc << 1) ^ 0x07);
            } else {
                crc = (uint8_t)(crc << 1);
            }
        }
    }
    return crc;
}

/* Відправка одного байта з контролем апаратного таймауту */
static DriverStatus uart_send_byte(UartDriverC* self, uint8_t byte) {
    uint32_t counter = self->timeout_cycles;
    while (!(self->regs->ISR & UART_ISR_TXE)) {
        if (--counter == 0) {
            return DRIVER_ERR_HARDWARE_TIMEOUT;
        }
    }
    self->regs->TDR = byte;
    return DRIVER_OK;
}

/* Формування та відправка протокольного кадру */
DriverStatus uart_transmit_packet(UartDriverC* self, const uint8_t* payload, size_t len) {
    if (len > 254) {
        return DRIVER_ERR_BUFFER_OVERFLOW;
    }

    /* 1. Заголовок кадру 0xAA */
    DriverStatus status = uart_send_byte(self, 0xAA);
    if (status != DRIVER_OK) return status;

    /* 2. Байт довжини корисних даних */
    status = uart_send_byte(self, (uint8_t)len);
    if (status != DRIVER_OK) return status;

    /* 3. Корисне навантаження */
    for (size_t i = 0; i < len; ++i) {
        status = uart_send_byte(self, payload[i]);
        if (status != DRIVER_OK) return status;
    }

    /* 4. Контрольна сума CRC */
    uint8_t crc = calculate_crc8(payload, len);
    return uart_send_byte(self, crc);
}
```
```cpp
#include <cstdint>
#include <cstddef>
#include <span>
#include <expected>
#include <concepts>

/* Типобезпечні коди помилок драйвера */
enum class DriverError : uint8_t {
    BufferOverflow,
    HardwareTimeout,
    Busy
};

/* Апаратні регістри мікроконтролера */
struct HardwareUartRegs {
    volatile uint32_t ISR;
    volatile uint32_t RDR;
    volatile uint32_t TDR;
};

inline constexpr uint32_t UART_ISR_TXE = (1U << 7);

/* Базовий протокольний клас CRTP (Static Polymorphism) */
template <typename Derived>
class PacketTransceiver {
public:
    /* Відправка пакета без використання винятків і динамічної пам'яті */
    [[nodiscard]] std::expected<size_t, DriverError> 
    transmit_packet(std::span<const uint8_t> payload) noexcept {
        if (payload.size() > 254) {
            return std::unexpected(DriverError::BufferOverflow);
        }

        /* Доступ до похідного класу через static_cast під час компіляції */
        auto& hw = static_cast<Derived&>(*this);

        /* 1. Заголовок кадру */
        if (auto res = hw.send_byte(0xAA); !res) {
            return std::unexpected(res.error());
        }

        /* 2. Довжина даних */
        if (auto res = hw.send_byte(static_cast<uint8_t>(payload.size())); !res) {
            return std::unexpected(res.error());
        }

        /* 3. Корисне навантаження */
        for (const uint8_t byte : payload) {
            if (auto res = hw.send_byte(byte); !res) {
                return std::unexpected(res.error());
            }
        }

        /* 4. Контрольна сума CRC-8 */
        const uint8_t crc = calculate_crc8(payload);
        if (auto res = hw.send_byte(crc); !res) {
            return std::unexpected(res.error());
        }

        return payload.size() + 3; /* Загальна кількість переданих байтів */
    }

protected:
    /* Захищений деструктор запобігає поліморфному видаленню */
    ~PacketTransceiver() = default;

private:
    [[nodiscard]] static constexpr uint8_t calculate_crc8(std::span<const uint8_t> data) noexcept {
        uint8_t crc = 0x00;
        for (const uint8_t b : data) {
            crc ^= b;
            for (uint8_t bit = 0; bit < 8; ++bit) {
                if (crc & 0x80) {
                    crc = static_cast<uint8_t>((crc << 1) ^ 0x07);
                } else {
                    crc = static_cast<uint8_t>(crc << 1);
                }
            }
        }
        return crc;
    }
};

/* Конкретний драйвер апаратного UART для STM32 */
class Stm32UartDriver : public PacketTransceiver<Stm32UartDriver> {
public:
    constexpr explicit Stm32UartDriver(HardwareUartRegs* regs, uint32_t timeout_cycles = 10000) noexcept
        : m_regs(regs), m_timeout(timeout_cycles) {}

    /* Прямий запис у периферійні регістри (компілятор інлайнить цей метод) */
    [[nodiscard]] std::expected<void, DriverError> send_byte(uint8_t byte) noexcept {
        uint32_t counter = m_timeout;
        while (!(m_regs->ISR & UART_ISR_TXE)) {
            if (--counter == 0) {
                return std::unexpected(DriverError::HardwareTimeout);
            }
        }
        m_regs->TDR = byte;
        return {};
    }

private:
    HardwareUartRegs* m_regs;
    uint32_t m_timeout;
};
```
:::

---

## 3. Розбір машинних інструкцій та поведінки конвеєра

Проаналізуємо асемблерний лістинг, згенерований компілятором GCC (`arm-none-eabi-g++ -O2 -mcpu=cortex-m4 -fno-exceptions -fno-rtti`) для виклику методу `transmit_packet`.

```assembly
# Машинний код циклу опитування прапорця TXE та відправки байта:
.L_send_wait:
    ldr     r3, [r0, #0]         @ Завантаження значення регістру ISR (m_regs->ISR)
    tst     r3, #128             @ Перевірка біта 7 (UART_ISR_TXE)
    bne     .L_tx_ready          @ Якщо біт встановлено — буфер готовий
    subs    r2, r2, #1           @ Зменшення лічильника таймауту
    bne     .L_send_wait         @ Повтор циклу очікування
    movs    r0, #1               @ Запис коду помилки DriverError::HardwareTimeout
    bx      lr                   @ Повернення з функції

.L_tx_ready:
    strb    r1, [r0, #8]         @ Прямий запис байта в регістр TDR (зміщення 8 байтів)
    movs    r0, #0               @ Запис прапорця успіху
    bx      lr                   @ Повернення з функції
```

### Порівняльний аналіз метрик ефективності

Вивчення згенерованого машинного коду демонструє три фундаментальні переваги перед віртуальною диспетчеризацією:

1. **Відсутність непрямих переходів**: У згенерованому коді немає жодної інструкції `BLX` чи таблиці переходів. Компілятор повністю прибрав абстрактну межу між `PacketTransceiver` та `Stm32UartDriver`. Весь протокольний алгоритм перетворився на лінійну послідовність інструкцій прямого запису в пам'ять `STRB`.
2. **Розмір структури в оперативній пам'яті (SRAM)**:
   - Розмір об'єкта `Stm32UartDriver` складає рівно 8 байтів (4 байти на покажчик `HardwareUartRegs*` та 4 байти на поле `m_timeout`).
   - Якби ми використовували класичний `virtual void send_byte()`, розмір об'єкта збільшився б до 12 байтів через приховане поле `vptr`. У системі з десятками каналів зв'язку та буферами це створює помітні непродуктивні витрати SRAM.
3. **Оптимізація обробки помилок**: Тип `std::expected<void, DriverError>` розгортається компілятором у повернення простого цілочисельного значення через регістр `R0`. Виклик не вимагає виділення динамічної пам'яті для об'єкта винятку та не звертається до секцій розгортання стеку `.ARM.exidx`.

---

## 4. Інженерні рекомендації та крайові випадки

Під час проектування периферійних драйверів на базі CRTP слід дотримуватися чотирьох правил безпеки:

1. **Контроль концепцій (C++20 Concepts)**: Щоб запобігти незрозумілим помилкам компіляції при випадковій передачі некоректного типу в шаблон, слід обмежувати базовий клас концепцією:
   ```cpp
   template <typename T>
   concept ByteTransmitter = requires(T t, uint8_t b) {
       { t.send_byte(b) } -> std::same_as<std::expected<void, DriverError>>;
   };
   ```
2. **Захищений невіртуальний деструктор**: Базовий клас CRTP ніколи не повинен мати публічний віртуальний деструктор (`virtual ~PacketTransceiver()`), оскільки це миттєво додасть `vptr` до класу. Деструктор оголошується захищеним (`protected ~PacketTransceiver() = default;`), що забороняє помилкове видалення об'єкта похідного класу через покажчик на базовий шаблон.
3. **Використання `std::span` замість покажчиків і довжини**: Передача буферів через `std::span<const uint8_t>` гарантує типобезпеку без динамічного виділення пам'яті. Метод однаково ефективно працює як зі статичними масивами `std::array<uint8_t, N>`, так і з буферами у Flash-пам'яті або локальними змінними на стеку.
4. **Бар'єри пам'яті при роботі з DMA**: Якщо драйвер розширюється для роботи з прямим доступом до пам'яті (DMA), операції запису в буфери повинні супроводжуватися інструкціями бар'єрів пам'яті (`__DMB()` — Data Memory Barrier), щоб запобігти перевпорядкуванню інструкцій оптимізатором компілятора до того, як апаратний контролер DMA почне читання пам'яті.
