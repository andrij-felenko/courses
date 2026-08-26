# ⚙️ Розробка регістрового драйвера за Reference Manual: від карти адрес до безпечного коду

Коли виробник постачає новий мікроконтролер, готових високорівневих бібліотек часто або ще не існує, або вони містять приховані блокуючі затримки та надлишкові шари абстракції. Єдиним джерелом істини для створення швидкого та надійного драйвера залишається Reference Manual. Пряма робота з регістрами вимагає строгого дотримання трьох інженерних правил: точного відображення структур у пам'ять, атомарного очищення прапорців стану та врахування ревізії кремнію для обходу апаратних дефектів.

## Задача: драйвер передавача UART з безпечним очищенням прапорців

Розглянемо типовий периферійний блок універсального асинхронного приймача-передавача (UART/USART). За документацією Reference Manual блок відображений у адресний простір пам'яті *(англ. Memory-Mapped I/O, MMIO)* за базовою адресою `0x40013800` (шина APB2). Регістрова карта містить:
- Регістр керування `CR1` (зміщення `+0x00`): біт 0 `UE` (дозвіл роботи блока, R/W), біт 3 `TE` (дозвіл передавача, R/W), біт 5 `RXNEIE` (дозвіл переривання прийому, R/W);
- Регістр налаштування швидкості `BRR` (зміщення `+0x0C`): дільник тактової частоти шини (R/W);
- Регістр стану та переривань `ISR` (зміщення `+0x1C`): біт 7 `TXE` (буфер передачі порожній, RO), біт 6 `TC` (передачу завершено, W1C), біти 3:0 (прапорці помилок переповнення та шуму, W1C);
- Регістр очищення переривань `ICR` (зміщення `+0x20`): запис «1» у відповідний біт скидає апаратний прапорець у `ISR` (тип доступу W1C / Write-Only);
- Регістр даних `TDR` (зміщення `+0x28`): молодші 8 або 9 бітів містять байт для відправки у лінію (Write-Only).

Крім того, бюлетень Errata Sheet для ревізії `Rev A` цього мікроконтролера фіксує апаратний баг: якщо записати байт у `TDR` негайно після встановлення біта `TE` у `CR1` без затримки щонайменше на 1 тактовий такт периферійної шини, перший стартовий біт формується некоректної тривалості. Для ревізії `Rev B` цю ваду усунуто в кремнії.

## Реалізація драйвера: C та ідіоматичний C++

Нижче наведено повну реалізацію регістрового драйвера: від оголошення структури регістрів з вирівнюванням пам'яті до перевірки ревізії чипа та атомарного скидання прапорців стану.

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>

/* Базові адреси периферійних блоків за Reference Manual */
#define PERIPH_BASE           (0x40000000UL)
#define APB2PERIPH_BASE       (PERIPH_BASE + 0x00010000UL)
#define USART1_BASE           (APB2PERIPH_BASE + 0x00003800UL)
#define DBGMCU_BASE           (0xE0042000UL)

/* Бітові маски регістрів USART */
#define USART_CR1_UE          (1UL << 0)   /* Увімкнення блока USART */
#define USART_CR1_TE          (1UL << 3)   /* Увімкнення передавача (Transmitter Enable) */
#define USART_ISR_TXE         (1UL << 7)   /* Буфер передачі вільний (Transmit Data Empty, RO) */
#define USART_ISR_TC          (1UL << 6)   /* Передачу завершено (Transmission Complete, W1C) */
#define USART_ICR_TCCF        (1UL << 6)   /* Очищення прапорця завершення передачі (Write 1 to Clear) */

