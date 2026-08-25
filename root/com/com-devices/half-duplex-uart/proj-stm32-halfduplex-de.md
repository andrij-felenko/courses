# ⚙️ Реалізація напівдуплексного UART та керування лінією DE

Напівдуплексний послідовний зв'язок через спільний провід або диференційну пару вимагає від прошивки безпомилкового керування напрямком передачі та апаратними прапорцями: помилка в один такт обрізає завершальний стоп-біт або спалює вихідний каскад зустрічним струмом. Розглянемо низькорівневу архітектуру апаратного блоку UART, конфігурацію однопровідного режиму (Single-Wire / HDSEL), автоматичне та програмне керування сигналом Driver Enable (DE), організацію високопродуктивного прийому через DMA з детектуванням тиші (IDLE Line), апаратний таймаут кадру (Receiver Timeout), обробку апаратних прапорців збоїв (ORE/FE/NE), керування кеш-пам'яттю на ядрах Cortex-M7, інтеграцію з RTOS, обробку локального відлуння та покроковий аналіз типових осцилограм при налагодженні.

### Внутрішня архітектура передавача UART: чому виникає пастка TXE

Щоб зрозуміти, чому просте перемикання ніжки GPIO після виклику функції передачі калічить дані, необхідно розібрати внутрішню структуру апаратного передавача UART у мікроконтролерах (наприклад, лінійки STM32, GD32, NXP LPC чи ESP32).

Передавальний тракт містить два послідовні апаратні регістри:
1. **Буферний регістр даних передавача (`TDR` — Transmit Data Register):** доступний програмісту регістр, у який записується наступний призначений для відправки байт (або слово). У новіших мікроконтролерах із чергою FIFO це верхівка апаратного буфера передачі.
2. **Зсувний регістр передавача (`TSR` — Transmit Shift Register):** внутрішній апаратний регістр, недоступний для прямого запису. Він отримує паралельний байт із `TDR`, додає до нього старт-біт, біт парності (якщо ввімкнено) та стоп-біти, після чого послідовно зсуває біти в лінію з частотою бод-генератора.

Робота передавача генерує два принципово різні апаратні статусні прапорці:

```
[Запис у TDR] ───(TDR → TSR паралельно)───► [Зсувний регістр TSR] ───(побітно)───► Лінія TX
                     │                                                      │
             Встановлюється                                           Встановлюється
           прапорець TXE = 1                                         прапорець TC = 1
     (TDR порожній, TSR працює)                                   (Стоп-біт пішов у лінію)
```

- **Прапорець `TXE` (Transmit Data Register Empty / TXFNF):** сигналізує, що `TDR` звільнився, оскільки його вміст було перевантажено в `TSR`. Це означає лише одне: у `TDR` можна записати *наступний* байт черги. Сам байт у цей момент щойно почав виходити в лінію крізь `TSR`.
- **Прапорець `TC` (Transmission Complete):** виставляється виключно тоді, коли `TDR` порожній, а `TSR` завершив зсув останнього стоп-біта в фізичну лінію і вихідний буфер перейшов у стан очікування (Mark state).

#### Особливості роботи з апаратним FIFO (STM32G4 / STM32H7 / STM32U5)
У сучасних мікроконтролерах із підтримкою апаратного FIFO (біт `FIFOEN = 1` у `USART_CR1`) регістр `TDR` перетворюється на 8-рівневий буфер черги:
- Прапорець `TXFNF` (TX FIFO Not Full) активується, коли у черзі FIFO є місце хоча б для одного байта.
- Прапорець `TXFE` (TX FIFO Empty) виставляється, коли апаратний буфер FIFO повністю спустошений, але в зсувному регістрі `TSR` ще може перебувати останній байт.
- Рівень порогу спрацьовування переривання FIFO (TXFTCFG) можна налаштувати на 1/8, 1/4, 1/2, 3/4 або повне спустошення буфера.
- Для скидання сигналу `DE` у низький рівень необхідно чекати виключно прапорець `TC`, оскільки прапорець `TXFE` з'являється до того, як останній байт залишить кристал мікроконтролера.

Якщо драйвер напівдуплексного трансивера RS-485 (лінія `DE`) вимикається за прапорцем `TXE` чи `TXFE`, мікроконтролер переводить передавач у стан високого імпедансу (Hi-Z) якраз у момент, коли `TSR` починає видавати старт-біт або перші біти даних останнього байта. Приймач на іншому кінці бачить обрив сигналу, фіксує помилку кадрування (*Framing Error*) або хибний байт `0x00`.

### Налаштування швидкості вихідного каскаду GPIO (Slew Rate Control)

