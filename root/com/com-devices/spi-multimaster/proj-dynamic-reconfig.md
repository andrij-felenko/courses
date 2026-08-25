# ⚙️ Драйвер динамічної реконфігурації шини SPI для різнорідних ведених

У сучасних вбудованих системах керування — від польотних контролерів безпілотних апаратів до медичних моніторів — єдиний апаратний блок SPI мікроконтролера змушений обслуговувати периферію з взаємовиключними вимогами. Високошвидкісна пам'ять NOR Flash працює у режимі Mode 0 (CPOL=0, CPHA=0) на граничній тактовій частоті 40 МГц із порядком бітів MSB First. Поруч на тій самій шині встановлено інерційний модуль IMU, який підтримує виключно Mode 3 (CPOL=1, CPHA=1) на частоті до 8 МГц. Додатково до шини підключено прецизійний 24-бітний сигнально-дельта АЦП, що вимагає режиму Mode 1 (CPOL=0, CPHA=1) на повільній частоті 2 МГц та передачі молодшим бітом уперед (LSB First).

Статична одноразова ініціалізація апаратних регістрів SPI під час старту мікроконтролера у такій системі принципово неможлива. Спроба виконати статичний обмін призведе до повної втрати зв'язку або спотворення даних при першому ж зверненні до «чужого» датчика. Більше того, наївна спроба перемикати біти полярності CPOL «на льоту» безпосередньо перед надсиланням байта породжує небезпечні апаратні збої: генерацію паразитних імпульсів на лінії тактування SCK, фазовий зсув слів (*Bit Slip*) та апаратні колізії ведучих Mode Fault (MODF).

Нижче наведено проектування, алгоритмічний аналіз та повну промислову реалізацію транзакційного драйвера динамічної реконфігурації шини SPI мовами C та C++, оптимізованого для багатозадачних операційних систем реального часу (FreeRTOS, Zephyr RTOS) та систем без операційної системи (Bare-Metal).

---

### 1. Анатомія апаратних проблем динамічного перемикання

Щоб спроектувати надійний драйвер, необхідно детально розібрати три фізичні явища, що виникають у кремнії контролера під час зміни параметрів шини.

#### Явище 1: Паразитний перепад SCK при зміні полярності (CPOL Glitch)

Регістр полярності тактового сигналу **CPOL** (*Clock Polarity*, від грецьк. *πόλος* — вісь, полюс) визначає рівень напруги на виводі SCK, коли передача не відбувається:
- При `CPOL = 0` лінія SCK у пасивному стані утримується нижнім N-MOSFET транзистором на рівні логічного нуля (0 В).
- При `CPOL = 1` лінія SCK у пасивному стані підтягнута верхнім P-MOSFET транзистором до напруги живлення `VCC` (+3.3 В).

Уявімо типову помилку в драйвері: програміст активував вивід вибору датчика `CS = 0`, і лише після цього вирішив змінити полярність із Mode 0 (`CPOL=0`) на Mode 3 (`CPOL=1`). Щойно мікроконтролер записує одиницю в біт `CPOL` регістра `SPI_CR1`, апаратний вихідний буфер миттєво піднімає лінію SCK з 0 В до 3.3 В. 

Оскільки вхід `CS` веденого в цей момент уже перебуває у нулі, внутрішня схема синхронізації чіпа сприймає цей стрибок напруги як **перший робочий тактовий імпульс**. Вхідний зсувний регістр веденого зсувається на один біт ще до того, як ведучий надіслав перший біт реальних даних. Як наслідок, кожен наступний байт у всій транзакції буде зміщений рівно на 1 розряд (*Bit Slip*), що руйнує пакети команд та повертає спотворені покази телеметрії.

#### Явище 2: Блокування запису в конфігураційні регістри (SPE Lock)

В архітектурі мікроконтролерів ARM Cortex-M (наприклад, лінійки STM32, NXP LPC, SAM E70) більшість керуючих бітів модуля SPI — біти вибору режиму `CPOL`, `CPHA`, розрядності `DFF/DataSize`, дільника частоти `BR[2:0]` та порядку бітів `LSBFIRST` — апаратно заблоковані від модифікації, поки активний біт дозволу периферії `SPE` (*SPI Enable*):

```
SPI_CR1: [LSBFIRST][SPE=1][BR2][BR1][BR0][MSTR][CPOL][CPHA]  ──► ЗАПИС ЗАБЛОКОВАНО!
```

Спроба змінити конфігурацію без попереднього скидання біта `SPE = 0` або просто ігнорується кремнієм, або переводить кінцевий автомат SPI у невизначений стан. Тому процедура реконфігурації зобов'язана дотримуватися суворого протоколу деактивації та повторного запуску блоку.

#### Явище 3: Небезпека колізії ведучих Mode Fault (MODF)

