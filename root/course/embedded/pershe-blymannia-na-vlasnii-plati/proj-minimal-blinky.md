# ⚙️ Мінімальний Blinky на голих регістрах C і C++

Готова плата лежить на монтажному столі, живлення від лабораторного джерела подано, але на ній ще немає жодної робочої бібліотеки. Цей проект демонструє повний, автономний код першого блимання світлодіодом без використання вендорних HAL, CubeMX чи сторонніх драйверів. Програма звертається напряму до фізичних адрес регістрів тактування (RCC) та конфігурації портів (GPIO), тактується від внутрішнього RC-генератора HSI та виконує затримку через прозорий програмний цикл. Це еталонний тестовий стенд для апаратної верифікації фізичного монтажу мікроконтролера та світлодіода.

Нижче наведено дві версії проекту: чистою мовою C (із прямими вказівниками та бітовими масками) та ідіоматичною мовою C++ (із типізованими шаблонами регістрів, `constexpr` базовими адресами та нульовими накладними витратами часу виконання).

## Архітектурний план програми

Програма розв'язує задачу апаратної верифікації за чотири послідовні кроки:

1. **Ввімкнення тактування порту введення-виведення:** у регістрі керування тактуванням (на прикладі `RCC_AHB1ENR` для архітектури STM32F4 або аналогічного `RCC_APB2ENR` для STM32F1) виставляється біт дозволу тактування шини відповідного порту.
2. **Конфігурація виводу як цифрового виходу:** у регістрі режиму `MODER` біти відповідного піна переводяться у стан `01` (General purpose output mode). Регістр типу виходу `OTYPER` залишається в нулі (Push-Pull), а швидкість `OSPEEDR` виставляється в `00` (Low speed) для мінімізації високочастотних завад на шині живлення.
3. **Атомарне перемикання стану:** у нескінченному циклі запис одиниці в молодші 16 бітів регістра `BSRR` встановлює на виводі високий рівень (3.3 В), а запис у старші 16 бітів скидає вивід у низький рівень (0 В).
4. **Програмна затримка:** циклічний відлік змінної з кваліфікатором `volatile`, який запобігає оптимізації та викиданню порожнього циклу компілятором.

## Реалізація проекту