При конфігурації піна TX у режимі відкритого стоку або лінії керування `DE` особливу увагу слід приділити регістру швидкості наростання фронту `GPIO_OSPEEDR`:
- **Very High Speed (50–100 МГц):** відкриває транзистор за 1–2 нс. Якщо провід має довжину понад 20–30 см, крутий спадний фронт викликає значний індуктивний викид напруги (*Ground Bounce*) та високочастотний дзвін.
- **Medium Speed (10–25 МГц):** оптимальний вибір для більшості напівдуплексних шин зі швидкостями до 1–2 Мбіт/с. Забезпечує достатню крутизну спаду без генерації надлишкового радіовипромінювання (EMI).

:::tabs
```c
// Налаштування швидкості виводу TX та DE (STM32, C)
void gpio_set_uart_pin_speed(GPIO_TypeDef *port, uint32_t pin_pos, uint32_t speed_level) {
    port->OSPEEDR &= ~(0x03 << (pin_pos * 2));
    port->OSPEEDR |= ((speed_level & 0x03) << (pin_pos * 2));
}
```
```cpp
// Налаштування швидкості виводу TX та DE (C++)
#include <cstdint>

struct GpioSpeedController {
    static constexpr void set_speed(GPIO_TypeDef *port, std::uint8_t pin_index, std::uint8_t speed_level) noexcept {
        port->OSPEEDR &= ~(0x03 << (pin_index * 2));
        port->OSPEEDR |= ((static_cast<std::uint32_t>(speed_level) & 0x03) << (pin_index * 2));
    }
};
```
:::

### Конфігурація однопровідного напівдуплексу (USART Single-Wire HDSEL)

Сучасні мікроконтролери сімейства STM32 мають вбудовану апаратну підтримку однопровідного напівдуплексного режиму (*Single-Wire Half-Duplex*). Її вмикають установкою біта `HDSEL` (Half-Duplex Selection) у керувальному регістрі `USART_CR3`.

При встановленні `HDSEL = 1`:
- Вивід `TX` мікроконтролера внутрішньо з'єднується з входом приймача `RX`.
- Зовнішній вивід `RX` повністю відключається від периферійного модуля UART і звільняється для використання як звичайний пін GPIO загального призначення.
- Вивід `TX` конфігурується в режимі альтернативної функції з **відкритим стоком** (*Open-Drain*). Для коректної роботи лінія вимагає зовнішнього або внутрішнього резистора підтяжки `Pull-Up`.

Нижче наведено порівняння конфігурації напівдуплексного режиму на мовах C та C++:

:::tabs
```c
// Регістрова ініціалізація USART1 у режимі Single-Wire Half-Duplex (STM32, C)
void usart1_half_duplex_init(uint32_t baudrate, uint32_t pclk_hz) {
    // 1. Тактування GPIOA та USART1
    RCC->IOPENR |= RCC_IOPENR_GPIOAEN;
    RCC->APBENR2 |= RCC_APBENR2_USART1EN;

    // 2. Налаштування піна PA9 (USART1_TX): Alternate Function, Open-Drain, Pull-up, High Speed
    GPIOA->MODER &= ~(GPIO_MODER_MODE9_Msk);
    GPIOA->MODER |= (0x02 << GPIO_MODER_MODE9_Pos);      // AF mode
    GPIOA->AFR[1] |= (0x01 << GPIO_AFRH_AFSEL9_Pos);      // AF1 = USART1
    GPIOA->OTYPER |= GPIO_OTYPER_OT9;                    // Open-Drain (обов'язково!)
    GPIOA->PUPDR |= GPIO_PUPDR_PUPD9_0;                  // Внутрішня підтяжка Pull-up
    GPIOA->OSPEEDR |= GPIO_OSPEEDR_OSPEED9;              // High speed

    // 3. Налаштування USART1
    USART1->CR1 = 0;                                     // Вимкнення перед конфігурацією
    USART1->BRR = (pclk_hz + (baudrate / 2)) / baudrate; // Розрахунок подільника частоти

    // 4. Увімкнення режиму Half-Duplex
    USART1->CR3 |= USART_CR3_HDSEL;

    // 5. Увімкнення передавача та приймача
    USART1->CR1 |= (USART_CR1_TE | USART_CR1_RE | USART_CR1_UE);
}
```
```cpp
// Об'єктно-орієнтована ініціалізація USART1 у режимі Single-Wire Half-Duplex (C++)
#include <cstdint>

struct UsartSingleWireConfig {
    static constexpr void init(std::uint32_t baudrate, std::uint32_t pclk_hz) noexcept {
        // 1. Тактування GPIOA та USART1
        RCC->IOPENR |= RCC_IOPENR_GPIOAEN;
        RCC->APBENR2 |= RCC_APBENR2_USART1EN;

        // 2. Налаштування PA9 (TX): Alternate Function, Open-Drain, Pull-up
        GPIOA->MODER &= ~(GPIO_MODER_MODE9_Msk);
        GPIOA->MODER |= (0x02 << GPIO_MODER_MODE9_Pos);
        GPIOA->AFR[1] |= (0x01 << GPIO_AFRH_AFSEL9_Pos);
        GPIOA->OTYPER |= GPIO_OTYPER_OT9;
        GPIOA->PUPDR |= GPIO_PUPDR_PUPD9_0;
        GPIOA->OSPEEDR |= GPIO_OSPEEDR_OSPEED9;

        // 3. Налаштування бодрейту та режиму Half-Duplex
        USART1->CR1 = 0;
        USART1->BRR = (pclk_hz + (baudrate / 2)) / baudrate;
        USART1->CR3 |= USART_CR3_HDSEL;

        // 4. Увімкнення передавача, приймача та блоку USART
        USART1->CR1 |= (USART_CR1_TE | USART_CR1_RE | USART_CR1_UE);
    }
};
```
:::