У багатопроцесорних або резервованих системах вивід `NSS` мікроконтролера налаштовується як апаратний вхід контролю колізій (*Hardware NSS Detection*). Якщо мікроконтролер вважає себе ведучим (`MSTR = 1`), але зовнішній контролер опускає його лінію `NSS` у нуль, апаратура фіксує аварійну ситуацію зустрічного увімкнення:
1. Біт `MSTR` у регістрі `SPI_CR1` апаратно скидається в `0`.
2. Виходи SCK та MOSI миттєво знеструмлюються і переходять у стан високого імпедансу (Hi-Z), рятуючи вихідні транзистори від теплового руйнування.
3. Встановлюється прапорець `MODF` у регістрі `SPI_SR`.

Драйвер зобов'язаний вміти детектувати цей прапорець, коректно очищати статус помилки та повідомляти операційну систему про конфлікт доступу.

---

### 2. Керування апаратними чергами FIFO та розрядністю слів

У сучасних мікроконтролерах Cortex-M4 та Cortex-M7 модуль SPI оснащено вбудованими чергами FIFO глибиною 4 або 16 рівнів (наприклад, `RXFIFO` та `TXFIFO` у мікроконтролерах серій STM32F7 та STM32H7).

При динамічній зміні конфігурації між веденими виникають специфічні апаратні пастки:
1. **Поріг заповнення FIFO прийому (`FRXTH`):** Якщо ведений використовує 8-бітний обмін, біт `FRXTH` у регістрі `SPI_CR2` повинен бути встановлений у `1`. Це налаштовує логіку на генерацію події `RXNE` при надходженні **одного байта** (8 бітів). Якщо помилково залишити `FRXTH = 0` (поріг 16 бітів), прапорець `RXNE` не підніметься доти, доки в буфер не зайде другий байт, викликавши зависання транзакції непарної довжини.
2. **Очищення залишкових байтів у FIFO:** Перед вимкненням модуля SPI (`SPE = 0`) драйвер зобов'язаний вичитати всі залишкові байти з `RXFIFO`, інакше вони потраплять у початок буфера прийому наступного датчика, спотворивши його відповідь.

---

### 3. Архітектура транзакційного шлюзу та патерни RTOS

Щоб усунути стан гонитви (*race conditions*) при одночасному зверненні кількох задач RTOS та гарантувати захисні інтервали часу, взаємодія з кожним веденим пристроєм загортається в концепцію **атомарної транзакції**:

```
[Задача RTOS A (IMU)]        [Задача RTOS B (Flash)]        [Задача RTOS C (ADC)]
         │                               │                               │
         └───────────────────────┬───────┴───────────────────────────────┘
                                 │
                                 ▼
                     ┌───────────────────────┐
                     │ SpiBusManager (Mutex) │  ──► Взаємне виключення доступу
                     └───────────┬───────────┘
                                 │
                                 ▼
                  [1. Перевірка прапорця BSY = 0]
                                 │
                                 ▼
                  [2. Деактивація всіх ліній CS = 1]
                                 │
                                 ▼
                  [3. Вимкнення периферії: SPE = 0]
                                 │
                                 ▼
                  [4. Запис CPOL, CPHA, BaudRate, FrameFormat]
                                 │
                                 ▼
                  [5. Увімкнення периферії: SPE = 1]
                                 │
                                 ▼
                  [6. Витримка паузи стабілізації t_settle]
                                 │
                                 ▼
                  [7. Активація CS цільового веденого: LOW]
                                 │
                                 ▼
                  [8. Витримка затримки вибору t_lead]
                                 │
                                 ▼
                  [9. Апаратний обмін даними (TXE/RXNE)]
                                 │
                                 ▼
                  [10. Очікування спустошення BSY = 0]
                                 │
                                 ▼
                  [11. Витримка затримки утримання t_lag]
                                 │
                                 ▼
                  [12. Деактивація CS цільового веденого: HIGH]
                                 │
                                 ▼
                  [13. Звільнення блокування Mutex]
```

#### Захист від інверсії пріоритетів в операційних системах реального часу

У середовищі RTOS (наприклад, FreeRTOS) кілька паралельних потоків із різними пріоритетами звертаються до спільної шини:
- **Високопріоритетна задача керування (200 Гц):** Опитує інерційний датчик IMU (транзакція триває 15 мкс).
- **Низькопріоритетна задача логування:** Записує масив телеметрії у Flash-пам'ять (транзакція триває 5 мс).

Якщо низькопріоритетна задача захопила м'ютекс шини, а в цей момент прокидається задача середнього пріоритету (наприклад, обробка протоколу зв'язку), планувальник витісняє низькопріоритетну задачу. У результаті високопріоритетна задача стабілізації дрона опиняється заблокованою на невизначений час через явище **інверсії пріоритетів** (*Priority Inversion*).

Для усунення цієї проблеми м'ютекс шини SPI зобов'язаний створюватися з підтримкою механізму **успадкування пріоритетів** (*Priority Inheritance*):

:::tabs
```c
// Створення м'ютекса шини з підтримкою успадкування пріоритету у FreeRTOS
SemaphoreHandle_t spi_bus_mutex = xSemaphoreCreateMutex();
```
```cpp
// У C++ обгортці для FreeRTOS або std::mutex
std::mutex spi_bus_mutex;
```
:::