:::tabs
```c
#include <stdint.h>

/* Базові адреси периферійних блоків на шині AHB1 (STM32F4) */
#define PERIPH_BASE           (0x40000000UL)
#define AHB1PERIPH_BASE       (PERIPH_BASE + 0x00020000UL)
#define RCC_BASE              (AHB1PERIPH_BASE + 0x3800UL)
#define GPIOC_BASE            (AHB1PERIPH_BASE + 0x0800UL)

/* Зсуви регістрів RCC */
#define RCC_AHB1ENR_OFFSET    (0x30UL)
#define RCC_AHB1ENR           (*(volatile uint32_t *)(RCC_BASE + RCC_AHB1ENR_OFFSET))
#define RCC_AHB1ENR_GPIOCEN   (1UL << 2)

/* Зсуви регістрів GPIO */
#define GPIO_MODER_OFFSET     (0x00UL)
#define GPIO_OTYPER_OFFSET    (0x04UL)
#define GPIO_OSPEEDR_OFFSET   (0x08UL)
#define GPIO_PUPDR_OFFSET     (0x0CUL)
#define GPIO_BSRR_OFFSET      (0x18UL)

#define GPIOC_MODER           (*(volatile uint32_t *)(GPIOC_BASE + GPIO_MODER_OFFSET))
#define GPIOC_OTYPER          (*(volatile uint32_t *)(GPIOC_BASE + GPIO_OTYPER_OFFSET))
#define GPIOC_OSPEEDR         (*(volatile uint32_t *)(GPIOC_BASE + GPIO_OSPEEDR_OFFSET))
#define GPIOC_PUPDR           (*(volatile uint32_t *)(GPIOC_BASE + GPIO_PUPDR_OFFSET))
#define GPIOC_BSRR            (*(volatile uint32_t *)(GPIOC_BASE + GPIO_BSRR_OFFSET))

#define LED_PIN               (13U)

/* Програмна затримка на змінній volatile */
static void delay_cycles(volatile uint32_t count) {
    while (count--) {
        __asm__ volatile ("nop");
    }
}

int main(void) {
    /* 1. Вмикаємо тактування порту GPIOC */
    RCC_AHB1ENR |= RCC_AHB1ENR_GPIOCEN;

    /* Короткий бар'єр пам'яті для стабілізації шини після ввімкнення такту */
    __asm__ volatile ("dmb" ::: "memory");

    /* 2. Налаштовуємо пін 13 як вихід (01 у бітах 27:26) */
    GPIOC_MODER &= ~(3UL << (LED_PIN * 2));
    GPIOC_MODER |=  (1UL << (LED_PIN * 2));

    /* Push-Pull (0 у біті 13) */
    GPIOC_OTYPER &= ~(1UL << LED_PIN);

    /* Низька швидкість Low Speed для зменшення завад (00 у бітах 27:26) */
    GPIOC_OSPEEDR &= ~(3UL << (LED_PIN * 2));

    /* Без внутрішньої підтяжки No Pull (00 у бітах 27:26) */
    GPIOC_PUPDR &= ~(3UL << (LED_PIN * 2));

    /* 3. Головний цикл блимання */
    while (1) {
        /* Вмикаємо світлодіод (для Active High — встановлення біта 13) */
        GPIOC_BSRR = (1UL << LED_PIN);
        delay_cycles(500000);

        /* Вимикаємо світлодіод (скидання біта 13 через старшу половину BSRR) */
        GPIOC_BSRR = (1UL << (LED_PIN + 16));
        delay_cycles(500000);
    }

    return 0;
}
```
```cpp
#include <cstdint>

namespace mcu {

// Безпечна типізована обгортка над апаратним регістром
template <std::uintptr_t Address>
struct Register {
    static void write(std::uint32_t value) noexcept {
        *reinterpret_cast<volatile std::uint32_t*>(Address) = value;
    }

    static std::uint32_t read() noexcept {
        return *reinterpret_cast<volatile std::uint32_t*>(Address);
    }

    static void set_bits(std::uint32_t mask) noexcept {
        write(read() | mask);
    }

    static void clear_bits(std::uint32_t mask) noexcept {
        write(read() & ~mask);
    }

    static void modify(std::uint32_t clear_mask, std::uint32_t set_mask) noexcept {
        write((read() & ~clear_mask) | set_mask);
    }
};

// Карта периферії STM32F4
inline constexpr std::uintptr_t periph_base     = 0x40000000UL;
inline constexpr std::uintptr_t ahb1periph_base = periph_base + 0x00020000UL;
inline constexpr std::uintptr_t rcc_base        = ahb1periph_base + 0x3800UL;
inline constexpr std::uintptr_t gpioc_base      = ahb1periph_base + 0x0800UL;

// Регістри тактування та портів
using RccAhb1Enr  = Register<rcc_base + 0x30UL>;
using GpiocModer  = Register<gpioc_base + 0x00UL>;
using GpiocOtyper = Register<gpioc_base + 0x04UL>;
using GpiocOspeed = Register<gpioc_base + 0x08UL>;
using GpiocPupdr  = Register<gpioc_base + 0x0CUL>;
using GpiocBsrr   = Register<gpioc_base + 0x18UL>;

enum class PinMode : std::uint32_t {
    Input     = 0b00,
    Output    = 0b01,
    Alternate = 0b10,
    Analog    = 0b11
};

enum class ActivePolarity {
    High,
    Low
};

template <std::uint8_t PinNumber, ActivePolarity Polarity = ActivePolarity::High>
class OutputPin {
    static_assert(PinNumber < 16, "Pin number must be between 0 and 15");

public:
    static void init() noexcept {
        // Конфігурація режиму General Purpose Output
        constexpr std::uint32_t mask = 0b11UL << (PinNumber * 2);
        constexpr std::uint32_t val  = static_cast<std::uint32_t>(PinMode::Output) << (PinNumber * 2);
        GpiocModer::modify(mask, val);

        // Push-pull вихід
        GpiocOtyper::clear_bits(1UL << PinNumber);

        // Low speed для зменшення шуму живлення
        GpiocOspeed::clear_bits(0b11UL << (PinNumber * 2));

        // Без підтяжки
        GpiocPupdr::clear_bits(0b11UL << (PinNumber * 2));

        turn_off();
    }

    static void set_raw_high() noexcept {
        GpiocBsrr::write(1UL << PinNumber);
    }

    static void set_raw_low() noexcept {
        GpiocBsrr::write(1UL << (PinNumber + 16));
    }

    static void turn_on() noexcept {
        if constexpr (Polarity == ActivePolarity::High) {
            set_raw_high();
        } else {
            set_raw_low();
        }
    }

    static void turn_off() noexcept {
        if constexpr (Polarity == ActivePolarity::High) {
            set_raw_low();
        } else {
            set_raw_high();
        }
    }

    static void toggle(bool state) noexcept {
        if (state) {
            turn_on();
        } else {
            turn_off();
        }
    }
};

} // namespace mcu

namespace {

void delay_ticks(volatile std::uint32_t ticks) noexcept {
    while (ticks--) {
        __asm__ volatile ("nop");
    }
}

} // namespace

int main() {
    // 1. Дозвіл тактування порту GPIOC (біт 2)
    mcu::RccAhb1Enr::set_bits(1UL << 2);

    // Бар'єр пам'яті для завершення транзакції на шині
    __asm__ volatile ("dmb" ::: "memory");

    // 2. Ініціалізація виводу світлодіода (PC13, Active High)
    using Led = mcu::OutputPin<13, mcu::ActivePolarity::High>;
    Led::init();

    // 3. Нескінченний цикл
    while (true) {
        Led::turn_on();
        delay_ticks(500000);

        Led::turn_off();
        delay_ticks(500000);
    }

    return 0;
}
```
:::