### Апаратне автокерування сигналом DE (Hardware Driver Enable)

Для роботи з RS-485 багато сучасних контролерів підтримують апаратне керування лінією `DE` безпосередньо логікою UART. У STM32 це реалізовано бітом `DEM` (Driver Enable Mode) у регістрі `USART_CR3`.

Апаратний блок дозволяє налаштувати два критичні часові інтервали за допомогою полів `DEAT` (Driver Enable Assertion Time) та `DEDT` (Driver Enable Deassertion Time):
- **`DEAT` (Час випередження увімкнення драйвера):** кількість тактів частоти UART, яку модуль вичікує між підняттям сигналу `DE` у високий рівень та початком генерації старт-біта. Це дає трансиверу час вийти зі стану Hi-Z і стабілізувати рівні на диференційній парі.
- **`DEDT` (Час затримки вимкнення драйвера):** кількість тактів після завершення передачі останнього стоп-біта перед опусканням лінії `DE` в низький рівень. Це запобігає передчасному обриву сигналу стоп-біта.

:::tabs
```c
// Конфігурація апаратного DE (RS-485 Driver Enable, C)
void usart1_rs485_hw_de_init(void) {
    // Вмикаємо режим Driver Enable, активний рівень — HIGH
    // DEAT = 4 такти випередження, DEDT = 4 такти затримки скидання
    USART1->CR3 |= USART_CR3_DEM;
    USART1->CR3 &= ~USART_CR3_DEP;                      // DEP = 0 -> DE active HIGH
    USART1->CR3 |= (4 << USART_CR3_DEAT_Pos);           // 4 тактових імпульси випередження
    USART1->CR3 |= (4 << USART_CR3_DEDT_Pos);           // 4 тактових імпульси затримки
}
```
```cpp
// Конфігурація апаратного DE (RS-485 Driver Enable, C++)
#include <cstdint>

struct HardwareDriverEnable {
    static constexpr void configure(std::uint8_t assert_clocks = 4, std::uint8_t deassert_clocks = 4) noexcept {
        USART1->CR3 |= USART_CR3_DEM;
        USART1->CR3 &= ~USART_CR3_DEP;
        USART1->CR3 |= (static_cast<std::uint32_t>(assert_clocks) << USART_CR3_DEAT_Pos);
        USART1->CR3 |= (static_cast<std::uint32_t>(deassert_clocks) << USART_CR3_DEDT_Pos);
    }
};
```
:::

### Програмне керування DE через GPIO: скінченний автомат на базі переривань

Якщо мікроконтролер не підтримує апаратний `DEM` або вивід `DE` жорстко прив'язаний до іншого піна плати, керування реалізується програмно через GPIO. Робота повинна будуватися на базі переривань `TXE` (для подачі байтів із буфера) та `TC` (для вимкнення передавача).

Алгоритм передачі пакета:
1. Підняти пін `DE` у високий рівень (вхід у режим передачі).
2. Записати перший байт у `TDR`.
3. Увімкнути переривання `TXEIE` (Transmit Data Register Empty Interrupt Enable).
4. У перериванні `TXE`: записувати наступні байти. Коли буфер вичерпано — **вимкнути** `TXEIE` та **увімкнути** `TCIE` (Transmission Complete Interrupt Enable).
5. У перериванні `TC`: очистити прапорець `TC` (записом `USART_ICR_TCCF` або читанням `ISR` з наступним записом `TDR`) і **опустити пін `DE`** у низький рівень (повернення в режим прийому).