/* Структура регістрової карти USART із точним зміщенням змісту за RM */
typedef struct {
    volatile uint32_t CR1;    /* Offset: 0x00 - Control Register 1 */
    volatile uint32_t CR2;    /* Offset: 0x04 - Control Register 2 */
    volatile uint32_t CR3;    /* Offset: 0x08 - Control Register 3 */
    volatile uint32_t BRR;    /* Offset: 0x0C - Baud Rate Register */
    volatile uint32_t GTPR;   /* Offset: 0x10 - Guard Time and Prescaler */
    volatile uint32_t RTOR;   /* Offset: 0x14 - Receiver Timeout */
    volatile uint32_t RQR;    /* Offset: 0x18 - Request Register */
    volatile uint32_t ISR;    /* Offset: 0x1C - Interrupt and Status Register (RO / W1C flags) */
    volatile uint32_t ICR;    /* Offset: 0x20 - Interrupt Flag Clear Register (WO / W1C) */
    volatile uint32_t RDR;    /* Offset: 0x24 - Receive Data Register (RO) */
    volatile uint32_t TDR;    /* Offset: 0x28 - Transmit Data Register (WO) */
} UsartRegisters;

/* Регістр ідентифікації кремнію для визначення ревізії чипа (DBGMCU_IDCODE) */
typedef struct {
    volatile uint32_t IDCODE; /* Offset: 0x00 - Device ID [11:0] та Silicon Revision [31:16] */
} DbgMcuRegisters;

#define USART1   ((UsartRegisters *)USART1_BASE)
#define DBGMCU   ((DbgMcuRegisters *)DBGMCU_BASE)

/* Зчитування ревізії кремнію: 0x1000 = Rev A (з багом), 0x2000 = Rev B (виправлений) */
static inline uint16_t get_silicon_revision(void) {
    return (uint16_t)(DBGMCU->IDCODE >> 16);
}

/* Ініціалізація передавача UART */
void usart_init_tx(uint32_t pclk_hz, uint32_t baudrate) {
    /* 1. Обчислення та запис дільника швидкості (Baud Rate) */
    uint32_t brr_val = (pclk_hz + (baudrate / 2U)) / baudrate;
    USART1->BRR = brr_val;

    /* 2. Конфігурація: вмикаємо блок і передавач */
    USART1->CR1 = USART_CR1_UE | USART_CR1_TE;

    /* 3. Апаратний обхід (Workaround) з Errata Sheet для ревізії Rev A:
     * Потрібна пауза на 1 такт шини після увімкнення TE перед першим записом */
    if (get_silicon_revision() == 0x1000U) {
        __asm__ volatile ("nop");
    }
}

/* Відправка одного байта з блокуючим очікуванням готовності буфера */
bool usart_send_byte(uint8_t byte, uint32_t timeout_cycles) {
    /* Очікуємо готовності передавального буфера (прапорець TXE) */
    while (!(USART1->ISR & USART_ISR_TXE)) {
        if (timeout_cycles == 0) {
            return false; /* Захист від вічного зависання при апаратній аварії */
        }
        timeout_cycles--;
    }

    /* Запис байта в регістр даних передавача */
    USART1->TDR = byte;
    return true;
}

/* Безпечне очищення прапорця завершення передачі TC через механізм W1C */
void usart_clear_tc_flag(void) {
    /* Запис 1 у біт TCCF регістра ICR очищає біт TC у регістрі ISR.
     * Ніякого Read-Modify-Write (RMW) над ISR не виконується! */
    USART1->ICR = USART_ICR_TCCF;
}
```
```cpp
#include <cstdint>
#include <cstddef>
#include <concepts>
#include <span>