Коли високопріоритетний потік намагається захопити зайнятий м'ютекс, планувальник RTOS тимчасово підвищує пріоритет поточного володаря м'ютекса до рівня очікуючого потоку, змушуючи його якнайшвидше завершити транзакцію та відпустити шину.

#### Патерн «Сервер шини» (Bus Server Pattern)

У критичних системах замість розподіленого захоплення м'ютекса часто застосовують архітектурний патерн **Bus Server**:
1. Створюється єдиний виділений потік-сервер шини `SpiServerTask`.
2. Інші задачі формують запити у вигляді структур транзакцій і надсилають їх у чергу повідомлень `QueueHandle_t spi_queue`.
3. Потік-сервер послідовно вичитує запити з черги, виконує динамічну реконфігурацію регістрів, здійснює обмін по шині та сповіщає задачу-замовника через пряме адресне повідомлення (*Direct-to-Task Notification*).
4. **Перевага патерну:** Повна ліквідація дедлоків, централізований облік помилок шини та можливість безпечного виклику неблокуючих транзакцій із контексту переривань `xQueueSendFromISR()`.

:::tabs
```c
// Повідомлення задачі-сервера шини FreeRTOS (C)
typedef struct {
    const spi_slave_config_t* slave_cfg;
    const uint8_t*            tx_data;
    uint8_t*                  rx_data;
    size_t                    length;
    TaskHandle_t              caller_task;
    spi_status_t              result_status;
} spi_transaction_request_t;
```
```cpp
// Повідомлення задачі-сервера шини (C++)
struct SpiTransactionRequest {
    const SpiSlaveConfig*          slaveCfg{nullptr};
    std::span<const uint8_t>       txData{};
    std::span<uint8_t>             rxData{};
    TaskHandle_t                   callerTask{nullptr};
    std::expected<void, SpiError>  resultStatus{};
};
```
:::

#### Узгодженість кеш-пам'яті (Cache Coherency) при роботі з DMA на Cortex-M7

На високопродуктивних мікроконтролерах із кешем даних D-Cache (STM32H7, i.MX RT1060) передача блоків через DMA вимагає спеціальної обробки пам'яті:
1. **Перед запуском передачі TX-DMA:** Виконується операція очищення кешу `SCB_CleanDCache_by_Addr()`, яка скидає змінені процесором байти з кешу L1 у фізичну пам'ять SRAM, звідки їх зчитуватиме контролер DMA.
2. **Після завершення прийому RX-DMA:** Виконується операція інвалідації кешу `SCB_InvalidateDCache_by_Addr()`, яка змушує процесор перечитати оновлені контролером DMA байти з оперативної пам'яті, а не використовувати застарілі дані з кешу.

#### Подвійна буферизація DMA (Ping-Pong Buffering)

Для потокових операцій високої пропускної здатності (наприклад, неперервного читання даних з АЦП на частоті 1 МГц) застосовують подвійну буферизацію DMA:

```
[Потік SPI] ──► DMA Channel ──► Буфер A (Заповнюється контролером DMA)
                                Буфер B (Обробляється процесором)
                                  ▲
                                  │ (По події DMA_HalfTransfer перемикаються)
```

При динамічній зміні веденого циклічний режим DMA обов'язково зупиняють, вичитують залишок байтів з апаратного FIFO SPI та проводять реконфігурацію параметрів перед запуском нового дескриптора.

#### Часові інтервали захисту (Guard Times)
1. **`t_settle` (Час стабілізації спокою):** Інтервал між увімкненням модуля SPI з новим бітом `CPOL` та активацією лінії `CS`. Необхідний для того, щоб вихідний буфер встиг зарядити або розрядити лінію SCK до нового стаціонарного рівня (зазвичай `1...5 мкс`).
2. **`t_lead` (Час випередження вибору):** Інтервал між опусканням лінії `CS` у нуль та генерацією першого перепаду `SCK`. Вимагається більшістю мікросхем для пробудження внутрішнього аналогового тракту з режиму глибокого сну.
3. **`t_lag` (Час утримання після такту):** Інтервал між останнім спадом `SCK` та підняттям лінії `CS` у високий рівень. Запобігає обрізанню фази фіксації останнього біта.

---

### 4. Архітектура підсистеми SPI у ядрі Linux

У вбудованих Linux-системах (наприклад, на базі процесорів NXP i.MX, TI Sitara, Allwinner або Raspberry Pi) динамічна реконфігурація шини реалізована на рівні підсистеми ядра `drivers/spi/`.

Структура `spi_transfer` описує окремий атомарний сегмент транзакції, де кожен сегмент може мати індивідуальні параметри:

:::tabs
```c
// Структура ядра Linux drivers/spi/ (C)
struct spi_transfer {
    const void *tx_buf;     // Буфер передачі
    void       *rx_buf;     // Буфер прийому
    unsigned    len;        // Довжина в байтах
    uint32_t    speed_hz;   // Динамічна швидкість для цього сегмента
    uint16_t    delay_usecs;// Пауза після сегмента (t_lag)
    uint8_t     bits_per_word; // Розрядність слів (8, 16, 32)
    uint8_t     cs_change;  // Деактивувати CS між сегментами
};
```
```cpp
// Структура дескриптора передачі (C++)
struct LinuxSpiTransferDescriptor {
    std::span<const uint8_t> txBuffer{};
    std::span<uint8_t>       rxBuffer{};
    uint32_t                 speedHz{0};
    uint16_t                 delayUsecs{0};
    uint8_t                  bitsPerWord{8};
    bool                     csChange{false};
};
```
:::