### Високопродуктивний прийом: DMA та переривання тиші лінії (IDLE Line)

Прийом пакетів змінної довжини в напівдуплексній шині без відомої заздалегідь кількості байтів найефективніше організовувати через зв'язку **DMA у кільцевому режимі + переривання IDLE Line**:

1. Контролер DMA налаштовується на постійне вичитування байтів із регістра `RDR` у кільцевий буфер в оперативній пам'яті (`Circular DMA Mode`).
2. У регістрі `USART_CR1` вмикається переривання виявлення тиші лінії — `IDLEIE` (Idle Line Interrupt Enable).
3. Коли передавач віддаленого вузла завершує пакет і відпускає лінію, на шині настає пауза тривалістю щонайменше в один повний кадр (10–11 бітів високого рівня Mark).
4. Апаратний блок UART детектує стан тиші та виставляє прапорець `IDLE` у регістрі `ISR`.
5. Обробник переривання `USART_IRQHandler` зчитує поточний покажчик лічильника DMA (`DMA_CNDTR`), обчислює точну кількість щойно прийнятих байтів пакета й передає буфер у чергу задач операційної системи (RTOS).

### Апаратний таймаут прийому (Receiver Timeout — RTO)

Для протоколів із жорсткими вимогами до міжсимвольних інтервалів (наприклад, Modbus RTU з інтервалами `t_1.5` та `t_3.5`) сучасні модулі UART надають вбудований таймер таймауту прийому:

1. У регістрі `USART_CR2` встановлюється біт `RTOEN` (Receiver Timeout Enable).
2. У регістр `USART_RTOR` записується точне значення допустимої паузи в бітових інтервалах (наприклад, 35 бітів для інтервалу `t_3.5`).
3. Якщо після останнього прийнятого байта пауза перевищує задане значення, апаратно генерується прапорець `RTOF` (Receiver Timeout Flag) та переривання `RTOIE`, що дає змогу закрити пакет без використання сторонніх таймерів.

:::tabs
```c
// Налаштування апаратного Modbus RTO таймера (STM32, C)
void usart1_setup_modbus_timeout(uint32_t bit_clocks) {
    USART1->RTOR = (bit_clocks & USART_RTOR_RTO_Msk); // Наприклад, 35 бітів для t3.5
    USART1->CR2 |= USART_CR2_RTOEN;                   // Увімкнення апаратного RTO
    USART1->CR1 |= USART_CR1_RTOIE;                   // Дозвіл переривання таймауту
}
```
```cpp
// Налаштування апаратного Modbus RTO таймера (C++)
#include <cstdint>

struct HardwareReceiverTimeout {
    static constexpr void enable(std::uint32_t bit_clocks = 35) noexcept {
        USART1->RTOR = (bit_clocks & USART_RTOR_RTO_Msk);
        USART1->CR2 |= USART_CR2_RTOEN;
        USART1->CR1 |= USART_CR1_RTOIE;
    }
};
```
:::

### Автоматичне очищення та відновлення після апаратних помилок

При виникненні переповнення буфера (`ORE`), помилки кадрування (`FE`) чи шуму (`NE`) апаратний приймач блокує нові дані. Для запобігання «зависанню» драйвера переривання повинно гарантовано скидати прапорці збоїв:

:::tabs
```c
// Обробка та очищення прапорців помилок UART (STM32, C)
static inline void usart1_clear_error_flags(uint32_t isr) {
    uint32_t clear_mask = 0;
    if (isr & USART_ISR_ORE) clear_mask |= USART_ICR_ORECF;
    if (isr & USART_ISR_FE)  clear_mask |= USART_ICR_FECF;
    if (isr & USART_ISR_NE)  clear_mask |= USART_ICR_NECF;
    if (isr & USART_ISR_PE)  clear_mask |= USART_ICR_PECF;
    if (clear_mask != 0) {
        USART1->ICR = clear_mask;
    }
}
```
```cpp
// Обробка та очищення прапорців помилок UART (C++)
#include <cstdint>

struct HardwareErrorManager {
    static inline void clear_if_present(std::uint32_t isr_status) noexcept {
        std::uint32_t clear_mask = 0;
        if (isr_status & USART_ISR_ORE) clear_mask |= USART_ICR_ORECF;
        if (isr_status & USART_ISR_FE)  clear_mask |= USART_ICR_FECF;
        if (isr_status & USART_ISR_NE)  clear_mask |= USART_ICR_NECF;
        if (isr_status & USART_ISR_PE)  clear_mask |= USART_ICR_PECF;
        if (clear_mask != 0) {
            USART1->ICR = clear_mask;
        }
    }
};
```
:::