namespace hardware {

/* Структура регістрової карти USART за Reference Manual */
struct UsartBlock {
    volatile uint32_t cr1;    // 0x00: Control Register 1
    volatile uint32_t cr2;    // 0x04: Control Register 2
    volatile uint32_t cr3;    // 0x08: Control Register 3
    volatile uint32_t brr;    // 0x0C: Baud Rate Register
    volatile uint32_t gtpr;   // 0x10: Guard Time / Prescaler
    volatile uint32_t rtor;   // 0x14: Receiver Timeout
    volatile uint32_t rqr;    // 0x18: Request Register
    volatile uint32_t isr;    // 0x1C: Status & Interrupts (RO / W1C)
    volatile uint32_t icr;    // 0x20: Flag Clear (Write 1 to Clear)
    volatile uint32_t rdr;    // 0x24: Receive Data Register
    volatile uint32_t tdr;    // 0x28: Transmit Data Register
};

struct DbgMcuBlock {
    volatile uint32_t idcode; // 0x00: Device ID & Revision
};

/* Типобезпечні константи адрес та масок */
inline constexpr uintptr_t usart1_address = 0x40013800UL;
inline constexpr uintptr_t dbgmcu_address = 0xE0042000UL;

namespace flags {
    inline constexpr uint32_t cr1_ue   = 1UL << 0;
    inline constexpr uint32_t cr1_te   = 1UL << 3;
    inline constexpr uint32_t isr_txe  = 1UL << 7;
    inline constexpr uint32_t isr_tc   = 1UL << 6;
    inline constexpr uint32_t icr_tccf = 1UL << 6;
}

/* Інкапсульований драйвер UART із захистом від апаратних пасток */
class UartDriver {
public:
    explicit constexpr UartDriver(uintptr_t base_addr = usart1_address) noexcept
        : regs_(*reinterpret_cast<UsartBlock*>(base_addr)),
          dbg_(*reinterpret_cast<DbgMcuBlock*>(dbgmcu_address)) {}

    // Заборона копіювання: апаратний блок унікальний
    UartDriver(const UartDriver&) = delete;
    UartDriver& operator=(const UartDriver&) = delete;

    [[nodiscard]] uint16_t get_silicon_revision() const noexcept {
        return static_cast<uint16_t>(dbg_.idcode >> 16);
    }

    void init_transmitter(uint32_t bus_clock_hz, uint32_t baudrate) noexcept {
        const uint32_t brr_val = (bus_clock_hz + (baudrate / 2U)) / baudrate;
        regs_.brr = brr_val;
        regs_.cr1 = flags::cr1_ue | flags::cr1_te;

        // Errata Workaround: затримка на 1 такт для ревізії Rev A (0x1000)
        if (get_silicon_revision() == 0x1000U) {
            asm volatile("nop");
        }
    }

    [[nodiscard]] bool send_byte(uint8_t byte, uint32_t timeout_cycles = 100'000) noexcept {
        while ((regs_.isr & flags::isr_txe) == 0) {
            if (timeout_cycles == 0) {
                return false;
            }
            --timeout_cycles;
        }

        regs_.tdr = byte;
        return true;
    }

    size_t send_buffer(std::span<const uint8_t> data) noexcept {
        size_t sent = 0;
        for (uint8_t byte : data) {
            if (!send_byte(byte)) {
                break;
            }
            ++sent;
        }
        return sent;
    }