## Збирання, прошивання та покроковий розбір

### 1. Команда збирання без стандартних бібліотек
Для компіляції цього мінімального проекту не потрібні заголовні файли CMSIS чи важка стандартна бібліотека libc. Використовується прямий виклик крос-компілятора GNU Arm Toolchain:

```bash
# Компіляція версії на C
arm-none-eabi-gcc -mcpu=cortex-m4 -mthumb -O1 -nostdlib -ffreestanding \
    -T link.ld startup.s main.c -o blinky.elf

# Компіляція версії на C++
arm-none-eabi-g++ -mcpu=cortex-m4 -mthumb -O1 -nostdlib -ffreestanding \
    -fno-exceptions -fno-rtti \
    -T link.ld startup.s main.cpp -o blinky.elf

# Отримання бінарного образу для прошивання
arm-none-eabi-objcopy -O binary blinky.elf blinky.bin
```

Прапорці `-nostdlib` та `-ffreestanding` гарантують, що компілятор не втягне бібліотеки вводу-виводу або конструктори рантайму, які потребують складної ініціалізації пам'яті до виклику `main()`. Прапорець `-O1` забезпечує генерацію компактного коду, зберігаючи при цьому передбачуваність налагодження.

### 2. Завантаження через OpenOCD та SWD
Заливання бінарного образу у Flash-пам'ять нової плати здійснюється за допомогою відлагоджувача ST-Link або J-Link та утиліти OpenOCD однією командою з термінала:

```bash
openocd -f interface/stlink.cfg -f target/stm32f4x.cfg \
    -c "init" \
    -c "reset halt" \
    -c "flash write_image erase blinky.elf" \
    -c "reset run" \
    -c "exit"
```

Якщо підключення SWD справне і живлення мікроконтролера в нормі, OpenOCD виведе ідентифікатор чипа (IDCODE) та виконає стирання і запис потрібних секторів Flash. Після виконання команди `reset run` мікроконтролер негайно розпочне виконання коду з нульової адреси Flash-пам'яті.