### Кеш-когерентність на ядрах ARM Cortex-M7

У високопродуктивних мікроконтролерах (серії STM32F7, STM32H7) ядро процесора працює через кеш даних першого рівня L1 (D-Cache). Контролер DMA виконує прямий доступ до оперативної пам'яті в обхід процесорного кешу. Це призводить до двох небезпечних станів несумісності даних:

1. **Прийом даних (RX DMA):** DMA записує прийнятий пакет у фізичну SRAM. Якщо кеш ядра містить застарілий кеш-рядок цієї адреси, процесор прочитає старі дані з кешу, пропустивши нові байти від DMA. Щоб цього уникнути, прошивка зобов'язана виконати інвалідацію рядка кешу перед читанням буфера.
2. **Передача даних (TX DMA):** процесор підготував пакет у буфері, але нові байти осіли в D-Cache і ще не потрапили у фізичну пам'ять. DMA прочитає стару пам'ять і відправить у лінію сміття. Прошивка зобов'язана скинути кеш (Clean / Flush) перед активацією каналу передачі DMA.

Нижче наведено коректне керування кеш-пам'яттю на C та C++:

:::tabs
```c
// Керування когерентністю D-Cache для буферів DMA (ARM Cortex-M7, C)
void dma_rx_cache_invalidate(uint8_t *buffer, size_t length) {
    // Вирівнювання адреси та розміру по межі кеш-рядка (32 байти)
    uint32_t addr = (uint32_t)buffer;
    SCB_InvalidateDCache_by_Addr((uint32_t*)addr, length);
}

void dma_tx_cache_clean(const uint8_t *buffer, size_t length) {
    uint32_t addr = (uint32_t)buffer;
    SCB_CleanDCache_by_Addr((uint32_t*)addr, length);
}
```
```cpp
// RAII-обгортка керування когерентністю D-Cache (C++)
#include <cstdint>
#include <cstddef>
#include <span>

template <typename T>
struct DmaCacheManager {
    static void invalidate(std::span<T> memory_block) noexcept {
        auto addr = reinterpret_cast<uint32_t*>(const_cast<std::remove_cv_t<T>*>(memory_block.data()));
        SCB_InvalidateDCache_by_Addr(addr, memory_block.size_bytes());
    }

    static void clean(std::span<const T> memory_block) noexcept {
        auto addr = reinterpret_cast<uint32_t*>(const_cast<T*>(memory_block.data()));
        SCB_CleanDCache_by_Addr(addr, memory_block.size_bytes());
    }
};
```
:::

### Інтеграція з RTOS: неблокувальні сповіщення задач

У системах під керуванням FreeRTOS або Zephyr передавальна задача не повинна витрачати процесорний час у циклі очікування прапорця `TC`. Замість цього використовують механізм прямих сповіщень задач (*Direct-to-Task Notifications*):

1. Задача формує буфер і викликає `rs485_send_async()`, який піднімає пін `DE`, запускає передачу першого байта по `TXE` і переводить задачу в стан сну через `ulTaskNotifyTake()`.
2. Процесор виконує інші корисні потоки.
3. Коли останній стоп-біт виходить у лінію, апаратне переривання `TC` опускає пін `DE`, вимикає `TCIE` і надсилає розблокувальне сповіщення задачі через виклик `vTaskNotifyGiveFromISR()`.
4. Задача миттєво прокидається і продовжує виконання без зайвих затримок і без марного спалювання тактів CPU.

### Придушення локального відлуння (Local Echo)

Коли приймач залишається підключеним до лінії під час передачі (як у випадку Single-Wire HDSEL або при заземленому виводі `/RE` у RS-485), кожен надісланий байт дзеркально потрапляє у власний приймальний буфер `RDR`.

Стратегії обробки відлуння:
- **Апаратне придушення:** об'єднання пінів `DE` та `/RE` трансивера RS-485. Коли `DE = 1` (передача), на `/RE` також подається `1`, що переводить вихід `RO` (Receiver Output) у стан Hi-Z і вимикає прийом.
- **Програмне вичитування:** лічильник переданих байтів. Під час передачі пакета довжиною `N` байтів перші `N` байтів, що надійшли в переривання `RXNE`, вважаються власним відлунням і скидаються без запису в буфер корисних повідомлень.
- **Апаратне вимкнення приймача на час передачі:** очищення біта `RE` (Receiver Enable) у `USART_CR1` перед початком передачі та його увімкнення після фіксації прапорця `TC`.

### Кільцевий буфер та нуль-копіювальний синтаксичний аналізатор