Драйвер контролера ядра (наприклад, `spi-imx.c` або `spi-stm32.c`) перед виконанням кожного дескриптора автоматично звіряє його `speed_hz`, `mode` та `bits_per_word` із поточним станом апаратних регістрів і за потреби виконує реконфігурацію апаратного модуля безпосередньо у ядрі.

---

### 5. Промислова реалізація драйвера

Нижче наведено закінчену реалізацію драйвера мовами C (чистий процедурний стиль із прямим доступом до регістрів) та C++ (об'єктно-орієнтований підхід із семантикою RAII, `std::span` та `std::expected`).

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

// Режими тактування шини SPI
typedef enum {
    SPI_CLOCK_MODE_0 = 0, // CPOL = 0, CPHA = 0 (спокій низький, вибірка по наростанню)
    SPI_CLOCK_MODE_1 = 1, // CPOL = 0, CPHA = 1 (спокій низький, вибірка по спаданню)
    SPI_CLOCK_MODE_2 = 2, // CPOL = 1, CPHA = 0 (спокій високий, вибірка по спаданню)
    SPI_CLOCK_MODE_3 = 3  // CPOL = 1, CPHA = 1 (спокій високий, вибірка по наростанню)
} spi_clock_mode_t;

// Порядок передачі розрядів
typedef enum {
    SPI_BIT_ORDER_MSB_FIRST = 0,
    SPI_BIT_ORDER_LSB_FIRST = 1
} spi_bit_order_t;

// Статуси виконання транзакцій
typedef enum {
    SPI_STATUS_OK = 0,
    SPI_STATUS_INVALID_ARG,
    SPI_STATUS_MODE_FAULT,
    SPI_STATUS_TIMEOUT,
    SPI_STATUS_BUSY
} spi_status_t;

// Конфігураційний профіль конкретного веденого пристрою
typedef struct {
    uint32_t         baudrate_hz;    // Бажана тактова частота (Гц)
    spi_clock_mode_t clock_mode;     // Режим фази та полярності (Mode 0..3)
    spi_bit_order_t  bit_order;      // Порядок бітів (MSB / LSB)
    uint8_t          cs_port_id;     // Ідентифікатор порту GPIO
    uint8_t          cs_pin_num;     // Номер виводу GPIO
    uint16_t         lead_delay_us;  // Захисний інтервал t_lead (мкс)
    uint16_t         lag_delay_us;   // Захисний інтервал t_lag (мкс)
    uint16_t         settle_delay_us;// Захисний інтервал t_settle (мкс)
} spi_slave_config_t;

// Апаратний дескриптор шини SPI
typedef struct {
    volatile uint32_t* CR1;          // Регістр керування 1
    volatile uint32_t* CR2;          // Регістр керування 2
    volatile uint32_t* SR;           // Регістр статусу
    volatile uint32_t* DR;           // Регістр даних
    uint32_t           bus_clock_hz; // Базова частота тактування шини (APB)
    bool               mode_fault_flag;
} spi_bus_hw_t;

// Бітові маски регістрів SPI (стандартна архітектура Cortex-M)
#define SPI_CR1_SPE        (1u << 6)  // SPI Enable (дозвіл роботи)
#define SPI_CR1_MSTR       (1u << 2)  // Master Selection (режим ведучого)
#define SPI_CR1_CPOL       (1u << 1)  // Clock Polarity (полярність спокою)
#define SPI_CR1_CPHA       (1u << 0)  // Clock Phase (фаза вибірки)
#define SPI_CR1_LSBFIRST   (1u << 7)  // Frame Format (LSB/MSB)
#define SPI_CR1_BR_MASK    (7u << 3)  // Маска бітів дільника Baud Rate

#define SPI_SR_TXE         (1u << 1)  // Transmit Buffer Empty (буфер передачі порожній)
#define SPI_SR_RXNE        (1u << 0)  // Receive Buffer Not Empty (прийнято байт)
#define SPI_SR_BSY         (1u << 7)  // Busy Flag (шина зайнята обміном)
#define SPI_SR_MODF        (1u << 5)  // Mode Fault Flag (помилка колізії)

// Апаратні зовнішні виклики (HAL / Board Support Package)
extern void gpio_write_pin(uint8_t port, uint8_t pin, bool level);
extern void delay_microseconds(uint32_t us);
extern void spi_mutex_lock(void);
extern void spi_mutex_unlock(void);

// Розрахунок дільника частоти Baud Rate Prescaler
static uint32_t spi_calc_prescaler(uint32_t bus_clk, uint32_t target_baud)
{
    uint32_t div = bus_clk / target_baud;
    if (div <= 2)   return (0u << 3); // Дільник /2
    if (div <= 4)   return (1u << 3); // Дільник /4
    if (div <= 8)   return (2u << 3); // Дільник /8
    if (div <= 16)  return (3u << 3); // Дільник /16
    if (div <= 32)  return (4u << 3); // Дільник /32
    if (div <= 64)  return (5u << 3); // Дільник /64
    if (div <= 128) return (6u << 3); // Дільник /128
    return (7u << 3);                 // Дільник /256
}

// Безпечна динамічна реконфігурація регістрів
static spi_status_t spi_reconfigure(spi_bus_hw_t* bus, const spi_slave_config_t* cfg)
{
    // 1. Перевірка прапорця Mode Fault від попередніх операцій
    if (*(bus->SR) & SPI_SR_MODF) {
        // Очищення MODF: читання регістра SR з наступним записом CR1
        volatile uint32_t dummy = *(bus->SR);
        (void)dummy;
        *(bus->CR1) |= SPI_CR1_MSTR; // Відновлення біта ведучого
        bus->mode_fault_flag = true;
        return SPI_STATUS_MODE_FAULT;
    }

    // 2. Очікування повного звільнення апаратного зсувного регістра
    uint32_t timeout = 100000;
    while ((*(bus->SR) & SPI_SR_BSY) && (--timeout > 0));
    if (timeout == 0) {
        return SPI_STATUS_TIMEOUT;
    }

    // 3. Тимчасове вимкнення модуля SPI для розблокування регістрів
    *(bus->CR1) &= ~SPI_CR1_SPE;

    // 4. Формування нового значення конфігураційного слова CR1
    uint32_t cr1_val = *(bus->CR1);
    cr1_val &= ~(SPI_CR1_CPOL | SPI_CR1_CPHA | SPI_CR1_LSBFIRST | SPI_CR1_BR_MASK);

    // Встановлення полярності та фази
    if (cfg->clock_mode == SPI_CLOCK_MODE_2 || cfg->clock_mode == SPI_CLOCK_MODE_3) {
        cr1_val |= SPI_CR1_CPOL;
    }
    if (cfg->clock_mode == SPI_CLOCK_MODE_1 || cfg->clock_mode == SPI_CLOCK_MODE_3) {
        cr1_val |= SPI_CR1_CPHA;
    }

    // Встановлення порядку бітів
    if (cfg->bit_order == SPI_BIT_ORDER_LSB_FIRST) {
        cr1_val |= SPI_CR1_LSBFIRST;
    }

    // Встановлення швидкості тактування
    cr1_val |= spi_calc_prescaler(bus->bus_clock_hz, cfg->baudrate_hz);
    cr1_val |= SPI_CR1_MSTR; // Завжди ведучий

    // 5. Запис конфігурації та повторне увімкнення блоку SPI
    *(bus->CR1) = cr1_val;
    *(bus->CR1) |= SPI_CR1_SPE;

    // 6. Захисна пауза стабілізації рівня спокою SCK перед активацією CS
    if (cfg->settle_delay_us > 0) {
        delay_microseconds(cfg->settle_delay_us);
    }

    return SPI_STATUS_OK;
}

// Виконання повнодуплексної транзакції
spi_status_t spi_transfer_transaction(
    spi_bus_hw_t*             bus,
    const spi_slave_config_t* cfg,
    const uint8_t*            tx_buf,
    uint8_t*                  rx_buf,
    size_t                    len)
{
    if (!bus || !cfg || len == 0) {
        return SPI_STATUS_INVALID_ARG;
    }

    // Захоплення м'ютекса для взаємного виключення в RTOS
    spi_mutex_lock();

    // 1. Динамічна реконфігурація регістрів під цільовий ведений
    spi_status_t status = spi_reconfigure(bus, cfg);
    if (status != SPI_STATUS_OK) {
        spi_mutex_unlock();
        return status;
    }

    // 2. Активація виводу CS (опускання в нуль)
    gpio_write_pin(cfg->cs_port_id, cfg->cs_pin_num, false);

    // 3. Затримка t_lead перед генерацією першого такту
    if (cfg->lead_delay_us > 0) {
        delay_microseconds(cfg->lead_delay_us);
    }

    // 4. Побайтний дуплексний обмін через апаратний регістр даних
    for (size_t i = 0; i < len; ++i) {
        // Перевірка колізії Mode Fault під час транзакції
        if (*(bus->SR) & SPI_SR_MODF) {
            status = SPI_STATUS_MODE_FAULT;
            break;
        }

        // Очікування готовності передавача (TXE = 1)
        uint32_t timeout = 100000;
        while (!(*(bus->SR) & SPI_SR_TXE) && (--timeout > 0));
        if (timeout == 0) { status = SPI_STATUS_TIMEOUT; break; }

        uint8_t byte_out = tx_buf ? tx_buf[i] : 0xFF;
        *(bus->DR) = byte_out;

        // Очікування прийому байта у відповідь (RXNE = 1)
        timeout = 100000;
        while (!(*(bus->SR) & SPI_SR_RXNE) && (--timeout > 0));
        if (timeout == 0) { status = SPI_STATUS_TIMEOUT; break; }

        uint8_t byte_in = (uint8_t)(*(bus->DR));
        if (rx_buf) {
            rx_buf[i] = byte_in;
        }
    }

    // 5. Очікування повного завершення передачі останнього біта (BSY = 0)
    uint32_t timeout = 100000;
    while ((*(bus->SR) & SPI_SR_BSY) && (--timeout > 0));

    // 6. Затримка t_lag після останнього такту
    if (cfg->lag_delay_us > 0) {
        delay_microseconds(cfg->lag_delay_us);
    }

    // 7. Деактивація виводу CS (підняття у високий рівень)
    gpio_write_pin(cfg->cs_port_id, cfg->cs_pin_num, true);

    // Звільнення блокування шини
    spi_mutex_unlock();

    return status;
}
```
```cpp
#include <cstdint>
#include <cstddef>
#include <span>
#include <expected>
#include <mutex>
#include <concepts>

namespace embedded::drivers {

enum class SpiClockMode : uint8_t {
    Mode0 = 0, // CPOL = 0, CPHA = 0 (Idle LOW, Sample Rising)
    Mode1 = 1, // CPOL = 0, CPHA = 1 (Idle LOW, Sample Falling)
    Mode2 = 2, // CPOL = 1, CPHA = 0 (Idle HIGH, Sample Falling)
    Mode3 = 3  // CPOL = 1, CPHA = 1 (Idle HIGH, Sample Rising)
};

enum class SpiBitOrder : uint8_t {
    MsbFirst = 0,
    LsbFirst = 1
};

enum class SpiError : uint8_t {
    InvalidArguments,
    ModeFault,
    Timeout,
    BusBusy
};

struct SpiSlaveConfig {
    uint32_t         baudrateHz;
    SpiClockMode     clockMode;
    SpiBitOrder      bitOrder;
    uint8_t          csPortId;
    uint8_t          csPinNum;
    uint16_t         leadDelayUs{2};   // t_lead
    uint16_t         lagDelayUs{2};    // t_lag
    uint16_t         settleDelayUs{2}; // t_settle
};

// RAII охоронець виводу Chip Select
template <typename GpioDriver>
class ChipSelectGuard {
public:
    ChipSelectGuard(GpioDriver& gpio, uint8_t port, uint8_t pin, uint16_t leadUs, uint16_t lagUs) noexcept
        : m_gpio{gpio}, m_port{port}, m_pin{pin}, m_lagUs{lagUs}
    {
        m_gpio.writePin(m_port, m_pin, false); // Активація CS (LOW)
        if (leadUs > 0) {
            m_gpio.delayUs(leadUs);
        }
    }

    ~ChipSelectGuard() noexcept {
        if (m_lagUs > 0) {
            m_gpio.delayUs(m_lagUs);
        }
        m_gpio.writePin(m_port, m_pin, true);  // Деактивація CS (HIGH)
    }

    ChipSelectGuard(const ChipSelectGuard&) = delete;
    ChipSelectGuard& operator=(const ChipSelectGuard&) = delete;

private:
    GpioDriver& m_gpio;
    uint8_t     m_port;
    uint8_t     m_pin;
    uint16_t    m_lagUs;
};

// Транзакційний менеджер шини SPI
template <typename SpiRegisters, typename GpioDriver, typename MutexType>
class SpiBusManager {
public:
    constexpr SpiBusManager(
        SpiRegisters& registers,
        GpioDriver&   gpio,
        MutexType&    mutex,
        uint32_t      busClockHz) noexcept
        : m_regs{registers}, m_gpio{gpio}, m_mutex{mutex}, m_busClockHz{busClockHz} {}

    [[nodiscard]] std::expected<void, SpiError> transfer(
        const SpiSlaveConfig& cfg,
        std::span<const uint8_t> txBuffer,
        std::span<uint8_t> rxBuffer) noexcept
    {
        const size_t len = txBuffer.empty() ? rxBuffer.size() : txBuffer.size();
        if (len == 0) {
            return std::unexpected(SpiError::InvalidArguments);
        }

        // Захоплення м'ютекса через RAII
        std::lock_guard<MutexType> lock(m_mutex);

        // Динамічна реконфігурація регістрів
        if (auto res = reconfigure(cfg); !res) {
            return std::unexpected(res.error());
        }

        // Керування виводом CS через RAII охоронець
        ChipSelectGuard<GpioDriver> csGuard(
            m_gpio, cfg.csPortId, cfg.csPinNum, cfg.leadDelayUs, cfg.lagDelayUs);

        // Повнодуплексний обмін даними
        for (size_t i = 0; i < len; ++i) {
            if (m_regs.SR & SpiRegisters::SR_MODF) {
                return std::unexpected(SpiError::ModeFault);
            }

            // Очікування готовності передавача (TXE)
            if (!waitForFlag(SpiRegisters::SR_TXE, true)) {
                return std::unexpected(SpiError::Timeout);
            }

            const uint8_t outByte = txBuffer.empty() ? 0xFF : txBuffer[i];
            m_regs.DR = outByte;

            // Очікування готовності приймача (RXNE)
            if (!waitForFlag(SpiRegisters::SR_RXNE, true)) {
                return std::unexpected(SpiError::Timeout);
            }

            const uint8_t inByte = static_cast<uint8_t>(m_regs.DR);
            if (!rxBuffer.empty()) {
                rxBuffer[i] = inByte;
            }
        }

        // Очікування повного спустошення зсувного регістра (BSY = 0)
        if (!waitForFlag(SpiRegisters::SR_BSY, false)) {
            return std::unexpected(SpiError::Timeout);
        }

        return {};
    }

private:
    [[nodiscard]] std::expected<void, SpiError> reconfigure(const SpiSlaveConfig& cfg) noexcept {
        // Перевірка прапорця Mode Fault
        if (m_regs.SR & SpiRegisters::SR_MODF) {
            [[maybe_unused]] volatile uint32_t dummy = m_regs.SR;
            m_regs.CR1 |= SpiRegisters::CR1_MSTR;
            return std::unexpected(SpiError::ModeFault);
        }

        if (!waitForFlag(SpiRegisters::SR_BSY, false)) {
            return std::unexpected(SpiError::Timeout);
        }

        // Вимкнення SPI перед зміною керуючих бітів
        m_regs.CR1 &= ~SpiRegisters::CR1_SPE;

        uint32_t cr1 = m_regs.CR1;
        cr1 &= ~(SpiRegisters::CR1_CPOL | SpiRegisters::CR1_CPHA | 
                 SpiRegisters::CR1_LSBFIRST | SpiRegisters::CR1_BR_MASK);

        if (cfg.clockMode == SpiClockMode::Mode2 || cfg.clockMode == SpiClockMode::Mode3) {
            cr1 |= SpiRegisters::CR1_CPOL;
        }
        if (cfg.clockMode == SpiClockMode::Mode1 || cfg.clockMode == SpiClockMode::Mode3) {
            cr1 |= SpiRegisters::CR1_CPHA;
        }

        if (cfg.bitOrder == SpiBitOrder::LsbFirst) {
            cr1 |= SpiRegisters::CR1_LSBFIRST;
        }

        cr1 |= calculatePrescaler(cfg.baudrateHz);
        cr1 |= SpiRegisters::CR1_MSTR;

        m_regs.CR1 = cr1;
        m_regs.CR1 |= SpiRegisters::CR1_SPE;

        if (cfg.settleDelayUs > 0) {
            m_gpio.delayUs(cfg.settleDelayUs);
        }

        return {};
    }

    [[nodiscard]] uint32_t calculatePrescaler(uint32_t targetBaud) const noexcept {
        const uint32_t div = m_busClockHz / targetBaud;
        if (div <= 2)   return (0u << 3);
        if (div <= 4)   return (1u << 3);
        if (div <= 8)   return (2u << 3);
        if (div <= 16)  return (3u << 3);
        if (div <= 32)  return (4u << 3);
        if (div <= 64)  return (5u << 3);
        if (div <= 128) return (6u << 3);
        return (7u << 3);
    }

    [[nodiscard]] bool waitForFlag(uint32_t mask, bool expectedSet) const noexcept {
        uint32_t timeout = 100000;
        while (--timeout > 0) {
            const bool isSet = (m_regs.SR & mask) != 0;
            if (isSet == expectedSet) {
                return true;
            }
        }
        return false;
    }

    SpiRegisters& m_regs;
    GpioDriver&   m_gpio;
    MutexType&    m_mutex;
    uint32_t      m_busClockHz;
};

} // namespace embedded::drivers
```
:::

---

### 6. Модульне тестування з Mock-об'єктами (Unit Testing & CI/CD)

Для перевірки стійкості драйвера до відмов апаратури в конвеєрах неперервної інтеграції (CI/CD) створюють синтетичні тестові каркаси з емуляцією регістрів:

```cpp
// Тестовий Mock для емуляції апаратного модуля SPI
struct MockSpiRegisters {
    static constexpr uint32_t CR1_SPE     = (1u << 6);
    static constexpr uint32_t CR1_MSTR    = (1u << 2);
    static constexpr uint32_t CR1_CPOL    = (1u << 1);
    static constexpr uint32_t CR1_CPHA    = (1u << 0);
    static constexpr uint32_t CR1_LSBFIRST= (1u << 7);
    static constexpr uint32_t CR1_BR_MASK = (7u << 3);

    static constexpr uint32_t SR_TXE      = (1u << 1);
    static constexpr uint32_t SR_RXNE     = (1u << 0);
    static constexpr uint32_t SR_BSY      = (1u << 7);
    static constexpr uint32_t SR_MODF     = (1u << 5);

    uint32_t CR1{CR1_MSTR | CR1_SPE};
    uint32_t CR2{0};
    uint32_t SR{SR_TXE | SR_RXNE};
    uint32_t DR{0x00};
};

struct MockGpio {
    void writePin(uint8_t port, uint8_t pin, bool level) {
        lastPort = port;
        lastPin = pin;
        lastLevel = level;
    }
    void delayUs(uint32_t us) { totalDelayUs += us; }

    uint8_t  lastPort{0};
    uint8_t  lastPin{0};
    bool     lastLevel{true};
    uint32_t totalDelayUs{0};
};
```

Такий підхід дозволяє перевірити:
1. **Тест Mode Fault:** Встановлення прапорця `SR_MODF` викликає повернення помилки `SpiError::ModeFault` та автоматичне відновлення біта `CR1_MSTR`.
2. **Тест Guard Times:** Перевірка, що сумарний час затримок `totalDelayUs` точно відповідає сумі `t_settle + t_lead + t_lag`.
3. **Тест коректності черговості:** Перевірка, що лінія CS опускається в нуль суворо **після** оновлення бітів `CPOL` у регістрі `CR1`.

---

### 7. Аналіз продуктивності та накладних витрат (Profiling & Benchmarks)

При виборі методу взаємодії з шиною (побайтове опитування, переривання чи DMA) інженер оцінює баланс між накладними витратами процесора та затримкою запуску:

1. **Метод побайтового опитування (Polling):**
   - *Накладні витрати на реконфігурацію:* ~1.2 мкс (скидання SPE, оновлення CR1, відновлення SPE).
   - *Час запуску транзакції:* Мінімальний (< 0.5 мкс).
   - *Використання:* Короткі транзакції від 1 до 8 байтів (читання показів акселерометра, налаштування регістрів ЦАП). Завантаження CPU під час очікування прапорця `BSY` не перевищує 5–10 мкс, що значно швидше за накладні витрати планувальника RTOS.

2. **Метод переривань (Interrupt-Driven):**
   - *Накладні витрати на байт:* Вхід та вихід із контексту ISR займає 1.5–3.0 мкс на ядрі Cortex-M4.
   - *Обмеження:* На частотах понад 10 МГц (де 8 бітів передаються швидше, ніж за 800 нс) потік переривань призводить до перевантаження процесора (*interrupt storm*), паралізуючи виконання фонових задач.

3. **Метод прямого доступу до пам'яті (DMA):**
   - *Накладні витрати на конфігурацію дескриптора:* ~4.0...6.0 мкс (запис базових адрес, лічильника довжини, налаштування тригерів).
   - *Продуктивність:* При обсягах даних понад 32 байти (Flash-пам'ять, OLED-дисплеї) DMA забезпечує 100% звільнення обчислювальних ресурсів процесора.

---

### 8. Інженерні пастки та діагностика осцилографом

При зневадженні систем із динамічною реконфігурацією SPI інженери найчастіше стикаються з чотирма критичними симптомами:

1. **Симптом «Зсув на 1 біт у першому байті після зміни пристрою»:**
   - **Діагностика:** Осцилограф підключають до каналів CS та SCK. Якщо на осцилограмі видно, що рівень SCK піднімається з 0 до 3.3 В у той момент, коли лінія CS уже опустилася в нуль, ведений фіксує хибний тактовий фронт.
   - **Виправлення:** Збільшити інтервал `t_settle` між увімкненням модуля SPI (`SPE=1`) та активацією `CS`, перевіривши, що конфігурація змінюється виключно при пасивному стані всіх ліній CS (`CS=1`).

2. **Симптом «Обрізання старшого або молодшого біта останнього байта пакета»:**
   - **Діагностика:** Лінія CS піднімається у високий рівень раніше, ніж завершився останній імпульс на лінії SCK.
   - **Причина:** Програма перевірила прапорець `TXE = 1` і негайно підняла CS. Прапорець `TXE` означає лише те, що буфер передавача порожній, але останній байт усе ще висувається з внутрішнього зсувного регістра.
   - **Виправлення:** Завжди чекати скидання прапорця зайнятості `BSY == 0` перед викликом `gpio_write_pin(CS, HIGH)`.

3. **Симптом «Контролер зависає з помилкою HardFault або дедлоком у RTOS»:**
   - **Причина:** Спроба виконати динамічну транзакцію з контексту обробника апаратного переривання (ISR), де виклик блокуючого м'ютекса (`std::lock_guard` або `spi_mutex_lock`) заборонений планувальником операційної системи.
   - **Архітектурне виправлення:** Обробник переривання не повинен безпосередньо звертатися до шини; він лише надсилає повідомлення в чергу задачі-сервера шини через неблокуючий виклик `xQueueSendFromISR()`.

4. **Симптом «Хибне спрацьовування Mode Fault без наявності другого ведучого»:**
   - **Причина:** Вивід `NSS` налаштований в апаратному режимі, але лінію залишили без зовнішнього резистора підтяжки 10 кОм до `VCC`. Наведення від сусідніх сигналів SCK короткочасно просаджують напругу на `NSS` нижче 1.0 В, скидаючи біт `MSTR`.
   - **Виправлення:** Якщо апаратний арбітраж не потрібен, вивід NSS перемикають у програмний режим (`SSM=1`, `SSI=1` у регістрі `SPI_CR1`), або встановлюють надійний фізичний підтягуючий резистор.