### 3. Чому потрібен бар'єр пам'яті після ввімкнення тактування
На швидких процесорних ядрах Cortex-M4/M7 запис у регістр `RCC_AHB1ENR` проходить через буфер запису шини (Write Buffer). Процесор може перейти до наступної інструкції запису в `GPIOC_MODER` ще до того, як блок логіки GPIOC фізично отримає тактовий сигнал від шини AHB. У результаті перший запис у `MODER` може бути проігнорований апаратурою або викликати апаратне виключення `BusFault`. Інструкція `__asm__ volatile ("dmb" ::: "memory")` (Data Memory Barrier) гарантує, що запис у RCC повністю зафіксований на шині до першого звернення до самого порту.

### 4. Чому затримка написана через `volatile uint32_t`
Якщо написати звичайний цикл `for (uint32_t i = 0; i < 500000; i++);` без кваліфікатора `volatile`, оптимізатор компілятора GCC із прапорцем `-O2` або `-Os` визначить, що цикл не має побічних ефектів, і повністю видалить його з машинного коду. Програма почне перемикати пін на частоті в кілька мегагерців, і світлодіод здаватиметься людині постійно ввімкненим на половину яскравості. Кваліфікатор `volatile` змушує компілятор чесно вичитувати та декрементувати значення змінної лічильника в кожній ітерації в пам'яті або регістрі, не викидаючи цикл.

### 5. Атомарність через регістр BSRR проти ODR
Зверніть увагу: код свідомо не використовує вираз `GPIOC_ODR ^= (1 << 13)`. Операція над `ODR` є операцією типу Read-Modify-Write (читання регістра, побітове «АБО» чи «виключне АБО», запис назад). На рівні асемблера це щонайменше три окремі інструкції (`LDR`, `EOR`, `STR`). Якщо між читанням і записом відбудеться переривання, в якому обробник змінить стан іншого виводу порту C, повернення з переривання перезапише старе значення та зіпсує стан сусіднього піна. Прямий запис у `BSRR` виконується за одну інструкцію запису (`STR`) і не потребує блокування переривань.

### 6. Оцінка реальної частоти та апаратні вимірювання
При тактуванні від внутрішнього генератора HSI (16 МГц) одна ітерація циклу `delay_cycles` на Cortex-M4 з оптимізацією `-O1` займає в середньому 4 машинні такти (декремент лічильника `subs`, перевірка умови `bne`, інструкція `nop` та робота конвеєра). Затримка на 500 000 ітерацій формує інтервал:

```
t_delay = (500000 * 4) / 16000000 = 2000000 / 16000000 = 0.125 с
```

Повний період коливання становить 0.25 секунди (частота 4 Гц). Це чітко помітно неозброєним оком і фіксується будь-яким осцилографом чи логічним аналізатором. Якщо реальний період на екрані приладу суттєво відрізняється від розрахункового, це вказує на зміщення заводського калібрування RC-генератора або на виконання коду з Flash-пам'яті з незапланованими тактами очікування (Wait States).

### 7. Адаптація до інших архітектур
Принцип прямого доступу є універсальним для всіх вбудованих мікроконтролерів:
- **Raspberry Pi RP2040 (Cortex-M0+):** замість `BSRR` блок швидкого вводу-виводу SIO надає атомарні регістри `GPIO_OUT_SET` (зсув `0x14`) та `GPIO_OUT_CLR` (зсув `0x18`) за базовою адресою `0xD0000000`.
- **Nordic nRF52 (Cortex-M4):** порт `P0` керується регістрами `OUTSET` (зсув `0x508`) та `OUTCLR` (зсув `0x50C`) від бази `0x50000000`.
- **AVR ATmega328P:** налаштування напрямку виконується через регістр `DDRB`, а атомарне інвертування піна — прямим записом одиниці у вхідний регістр `PINB`.