Для обробки безперервного потоку пакетів у напівдуплексній шині без затримок копіювання пам'яті застосовують структуру кільцевого буфера (*Circular Ring Buffer*). Це дає змогу вичитувати кадри на льоту:

:::tabs
```c
// Структура кільцевого буфера для прийому кадрів (C)
typedef struct {
    uint8_t storage[RS485_BUFFER_SIZE];
    volatile size_t head;
    volatile size_t tail;
} ring_buffer_t;

static inline bool ring_buffer_push(ring_buffer_t *rb, uint8_t byte) {
    size_t next = (rb->head + 1) % RS485_BUFFER_SIZE;
    if (next == rb->tail) {
        return false; // Переповнення буфера
    }
    rb->storage[rb->head] = byte;
    rb->head = next;
    return true;
}

static inline bool ring_buffer_pop(ring_buffer_t *rb, uint8_t *byte) {
    if (rb->head == rb->tail) {
        return false; // Буфер порожній
    }
    *byte = rb->storage[rb->tail];
    rb->tail = (rb->tail + 1) % RS485_BUFFER_SIZE;
    return true;
}
```
```cpp
// Інкапсульований нуль-копіювальний кільцевий буфер (C++)
#include <cstdint>
#include <cstddef>
#include <array>
#include <optional>

template <size_t Capacity = 256>
class RingBuffer {
public:
    constexpr RingBuffer() noexcept = default;

    [[nodiscard]] bool push(uint8_t byte) noexcept {
        const size_t next = (head_ + 1) % Capacity;
        if (next == tail_) {
            return false; // Переповнення буфера
        }
        storage_[head_] = byte;
        head_ = next;
        return true;
    }

    [[nodiscard]] std::optional<uint8_t> pop() noexcept {
        if (head_ == tail_) {
            return std::nullopt; // Буфер порожній
        }
        const uint8_t byte = storage_[tail_];
        tail_ = (tail_ + 1) % Capacity;
        return byte;
    }

    [[nodiscard]] size_t available() const noexcept {
        return (head_ >= tail_) ? (head_ - tail_) : (Capacity - tail_ + head_);
    }

private:
    std::array<uint8_t, Capacity> storage_{};
    volatile size_t head_{0};
    volatile size_t tail_{0};
};
```
:::

### Повна реалізація напівдуплексного драйвера

Нижче наведено модульну, виробничу реалізацію драйвера напівдуплексного зв'язку з захистом від блокування, реалізовану на мовах C та ідіоматичному C++.

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

#define RS485_BUFFER_SIZE 256

typedef enum {
    RS485_STATE_IDLE = 0,
    RS485_STATE_TRANSMITTING,
    RS485_STATE_RECEIVING,
    RS485_STATE_ERROR
} rs485_state_t;

typedef struct {
    uint8_t tx_buf[RS485_BUFFER_SIZE];
    volatile size_t tx_head;
    volatile size_t tx_len;
    uint8_t rx_buf[RS485_BUFFER_SIZE];
    volatile size_t rx_len;
    volatile rs485_state_t state;
    bool local_echo_enabled;
    volatile size_t echo_skip_count;
} rs485_driver_t;

static rs485_driver_t g_rs485;

// Керування піном DE через атомарний регістр BSRR (порт GPIOA, пін PA4)
static inline void de_pin_set_high(void) {
    GPIOA->BSRR = (1 << 4);
}

static inline void de_pin_set_low(void) {
    GPIOA->BSRR = (1 << (4 + 16));
}

void rs485_init(bool enable_local_echo) {
    g_rs485.tx_head = 0;
    g_rs485.tx_len = 0;
    g_rs485.rx_len = 0;
    g_rs485.state = RS485_STATE_IDLE;
    g_rs485.local_echo_enabled = enable_local_echo;
    g_rs485.echo_skip_count = 0;
    de_pin_set_low();
}

bool rs485_send_packet(const uint8_t *data, size_t len) {
    if (len == 0 || len > RS485_BUFFER_SIZE || g_rs485.state == RS485_STATE_TRANSMITTING) {
        return false;
    }

    for (size_t i = 0; i < len; ++i) {
        g_rs485.tx_buf[i] = data[i];
    }
    g_rs485.tx_head = 0;
    g_rs485.tx_len = len;
    g_rs485.echo_skip_count = g_rs485.local_echo_enabled ? 0 : len;
    g_rs485.state = RS485_STATE_TRANSMITTING;

    // Піднімаємо лінію DE перед першим байтом
    de_pin_set_high();

    // Записуємо перший байт і вмикаємо переривання TXE
    USART1->TDR = g_rs485.tx_buf[g_rs485.tx_head++];
    USART1->CR1 |= USART_CR1_TXEIE;

    return true;
}