    void clear_transmission_complete_flag() noexcept {
        // Атомарне очищення W1C: запис у ICR без модифікації ISR
        regs_.icr = flags::icr_tccf;
    }

private:
    UsartBlock& regs_;
    DbgMcuBlock& dbg_;
};

} // namespace hardware
```
:::

## Глибокий розбір апаратних механізмів та пасток

Наведена реалізація враховує специфіку поведінки апаратних шин мікроконтролера на найнижчому фізичному рівні:

### 1. Ключове слово `volatile` та оптимізації компілятора

Специфікатор `volatile` вказує компілятору C/C++, що значення за цією адресою пам'яті може змінюватися зовнішніми апаратними процесами без участі процесорного ядра. Без `volatile` оптимізатор компілятора (рівні `-O2`, `-O3`, `-Os`) вважає доступ до пам'яті звичайною змінною:
- При циклі очікування прапорця `while (!(USART1->ISR & USART_ISR_TXE))` компілятор зчитає значення регістра `ISR` у внутрішній регістр процесора `r0` рівно один раз перед циклом;
- Оскільки всередині тіла циклу записів у `ISR` немає, компілятор видалить повторні звернення до пам'яті й згенерує нескінченний порожній цикл `b .`, якщо прапорець спочатку дорівнював нулю;
- Зі специфікатором `volatile` кожна ітерація циклу гарантовано породжує інструкцію читання з шини (`LDR` на ARM або `LW` на RISC-V).

### 2. Розрядність доступу та вирівнювання (Bus Width & Alignment)

Усі регістри периферії в 32-бітних мікроконтролерах відображені на системні шини (AHB, APB) у вигляді 32-бітних слів і мають бути строго вирівняні за межею 4 байтів *(англ. 4-byte aligned)*. Звернення за непарною адресою або спроба записати один байт за допомогою інструкції `STRB` у регістр, який апаратно підтримує лише 32-бітний доступ `STR`, призводить до апаратного винятку `BusFault` або мовчазного спотворення сусідніх бітів у регістрі.

Оголошення регістрової карти як структури з полями типу `volatile uint32_t` гарантує, що кожне поле займає рівно 4 байти, зміщення кожного регістра строго відповідає документації Reference Manual, а компілятор завжди генерує повні 32-бітні інструкції завантаження та збереження.

### 3. Механіка W1C та захист від гонки станів (Race Condition)

Прапорці подій у мікроконтролерах часто встановлюються апаратними автоматами периферії асинхронно відносно виконання коду програми. Розглянемо детальний часовий зріз аварійної ситуації при спробі скинути прапорець класичним програмним маскуванням:

1. Драйвер вирішує скинути прапорець завершення передачі `TC` (біт 6) у регістрі `ISR`.
2. Процесор зчитує поточне значення `ISR` у регістр ядра: `r0 = 0x00000040` (активний лише біт `TC`).
3. Рівно в наступний такт, поки процесор виконує операцію `BIC` (побітове скидання біта), на лінії UART закінчується прийом байта, і апаратний приймач встановлює біт 5 `RXNE` (новий байт у буфері). Фізичний регістр у кремнії тепер містить `0x00000060`.
4. Процесор завершує операцію і записує модифіковане значення `0x00000000` назад у регістр `ISR`.
5. **Наслідок:** біт `RXNE` виявляється примусово скинутим, хоча процесор його навіть не прочитав. Переривання прийому не виникає, прийнятий байт залишається непоміченим і згодом перезаписується наступним символом із виникненням помилки переповнення `Overrun Error`.

Розділення регістру стану `ISR` та регістра очищення `ICR` (або пряме використання принципу W1C, коли запис «1» скидає біт, а запис «0» залишає його без змін) повністю усуває цю проблему. Запис `USART1->ICR = USART_ICR_TCCF` надсилає на шину значення `0x00000040`. Внутрішня логіка кремнію використовує цей запис як імпульс скидання виключно для тригера `TC`, жодним чином не впливаючи на стан паралельного тригера `RXNE`.

### 4. Бар'єри пам'яті та буферизація запису (Memory Barriers)

На процесорах із конвеєрною архітектурою та буферизацією шини (таких як ARM Cortex-M4/M7 або високопродуктивні ядра RISC-V) операція запису в периферійний регістр потрапляє в буфер запису *(англ. Write Buffer)* і виконується асинхронно. Якщо драйвер скидає прапорець переривання в останньому рядку функції обробника переривання (ISR) і негайно повертає керування, ядро може вийти з обробника до того, як сигнал скидання добіжить шиною до периферійного модуля. Контролер переривань (NVIC) побачить активний прапорець і миттєво викличе той самий обробник переривання вдруге.

Для запобігання фальшивим повторним перериванням після запису в регістри скидання прапорців використовують або повторне фіктивне читання регістра (яке примусово зупиняє конвеєр до завершення транзакції на шині), або апаратну інструкцію бар'єра синхронізації даних:

:::tabs
```c
USART1->ICR = USART_ICR_TCCF;
__asm__ volatile ("dsb" ::: "memory"); /* Data Synchronization Barrier */
```
```cpp
regs_.icr = flags::icr_tccf;
asm volatile("dsb" ::: "memory"); // Data Synchronization Barrier
```
:::

Така комбінація точного слідування Reference Manual, використання безпечних бітових масок, таймаутів та врахування кремнієвих ревізій утворює надійний фундамент для промислового коду вбудованих систем.