// Обробник переривання USART (ISR)
void USART1_IRQHandler(void) {
    uint32_t isr = USART1->ISR;
    uint32_t cr1 = USART1->CR1;

    // 1. Очищення апаратних помилок
    usart1_clear_error_flags(isr);

    // 2. Обробка передачі: TDR звільнився (TXE)
    if ((isr & USART_ISR_TXE_TXFNF) && (cr1 & USART_CR1_TXEIE)) {
        if (g_rs485.tx_head < g_rs485.tx_len) {
            USART1->TDR = g_rs485.tx_buf[g_rs485.tx_head++];
        } else {
            // Буфер вичерпано: вимикаємо TXE, вмикаємо очікування завершення стоп-біта (TC)
            USART1->CR1 &= ~USART_CR1_TXEIE;
            USART1->CR1 |= USART_CR1_TCIE;
        }
    }

    // 3. Обробка повного завершення передачі (TC)
    if ((isr & USART_ISR_TC) && (cr1 & USART_CR1_TCIE)) {
        USART1->ICR = USART_ICR_TCCF; // Очищення прапорця TC
        USART1->CR1 &= ~USART_CR1_TCIE;
        de_pin_set_low();             // Опускаємо DE: перехід у прийом
        g_rs485.state = RS485_STATE_IDLE;
    }

    // 4. Обробка прийому даних (RXNE)
    if (isr & USART_ISR_RXNE_RXFNE) {
        uint8_t byte = (uint8_t)USART1->RDR;
        if (g_rs485.echo_skip_count > 0) {
            g_rs485.echo_skip_count--; // Скидання байта власного відлуння
        } else if (g_rs485.rx_len < RS485_BUFFER_SIZE) {
            g_rs485.rx_buf[g_rs485.rx_len++] = byte;
        }
    }
}
```
```cpp
#include <cstdint>
#include <cstddef>
#include <span>
#include <array>
#include <expected>

enum class DriverError {
    BusBusy,
    BufferOverflow,
    HardwareFault,
    Timeout
};

enum class BusState {
    Idle,
    Transmitting,
    Receiving,
    Error
};

template <size_t BufferSize = 256>
class HalfDuplexUart {
public:
    constexpr explicit HalfDuplexUart(bool suppress_echo = true) noexcept
        : suppress_local_echo_(suppress_echo) {}

    void init() noexcept {
        tx_head_ = 0;
        tx_len_ = 0;
        rx_len_ = 0;
        state_ = BusState::Idle;
        echo_to_skip_ = 0;
        set_driver_enable(false);
    }

    [[nodiscard]] std::expected<void, DriverError> send(std::span<const uint8_t> data) noexcept {
        if (data.empty() || data.size() > BufferSize) {
            return std::unexpected(DriverError::BufferOverflow);
        }
        if (state_ == BusState::Transmitting) {
            return std::unexpected(DriverError::BusBusy);
        }

        for (size_t i = 0; i < data.size(); ++i) {
            tx_buffer_[i] = data[i];
        }
        tx_len_ = data.size();
        tx_head_ = 0;
        echo_to_skip_ = suppress_local_echo_ ? tx_len_ : 0;
        state_ = BusState::Transmitting;

        // Активація режиму передачі
        set_driver_enable(true);
        start_hardware_tx();
        return {};
    }

    [[nodiscard]] std::span<const uint8_t> received_data() const noexcept {
        return std::span<const uint8_t>(rx_buffer_.data(), rx_len_);
    }

    void clear_rx_buffer() noexcept {
        rx_len_ = 0;
    }

    [[nodiscard]] BusState state() const noexcept {
        return state_;
    }

    // Обробники внутрішніх переривань апаратного контролера
    void on_txe_interrupt() noexcept {
        if (state_ != BusState::Transmitting) return;

        if (tx_head_ < tx_len_) {
            write_hw_tdr(tx_buffer_[tx_head_++]);
        } else {
            disable_hw_txe_interrupt();
            enable_hw_tc_interrupt();
        }
    }

    void on_tc_interrupt() noexcept {
        clear_hw_tc_flag();
        disable_hw_tc_interrupt();
        set_driver_enable(false); // Повернення лінії в прийом
        state_ = BusState::Idle;
    }

    void on_rxne_interrupt(uint8_t received_byte) noexcept {
        if (echo_to_skip_ > 0) {
            --echo_to_skip_;
            return;
        }
        if (rx_len_ < BufferSize) {
            rx_buffer_[rx_len_++] = received_byte;
        }
    }

private:
    std::array<uint8_t, BufferSize> tx_buffer_{};
    std::array<uint8_t, BufferSize> rx_buffer_{};
    volatile size_t tx_head_{0};
    volatile size_t tx_len_{0};
    volatile size_t rx_len_{0};
    volatile size_t echo_to_skip_{0};
    volatile BusState state_{BusState::Idle};
    bool suppress_local_echo_{true};

    // Апаратно-залежні методи доступу до регістрів
    static void set_driver_enable(bool enable) noexcept {
        if (enable) {
            GPIOA->BSRR = (1 << 4);
        } else {
            GPIOA->BSRR = (1 << (4 + 16));
        }
    }

    void start_hardware_tx() noexcept {
        USART1->TDR = tx_buffer_[tx_head_++];
        USART1->CR1 |= USART_CR1_TXEIE;
    }

    static void write_hw_tdr(uint8_t byte) noexcept {
        USART1->TDR = byte;
    }

    static void disable_hw_txe_interrupt() noexcept {
        USART1->CR1 &= ~USART_CR1_TXEIE;
    }

    static void enable_hw_tc_interrupt() noexcept {
        USART1->CR1 |= USART_CR1_TCIE;
    }

    static void clear_hw_tc_flag() noexcept {
        USART1->ICR = USART_ICR_TCCF;
    }

    static void disable_hw_tc_interrupt() noexcept {
        USART1->CR1 &= ~USART_CR1_TCIE;
    }
};
```
:::

### Осцилографічне налагодження та діагностика дефектів

При налагодженні напівдуплексного послідовного порту за допомогою 2-канального цифрового осцилографа або логічного аналізатора (канал 1 — сигнал DE, канал 2 — лінія шини) найчастіше зустрічаються чотири характерні дефекти:

1. **Обрив стоп-біта (DE Deassert Early):** сигнал DE падає в нуль у середині або на початку останнього байта. На осцилограмі видно, як рівень лінії миттєво підскакує або падає в невизначеність до завершення передачі. *Причина:* прошивка вимикає DE за прапорцем `TXE` замість `TC`.
2. **Сходинка напруги на початку відповіді (Contention Glitch):** на першому старт-біті відповіді веденого амплітуда сигналу просідає до половинного значення (близько 1.5 В) протягом 0.5...2 мкс, після чого повертається до норми. *Причина:* ведучий ще не встиг опустити DE через затримку обробника переривання, а ведений уже почав передачу. *Лікування:* збільшення захисного часу `T_guard` або використання апаратного режиму `DEM/DEDT`.
3. **Заокруглений наростаючий фронт Open-Drain (RC Slew Limit):** спадний фронт прямокутний, а наростаючий має виражену експоненційну форму зі сходинкою в районі порогу 1.5 В. *Причина:* надто великий опір підтяжки `R_pu` або надмірна ємність довгого кабелю. *Лікування:* заміна резистора підтяжки на номінал 1...2.2 кОм.
4. **Зависання прийому через прапорець Overrun (ORE Lockup):** мікроконтролер перестає приймати будь-які байти, хоча на фізичній лінії сигнал присутній. *Причина:* через затримку обробки переривання стався переповнення приймального буфера, виставився біт `ORE` у регістрі `ISR`, який блокує запис нових байтів у `RDR` доти, доки його не очистять записом у `USART_ICR_ORECF`.

### Покроковий чек-лист перевірки прошивки перед запуском у виробництво

1. **Перевірка термінації лінії:** виміряйте опір між лініями `A` і `B` при знеструмленій системі. Він має становити близько 60 Ом (два паралельні резистори по 120 Ом на крайніх вузлах). Якщо опір 120 Ом — один термінатор відсутній; якщо менше 40 Ом — хтось помилково впаяв термінатори на проміжних платах.
2. **Перевірка стану піна DE при Reset:** переконайтеся осцилографом, що під час скидання мікроконтролера лінія DE стабільно тримається на нулі завдяки резистору Pull-Down (10 кОм), не створюючи імпульсів блокування шини.
3. **Контроль закінчення передачі:** переконайтеся, що сигнал DE опускається не раніше ніж через 1 такт після завершення стоп-біта (за прапорцем `TC`).
4. **Очищення прапорців помилок:** переконайтеся, що в обробнику переривань або в циклі опитування очищаються всі прапорці помилок (`ORE`, `FE`, `NE`, `PE`).
5. **Валідація таймауту:** перевірте реакцію ведучого при повному відключенні кабелю від веденого — ведучий повинен стабільно виходити за таймаутом без зациклення й переходити до опитування наступного ідентифікатора.
