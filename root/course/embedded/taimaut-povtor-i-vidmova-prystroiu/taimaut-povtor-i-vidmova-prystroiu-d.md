# Таймаут, повтор і відмова пристрою

<preknowlist>
- [Як чипи розмовляють: навіщо шини](root:embedded/why-buses) — фізика ліній зв'язку I2C/SPI, таймінги, стан готовності та арбітраж.
- [Драйвер чипа: від регістрової карти до значення у SI](root:embedded/draiver-chypa) — рівнева архітектура драйвера, абстракція транспорту та статусний код повернення.
- [Послідовність ініціалізації: порядок, затримки, перевірка](root:embedded/poslidovnist-initsializatsii) — часові інтервали POR, перехідні процеси живлення та перевірка ідентифікатора.
- [Блокуючий і неблокуючий ввід-вивід](root:sf-tasks/blocking-vs-nonblocking-io) — блокування потоків на очікуванні подій, небезпека затримки та асинхронні переходи.
- [Жодна помилка не мовчить](root:sf-apps/error-handling) — таксономія кодів повернення, обробка збоїв і захисне програмування.
</preknowlist>

Коли бортовий контролер промислового газового пальника або автопілот безпілотного літака опитує цифровий датчик тиску через шину I2C, розробник-початківець зазвичай пише прямий виклик зчитування регістра у головному циклі програми. За стабільного лабораторного живлення на столі такий код виконується за 150 мікросекунд і щоразу повертає очікувані байти. Проте варто вібрації від двигуна на частку мілісекунди порушити контакт у роз'ємі лінії тактування SCL або імпульсній заваді від запалювання викликати короткочасне просідання напруги на платі датчика, як процесор намертво застрягає в циклі `while (!(I2C1->SR1 & I2C_SR1_RXNE))`. Переривання таймерів можуть продовжувати цокати, але головний потік керування зупиняється назавжди: клапан подачі газу залишається відкритим, сервоприводи елеронів завмирають у крайньому положенні, а сторожовий таймер або перезавантажує мікроконтролер посеред польоту, або взагалі не спрацьовує, якщо його скидання необачно винесли в обробник апаратного таймерного переривання.

Ця аварія розкриває фундаментальну асиметрію вбудованих систем: внутрішні регістри периферії мікроконтролера гарантовано відповідають за фіксовану кількість тактів процесорного ядра, тоді як зовнішній пристрій на друкованій платі або кабельному шлейфі є принципово ненадійним фізичним середовищем. Зовнішній чип може раптово знеструмитися, зависнути у власному внутрішньому циклі очікування аналого-цифрового перетворення, затиснути лінію зв'язку в нуль через апаратне розтягування такту *(англ. Clock Stretching)* або зазнати збою від електромагнітної наводки. Програма, яка безумовно очікує відповіді від зовнішнього заліза без обмеження часу, перетворює будь-який локальний електричний шум на фатальну відмову всього приладу.

> 🔧 **Навіщо це.** Стійкий драйвер розглядає шину зв'язку не як надійну локальну пам'ять, а як ворожий розподілений канал з імовірнісними збоями. Впровадження детермінованих апаратних таймаутів, розрізнення тимчасових завад і фатальних поломок, експоненційний відкат повторів та автоматична ізоляція мертвого чипа через патерн Circuit Breaker гарантують, що збій окремого датчика ніколи не викличе колапс процесора, а система контрольовано перейде в безпечний режим деградації.

---

## Анатомія мертвого зависання: Пастка вічного опитування прапорців

Типовий низькорівневий драйвер, згенерований графічним конфігуратором або списаний з навчального посібника, переповнений конструкціями прямого очікування готовності апаратного периферійного модуля мікроконтролера.

:::tabs
```c
/* Смертельна пастка: нескінченне блокуюче опитування прапорця шини */
void i2c_write_byte_naive(I2C_TypeDef *i2c, uint8_t data) {
    i2c->DR = data;
    while (!(i2c->SR1 & I2C_SR1_TXE)) {
        /* Чекаємо, поки буфер передачі звільниться */
    }
    while (!(i2c->SR1 & I2C_SR1_BTF)) {
        /* Чекаємо завершення передачі байта на фізичній шині */
    }
}
```
```cpp
#include <cstdint>

// Смертельна пастка у стилі C++: блокуюче опитування регістрів без дедлайну
struct I2cRegisters {
    volatile uint32_t CR1;
    volatile uint32_t CR2;
    volatile uint32_t SR1;
    volatile uint32_t SR2;
    volatile uint32_t DR;
};

void i2c_write_byte_naive(I2cRegisters* i2c, uint8_t data) noexcept {
    i2c->DR = data;
    constexpr uint32_t TXE_FLAG = (1UL << 7);
    constexpr uint32_t BTF_FLAG = (1UL << 2);

    while ((i2c->SR1 & TXE_FLAG) == 0) {
        // Очікування без дедлайну блокує потік назавжди
    }
    while ((i2c->SR1 & BTF_FLAG) == 0) {
        // Зависання при відриві SCL або утриманні лінії веденим чипом
    }
}
```
:::

У нормальних умовах передача одного байта на шині I2C із частотою 400 кГц триває 9 тактових імпульсів:

```
t_byte  =  9 ÷ 400000 Гц  =  22.5 мкс
```

Здається, що цикл виконається за кілька сотень тактів процесора на частоті 168 МГц і миттєво завершиться. Проте прапорець `BTF` *(Byte Transfer Finished)* або `TXE` *(Transmit Data Register Empty)* формується не процесором, а внутрішньою логікою шинного контролера МК на основі аналізу електричних сигналів на зовнішніх ніжках мікроконтролера.

![Порівняння реакцій системи на апаратний збій периферії](/root/course/embedded/taimaut-povtor-i-vidmova-prystroiu/img/spinning-trap-vs-timeout.svg)
*Порівняння наслідків нескінченного опитування прапорця та детермінованого таймауту під час фізичного відриву лінії або зависання зовнішнього чипа.*

### Фізичні причини блокування апаратних прапорців

Існує п'ять фізичних сценаріїв, за яких апаратний прапорець шини ніколи не перейде в активний стан:

1. **Зависання лінії веденим чипом через Clock Stretching:** Стандарт I2C дозволяє повільному веденому пристрою примусово притягнути лінію SCL до землі (рівень логічного нуля), якщо він не встигає обробити попередній байт або виконує внутрішнє аналогове перетворення. Якщо ведений мікроконтролер чи датчик зазнав програмного збою, випав у HardFault або знеструмився посеред розтягування, лінія SCL залишається замкненою на нуль назавжди. Контролер I2C ведучого зупиняє генерацію тактових імпульсів і чекає відпускання лінії, а прапорець `BTF` не виставляється ніколи.
2. **Обрив підтягувального резистора (Pull-up) або живлення шини:** Якщо лінія відкритого стоку втрачає резистивну підтяжку до напруги живлення V_DD, вхідні буфери фіксують постійний низький рівень. Шинний автомат фіксує стан `BUSY` *(шина зайнята чужою транзакцією)* і блокує старт будь-якої передачі.
3. **Паразитне живлення через захисні діоди (Phantom Powering):** Якщо зовнішній модуль втратив штатне живлення V_DD через обрив доріжки чи перегорання LDO, струм з сигнальних ліній SCL/SDA та CS/MOSI починає протікати через вбудовані кремнієві ESD-діоди на внутрішню шину живлення знеструмленого чипа. Напруга на ньому встановлюється на рівні 1.8–2.2 В, чого недостатньо для стабільної роботи логіки, але достатньо для хаотичного відкриття вихідних транзисторів, які коротять шину на землю.
4. **Електромагнітне розсинхронізування бітового лічильника:** Імпульсна завада від комутації реле або силового ключа інвертора створює хибний сплеск на тактовій лінії. Внутрішній 3-бітний лічильник веденого чипа перескакує на 1 такт уперед. Ведений вважає, що зараз передається 8-й біт даних, тоді як ведучий уже генерує 9-й такт підтвердження (ACK). Ведений очікує наступного клока, ведучий чекає завершення транзакції — система потрапляє у стан взаємного очікування *(Deadlock)*.
5. **Втрата сигналу вибору кристала SPI (Chip Select):** Якщо провід CS відірвався або перебуває у плаваючому стані high-Z, ведений SPI-чип відключає свій вихід MISO. Ведучий передає байти в порожнечу, отримуючи у відповідь `0xFF` або `0x00`, проте якщо протокол вимагає очікування службового байта готовності (наприклад, `0xAA` від Flash-пам'яті чи статусного біта `BUSY=0`), цикл `while (spi_read() != READY)` стає нескінченним.

Перше залізне правило надійної прошивки: **Жоден цикл очікування апаратного регістра, стану лінії чи прапорця завершення передачі не має права існувати без жорсткого та детермінованого обмеження за часом (Deadline Timeout).**

---

## Реалізація та розрахунок таймаутів: Апаратні таймери проти лічильників

Найпоширеніша помилка при спробі захистити цикл від зависання — використання простого програмного декременту інкрементного лічильника:

:::tabs
```c
/* Ілюзія захисту: програмний лічильник ітерацій */
uint32_t timeout_counter = 100000;
while (!(I2C1->SR1 & I2C_SR1_RXNE)) {
    if (--timeout_counter == 0) {
        return DRIVER_ERR_BUS_TIMEOUT;
    }
}
```
```cpp
#include <cstdint>

// Ілюзія захисту у C++: програмний декремент лічильника ітерацій
uint32_t timeout_counter = 100'000;
while ((I2C1->SR1 & (1UL << 6)) == 0) {
    if (--timeout_counter == 0) {
        return DriverStatus::BusTimeout;
    }
}
```
:::

Цей код створює фальшиве відчуття надійності, але є міною сповільненої дії для реального виробу.

### Чому програмні лічильники ітерацій неприпустимі

Тривалість виконання однієї ітерації такого циклу залежить від безлічі неконтрольованих факторів середовища виконання:

1. **Рівень оптимізації компілятора (`-O0`, `-O2`, `-Os`, `-O3`):** За прапорця `-O0` кожна ітерація транслюється у вичитку змінної зі стека в регістр ядра, декремент, запис назад у стек і умовний перехід (близько 12–16 тактів CPU). За прапорця `-O3` лічильник розміщується виключно в регістрі ядра `r3`, а компілятор розгортає цикл, скорочуючи час ітерації до 2 тактів. Один і той самий ліміт у `100000` ітерацій дасть затримку 9.5 мс у Debug-збірці та лише 1.1 мс у Release-збірці. Якщо за 1.1 мс чип просто не встиг відповісти за штатною діаграмою, Release-версія впаде з помилкою таймауту там, де Debug-версія працювала ідеально.
2. **Зміна частоти тактування ядра (Clock Scaling):** Якщо для енергозбереження частоту ядра мікроконтролера динамічно знижують зі 168 МГц до 16 МГц, час програмного таймауту автоматично розтягується в 10.5 раза.
3. **Стани очікування Flash-пам'яті (Flash Wait States / Latency):** Виконання коду з Flash-пам'яті на високих частотах вимагає від 3 до 7 тактів очікування шини пам'яті. Робота кешу інструкцій (ART Accelerator або I-Cache) робить час виконання циклу залежним від того, чи потрапило тіло циклу на границю кеш-лінії.
4. **Витіснення перериваннями (Interrupt Preemption):** Якщо під час опитування виникають часті високопріоритетні переривання від АЦП або радіотракту, процесор витрачає час на їхню обробку. Реальний фізичний час спливає, але лічильник ітерацій не зменшується, оскільки опитувальний потік витіснений. В результаті таймаут не спрацьовує тоді, коли шина реально зависла.

![Порівняння механізмів вимірювання часу для таймаутів](/root/course/embedded/taimaut-povtor-i-vidmova-prystroiu/img/timeout-mechanisms-comparison.svg)
*Аналіз точності та надійності трьох підходів до формування таймаутів: програмні цикли, системний таймер SysTick та апаратний лічильник циклів DWT.*

### Детерміновані джерела часу: DWT->CYCCNT, SysTick та апаратні таймери

Для забезпечення надійного часового обмеження драйвер повинен спиратися на апаратні джерела відліку фізичного часу, незалежні від коду та компілятора.

#### 1. Апаратний лічильник циклів DWT->CYCCNT (ARM Cortex-M3/M4/M7/M33)

Модуль DWT *(англ. Data Watchpoint and Trace)* містить 32-бітний регістр `CYCCNT`, який інкрементується на кожному такті системного ядра процесора. Це ідеальний інструмент для мікросекундних та субмілісекундних затримок, оскільки читання регістра займає рівно 1 такт CPU без звернення до шин периферії.

Роздільна здатність одного такту на частоті ядра `f_CPU = 168 МГц`:

```
t_tick  =  1 ÷ 168000000 Гц  ≈  5.952 нс
```

Переповнення 32-бітного регістра `2^32 = 4294967296` тактів настає через:

```
t_overflow  =  4294967296 ÷ 168000000 Гц  ≈  25.56 секунди
```

Завдяки правилам беззнакової арифметики за модулем `2^32` різниця `(uint32_t)(now - start)` завжди дає точну кількість пройдених тактів навіть тоді, коли лічильник перейшов через нуль *(Rollover)*:

```
now = 0x00000010,  start = 0xFFFFFFF0
Δt  =  (uint32_t)(0x00000010 - 0xFFFFFFF0)  =  0x00000020 (32 такти)
```

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>

/* Структури та маски Cortex-M DWT/CoreDebug */
#define DWT_CTRL_CYCCNTENA_BIT (1UL << 0)
#define COREDEBUG_DEMCR_TRCENA_BIT (1UL << 24)

/* Ініціалізація апаратного лічильника тактів DWT Cortex-M */
void dwt_timer_init(void) {
    /* Дозволяємо модуль трасування в CoreDebug */
    CoreDebug->DEMCR |= COREDEBUG_DEMCR_TRCENA_BIT;
    /* Скидаємо поточне значення лічильника */
    DWT->CYCCNT = 0;
    /* Вмикаємо підрахунок тактів ядра */
    DWT->CTRL |= DWT_CTRL_CYCCNTENA_BIT;
}

/* Структура контролю дедлайну в мікросекундах */
typedef struct {
    uint32_t start_cycles;
    uint32_t timeout_cycles;
} timeout_dwt_t;

void timeout_dwt_start(timeout_dwt_t *t, uint32_t timeout_us, uint32_t cpu_freq_hz) {
    t->start_cycles = DWT->CYCCNT;
    /* Кількість тактів ядра на вказаний інтервал мікросекунд */
    t->timeout_cycles = timeout_us * (cpu_freq_hz / 1000000UL);
}

bool timeout_dwt_expired(const timeout_dwt_t *t) {
    /* Беззнакова різниця автоматично коректна при переході через 0xFFFFFFFF */
    uint32_t elapsed = DWT->CYCCNT - t->start_cycles;
    return elapsed >= t->timeout_cycles;
}
```
```cpp
#include <cstdint>

// Інкапсуляція апаратного дедлайну DWT у C++
class DwtTimeout {
public:
    static void init() noexcept {
        constexpr uint32_t TRCENA = (1UL << 24);
        constexpr uint32_t CYCCNTENA = (1UL << 0);
        CoreDebug->DEMCR |= TRCENA;
        DWT->CYCCNT = 0;
        DWT->CTRL |= CYCCNTENA;
    }

    constexpr DwtTimeout(uint32_t timeout_us, uint32_t cpu_freq_hz) noexcept
        : start_cycles_(DWT->CYCCNT),
          timeout_cycles_(timeout_us * (cpu_freq_hz / 1'000'000UL)) {}

    [[nodiscard]] bool expired() const noexcept {
        const uint32_t elapsed = DWT->CYCCNT - start_cycles_;
        return elapsed >= timeout_cycles_;
    }

private:
    uint32_t start_cycles_{0};
    uint32_t timeout_cycles_{0};
};
```
:::

#### 2. Системний таймер SysTick та RTOS Tick Counter

Для мілісекундних таймаутів (перетворення АЦП, стирання Flash-пам'яті, очікування стабілізації кварцового резонатора) використовують лічильник мілісекунд системного таймера `SysTick` або лічильник тіків операційної системи реального часу (FreeRTOS `xTaskGetTickCount()`).

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>

/* Отримання глобального монотонного часу системи у мілісекундах */
extern uint32_t platform_get_millis(void);

typedef struct {
    uint32_t start_ms;
    uint32_t timeout_ms;
} timeout_ms_t;

void timeout_ms_start(timeout_ms_t *t, uint32_t timeout_ms) {
    t->start_ms = platform_get_millis();
    t->timeout_ms = timeout_ms;
}

bool timeout_ms_expired(const timeout_ms_t *t) {
    uint32_t elapsed = platform_get_millis() - t->start_ms;
    return elapsed >= t->timeout_ms;
}
```
```cpp
#include <cstdint>
#include <chrono>

extern uint32_t platform_get_millis() noexcept;

class MillisTimeout {
public:
    explicit constexpr MillisTimeout(std::chrono::milliseconds timeout) noexcept
        : start_ms_(platform_get_millis()),
          timeout_ms_(static_cast<uint32_t>(timeout.count())) {}

    [[nodiscard]] bool expired() const noexcept {
        const uint32_t elapsed = platform_get_millis() - start_ms_;
        return elapsed >= timeout_ms_;
    }

private:
    uint32_t start_ms_{0};
    uint32_t timeout_ms_{0};
};
```
:::

### Розрахунок бюджету таймауту (Timeout Budgeting)

Таймаут не можна обирати навмання. Занадто малий таймаут викличе помилкові спрацьовування під час штатних затримок веденого чипа (наприклад, при підвищенні температури), а занадто великий — заморозить процесор і призведе до зриву дедлайнів керування виконавчими механізмами.

Інженерна формула розрахунку таймауту транзакції:

```
t_timeout  =  t_tx_nominal + t_slave_process_max + t_stretch_max + t_safety_margin
```

Розрахуємо таймаут для пакетного зчитування 6 байтів вектора прискорення (X, Y, Z) з IMU-акселерометра шиною I2C Fast Mode (400 кГц):

```
Крок 1: Обсяг транзакції на фізичному рівні
N_bits  =  (1 байт адреси + 1 байт регістра + 1 байт рестарту + 6 байтів даних) · 9 бітів
        =  9 байтів · 9 бітів  =  81 біт

Крок 2: Номінальний час передачі бітів
t_tx_nominal  =  81 ÷ 400000 Гц  =  202.5 мкс

Крок 3: Максимальний час внутрішнього АЦП-перетворення датчика
t_slave_process_max  =  50.0 мкс

Крок 4: Максимально допустиме розтягування такту датчиком за даташитом
t_stretch_max  =  100.0 мкс

Крок 5: Інженерний запас (Safety Margin 100% на переривання ядра та дрейф RC-генератора датчика)
t_safety_margin  =  t_tx_nominal + t_slave_process_max  =  252.5 мкс

Крок 6: Підсумковий бюджет
t_timeout  =  202.5 + 50.0 + 100.0 + 252.5  =  605.0 мкс  ≈  0.8–1.0 мс
```

Встановлення таймауту в 1.0 мс гарантує безпомилкову передачу за будь-яких теплових режимів датчика та забезпечує детерміноване повернення керування максимум за 1 мілісекунду у випадку обриву шлейфу.

---

## Класифікація помилок комунікації: Транзиєнтні, фатальні та шинні відмови

Не кожна помилка вимагає перезавантаження системи, і не на кожну помилку слід відповідати повторною спробою. Сліпий ретрай фатальної помилки блокує шину і спалює процесорний час, тоді як миттєва капітуляція перед одиничною завадою знижує надійність виробу до нуля.

![Класифікація помилок комунікації та алгоритм реакції](/root/course/embedded/taimaut-povtor-i-vidmova-prystroiu/img/error-classification-taxonomy.svg)
*Дерево класифікації помилок комунікації у вбудованому драйвері: розподіл на транзиєнтні, фатальні та шинні збої з відповідними маршрутами відновлення.*

### Таксономія помилок драйвера

Помилки поділяються на три принципові класи:

| Клас помилки | Фізична природа збою | Типові симптоми в регістрах | Дія драйвера |
|---|---|---|---|
| **Транзиєнтна (Transient / Soft)** | Короткочасна завада, імпульсний шум, зайнятість чипа | NACK на фазі адреси/даних, незбіг контрольної суми CRC, таймаут через чергу | Затримка (Backoff) та повторна спроба (Retry ≤ 3 рази) |
| **Фатальна (Permanent / Hard)** | Обрив дроту, знеструмлення, вихід чипа з ладу, хибна конфігурація | Стійкий NACK, незбіг `WHO_AM_I` (`0x00`/`0xFF`), неприпустимі параметри виклику | Негайне скасування ретраїв, звіт про відмову, перехід у Failsafe |
| **Шинна відмова (Bus-Level Lockup)** | Зависання кінцевого автомата чипа, затиснута лінія SDA | Прапорець `BUSY=1`, лінія SDA=0 при SCL=1, неможливість сформувати START | Апаратний скид шини: 9 тактів SCL (Bus Clear), реініціалізація периферії МК |

### Матриця рішень для статусних кодів

:::tabs
```c
typedef enum {
    DRIVER_OK = 0,
    DRIVER_ERR_PARAM,          /* Некоректний аргумент (NULL, вихід за межі діапазону) */
    DRIVER_ERR_NACK_ADDR,      /* Чип не відповів на власну адресу на шині */
    DRIVER_ERR_NACK_DATA,      /* Чип відхилив байт даних/регістра */
    DRIVER_ERR_CRC_MISMATCH,   /* Помилка контрольної суми пакета */
    DRIVER_ERR_BUS_TIMEOUT,    /* Апаратний таймаут очікування лінії/прапорця */
    DRIVER_ERR_BUS_STUCK,      /* Лінія SDA або SCL апаратно затиснута в нуль */
    DRIVER_ERR_WRONG_DEVICE_ID /* Зчитано невірний ID чипа (WHO_AM_I) */
} driver_status_t;

typedef enum {
    ACTION_NONE = 0,
    ACTION_RETRY_IMMEDIATE,    /* Повторити негайно (при поодинокому CRC) */
    ACTION_RETRY_WITH_BACKOFF, /* Повторити після часової паузи */
    ACTION_BUS_RECOVER,        /* Необхідна процедура очищення шини 9 імпульсами SCL */
    ACTION_CIRCUIT_BREAKER_HIT /* Зафіксувати фатальну відмову, заблокувати запити */
} error_action_t;

error_action_t classify_driver_error(driver_status_t status) {
    switch (status) {
        case DRIVER_OK:
            return ACTION_NONE;

        case DRIVER_ERR_CRC_MISMATCH:
        case DRIVER_ERR_NACK_DATA:
            /* Транзиєнтний збій: повторюємо через Backoff */
            return ACTION_RETRY_WITH_BACKOFF;

        case DRIVER_ERR_NACK_ADDR:
        case DRIVER_ERR_BUS_TIMEOUT:
            /* Можливе зависання шини або транзиєнтний скид живлення */
            return ACTION_RETRY_WITH_BACKOFF;

        case DRIVER_ERR_BUS_STUCK:
            /* Апаратне залипання лінії: потрібен спец-протокол відновлення */
            return ACTION_BUS_RECOVER;

        case DRIVER_ERR_PARAM:
        case DRIVER_ERR_WRONG_DEVICE_ID:
        default:
            /* Фатальні помилки: ретраї не допоможуть, фіксуємо відмову */
            return ACTION_CIRCUIT_BREAKER_HIT;
    }
}
```
```cpp
#include <cstdint>

enum class DriverStatus : uint8_t {
    Ok = 0,
    InvalidParam,
    NackAddress,
    NackData,
    CrcMismatch,
    BusTimeout,
    BusStuck,
    WrongDeviceId
};

enum class ErrorAction : uint8_t {
    None = 0,
    RetryImmediate,
    RetryWithBackoff,
    BusRecover,
    CircuitBreakerHit
};

[[nodiscard]] constexpr ErrorAction classify_error(DriverStatus status) noexcept {
    switch (status) {
        case DriverStatus::Ok:
            return ErrorAction::None;

        case DriverStatus::CrcMismatch:
        case DriverStatus::NackData:
        case DriverStatus::NackAddress:
        case DriverStatus::BusTimeout:
            return ErrorAction::RetryWithBackoff;

        case DriverStatus::BusStuck:
            return ErrorAction::BusRecover;

        case DriverStatus::InvalidParam:
        case DriverStatus::WrongDeviceId:
        default:
            return ErrorAction::CircuitBreakerHit;
    }
}
```
:::

---

## Апаратне скидання шини I2C: Протокол 9 імпульсів SCL (Bus Clear)

Найпідступніший стан на шині I2C виникає, коли ведучий мікроконтролер перезавантажується або скидає транзакцію за таймаутом у момент, коли ведений чип передавав логічний нуль. Ведений утримує лінію SDA притягнутою до землі, очікуючи чергового спадного фронту на SCL для передачі наступного біта. Оскільки лінія SDA притиснута до нуля, ведучий не здатний згенерувати обов'язкову умову `START` (перепад SDA з 1 в 0 при SCL=1) і фіксує стан шини як постійно зайнятий (`BUSY`).

Програмне перезавантаження периферійного модуля I2C у мікроконтролері (`I2C_CR1_SWRST`) не допомагає, оскільки проблема знаходиться зовні — у внутрішньому скінченному автоматі веденого чипа.

Для розблокування шини реалізують стандартну процедуру апаратного очищення шини *(англ. I2C Bus Clear Sequence)*:

1. Вимикають периферійний модуль I2C мікроконтролера.
2. Переналаштовують виводи SCL та SDA як звичайні виходи загального призначення GPIO в режимі відкритого стоку *(Open-Drain)* із зовнішніми підтяжками.
3. Генерують до 9 послідовних тактових імпульсів на лінії SCL (перемиканням GPIO з частотою ~50–100 кГц).
4. На кожному такті перевіряють стан входу лінії SDA: щойно ведений чип дорахує 8 бітів і відпустить лінію (SDA підніметься до логічної 1 під дією резистора), тактування можна припинити.
5. Формують умову `STOP`: примусово переводять SDA в 0 при низькому SCL, піднімають SCL до 1, а потім відпускають SDA в 1.
6. Повертають ніжки мікроконтролера в режим альтернативної функції I2C та реініціалізують апаратний блок.

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>

/* Абстракція платформних викликів керування ніжками GPIO */
extern void gpio_set_mode_gpio_opendrain(void);
extern void gpio_set_mode_i2c_alternate(void);
extern void gpio_set_scl(bool level);
extern bool gpio_read_sda(void);
extern void platform_delay_us(uint32_t us);

/* Процедура апаратного розблокування завислої шини I2C */
bool i2c_hardware_bus_recover(void) {
    /* 1. Переводимо лінії в режим прямого керування GPIO Open-Drain */
    gpio_set_mode_gpio_opendrain();
    platform_delay_us(10);

    /* 2. Якщо SDA вже висока — шина не затиснута веденим */
    if (gpio_read_sda()) {
        gpio_set_mode_i2c_alternate();
        return true;
    }

    /* 3. Генеруємо до 9 тактових імпульсів на SCL для виштовхування біта */
    bool recovered = false;
    for (uint8_t i = 0; i < 9; i++) {
        gpio_set_scl(false);
        platform_delay_us(5);
        gpio_set_scl(true);
        platform_delay_us(5);

        if (gpio_read_sda()) {
            recovered = true;
            break;
        }
    }

    /* 4. Формуємо примусову умову STOP для скидання автоматів ведених чипів */
    gpio_set_scl(false);
    platform_delay_us(5);
    /* SDA примусово притягуємо до нуля */
    /* SCL піднімаємо до 1 */
    gpio_set_scl(true);
    platform_delay_us(5);
    /* Відпускаємо SDA у високий рівень при високому SCL -> умова STOP */
    platform_delay_us(5);

    /* 5. Повертаємо ніжки під контроль апаратного модуля I2C */
    gpio_set_mode_i2c_alternate();
    return recovered;
}
```
```cpp
#include <cstdint>

class I2cBusRecovery {
public:
    struct GpioInterface {
        void (*set_opendrain_mode)() noexcept;
        void (*set_alternate_mode)() noexcept;
        void (*set_scl)(bool level) noexcept;
        bool (*read_sda)() noexcept;
        void (*delay_us)(uint32_t us) noexcept;
    };

    explicit constexpr I2cBusRecovery(const GpioInterface& gpio) noexcept
        : gpio_(gpio) {}

    [[nodiscard]] bool recover() const noexcept {
        gpio_.set_opendrain_mode();
        gpio_.delay_us(10);

        if (gpio_.read_sda()) {
            gpio_.set_alternate_mode();
            return true;
        }

        bool recovered = false;
        for (uint8_t i = 0; i < 9; ++i) {
            gpio_.set_scl(false);
            gpio_.delay_us(5);
            gpio_.set_scl(true);
            gpio_.delay_us(5);

            if (gpio_.read_sda()) {
                recovered = true;
                break;
            }
        }

        // Формування умови STOP
        gpio_.set_scl(false);
        gpio_.delay_us(5);
        gpio_.set_scl(true);
        gpio_.delay_us(5);

        gpio_.set_alternate_mode();
        return recovered;
    }

private:
    GpioInterface gpio_;
};
```
:::

---

## Стратегії повторних спроб: Фіксовані паузи, експоненційний відкат та джитер

Якщо драйвер виявив транзиєнтну помилку (наприклад, NACK через зайнятість внутрішнього АЦП датчика), негайний повтор транзакції у тому ж мікросекундному вікні зазвичай знову призведе до помилки.

Чому миттєвий повтор без затримки шкідливий:
1. **Перехідні процеси:** Якщо збій стався через просідання живлення або внутрішнє перезавантаження датчика, його аналоговій частині потрібен час на заряд ємностей підкладки (100–500 мкс).
2. **Забивання шини:** Безперервне спамування запитами не дозволяє іншим периферійним пристроям на спільній шині I2C/SPI отримати доступ до інтерфейсу.
3. **Енергоспоживання:** Швидкісний ретрай тримає ядро мікроконтролера на 100% завантаженні у гарячому циклі опитування.

### Експоненційний відкат (Exponential Backoff)

Алгоритм експоненційного відкату збільшує тривалість паузи між кожною наступною невдалою спробою вдвічі:

```
t_backoff(k)  =  min(t_base · 2^(k - 1),  t_max)
```

де `k` — номер поточної спроби (1, 2, 3...), `t_base` — базова затримка (наприклад, 1 мс), `t_max` — стеля паузи (наприклад, 16 мс).

Послідовність пауз:

```
Спроба 1:  t_backoff(1)  =  1 · 2⁰   =   1 мс
Спроба 2:  t_backoff(2)  =  1 · 2¹   =   2 мс
Спроба 3:  t_backoff(3)  =  1 · 2²   =   4 мс
Спроба 4:  t_backoff(4)  =  1 · 2³   =   8 мс
Спроба 5:  t_backoff(5)  =  1 · 2⁴   =  16 мс (t_max)
```

Такий підхід дає зовнішньому чипу експоненційно більший час на самовідновлення без зависання шини на довгий фіксований час на першій же спробі.

### Джитер та проблема синхронізації збоїв (Thundering Herd)

На мультидроп-шинах (RS-485, CAN, Modbus або багатомайстрові системи I2C) виникає ефект «громового стада» *(Thundering Herd)*: коли через спільний стрибок живлення всі вузли одночасно фіксують збій і починають повторні спроби через однаковий детермінований інтервал `t_backoff`. Їхні пакети знову стикаються в колізії, шина знову падає, і всі вузли знову синхронно чекають наступного ступеня відкату.

Для запобігання цьому явищу до експоненційного інтервалу додають псевдовипадковий шум — **джитер (Jitter)**.

Алгоритм повного джитеру *(Full Jitter)* обирає випадковий інтервал у межах від 0 до стелі поточного ступеня:

```
t_sleep  =  random(0, t_backoff(k))
```

Для вбудованих систем без апаратного генератора випадкових чисел (RNG) використовують швидкий лінійний конгруентний генератор (LCG), ініціалізований значенням таймера `SysTick` або `DWT->CYCCNT`:

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>

/* Простий вбудований генератор псевдовипадкових чисел (LCG) */
static uint32_t fast_rand(uint32_t *seed) {
    *seed = (*seed * 1664525UL + 1013904223UL);
    return *seed;
}

typedef struct {
    uint8_t  max_attempts;    /* Максимальна кількість спроб (зазвичай 3–5) */
    uint32_t base_delay_us;   /* Базова затримка у мікросекундах */
    uint32_t max_delay_us;    /* Максимальна затримка */
    uint32_t rand_seed;       /* Стан генератора випадкових чисел */
} retry_policy_t;

/* Обчислення паузи для поточної спроби k (від 1 до max_attempts) */
uint32_t retry_calculate_delay_us(retry_policy_t *p, uint8_t attempt) {
    if (attempt == 0) return 0;
    
    /* 1 << (attempt - 1) реалізує 2^(k-1) */
    uint32_t shift = (attempt > 10) ? 10 : (attempt - 1);
    uint32_t exp_delay = p->base_delay_us * (1UL << shift);
    
    if (exp_delay > p->max_delay_us) {
        exp_delay = p->max_delay_us;
    }
    
    /* Додаємо джитер: випадкове значення в інтервалі [0.5 * exp_delay ... exp_delay] */
    uint32_t half = exp_delay / 2;
    uint32_t jitter = fast_rand(&p->rand_seed) % (half + 1);
    
    return half + jitter;
}
```
```cpp
#include <cstdint>
#include <algorithm>

class RetryPolicy {
public:
    constexpr RetryPolicy(uint8_t max_attempts, uint32_t base_delay_us, 
                          uint32_t max_delay_us, uint32_t initial_seed) noexcept
        : max_attempts_(max_attempts),
          base_delay_us_(base_delay_us),
          max_delay_us_(max_delay_us),
          rand_seed_(initial_seed) {}

    [[nodiscard]] uint32_t calculate_delay_us(uint8_t attempt) noexcept {
        if (attempt == 0) return 0;

        const uint32_t shift = (attempt > 10) ? 10 : (attempt - 1);
        uint32_t exp_delay = base_delay_us_ * (1UL << shift);
        exp_delay = std::min(exp_delay, max_delay_us_);

        const uint32_t half = exp_delay / 2;
        const uint32_t jitter = next_random() % (half + 1);
        return half + jitter;
    }

    [[nodiscard]] constexpr uint8_t max_attempts() const noexcept {
        return max_attempts_;
    }

private:
    uint32_t next_random() noexcept {
        rand_seed_ = (rand_seed_ * 1664525UL + 1013904223UL);
        return rand_seed_;
    }

    uint8_t  max_attempts_{3};
    uint32_t base_delay_us_{1000};
    uint32_t max_delay_us_{16000};
    uint32_t rand_seed_{1234567};
};
```
:::

---

## Автомат здоров'я пристрою: Патерн Circuit Breaker та деградація (Failsafe)

Якщо датчик остаточно відірвався від шини або згорів, ретраї з таймаутами при кожному виклику стають отрутою для прошивки. Припустимо, цикл оновлення телеметрії викликається з частотою 100 Гц (кожні 10 мс). Якщо кожне опитування мертвого датчика робить 3 спроби з таймаутом по 1 мс та паузами, процесор витрачатиме понад 5–8 мс на кожній ітерації на марні очікування. Залишкового часу не вистачить на виконання інших задач (математики фільтра Калмана чи розрахунку ПІД-регулятора), і вся система втратить керування.

Для захисту процесора від спаму невдалих викликів застосовують адаптований для вбудованих систем патерн **Запобіжник (Circuit Breaker)**.

![Автомат станів Circuit Breaker](/root/course/embedded/taimaut-povtor-i-vidmova-prystroiu/img/circuit-breaker-fsm.svg)
*Кінцевий автомат моніторингу працездатності периферійного пристрою: стани CLOSED (штатна робота), OPEN (ізоляція та миттєвий Fast-Fail) і HALF-OPEN (пробна перевірка).*

### Стан автомату здоров'я пристрою

Автомат має три дискретні стани:

1. **CLOSED (Замкнений — Штатний робочий стан):**
   - Усі запити до датчика виконуються безпосередньо через шину.
   - Лічильник послідовних помилок `consecutive_failures` інкрементується при кожному збої.
   - У разі успішної транзакції лічильник миттєво обнуляється: `consecutive_failures = 0`.
   - Якщо `consecutive_failures >= FAILURE_THRESHOLD` (наприклад, 5 поспіль невдалих транзакцій), автомат «розмикає контур» і переходить у стан `OPEN`.

2. **OPEN (Розірваний — Ізоляція несправності):**
   - Будь-який наступний виклик драйвера **не торкається шини** взагалі. Функція негайно повертає код помилки `ERR_DEVICE_OFFLINE` за 1–2 такти процесора *(Fast-Fail)*.
   - Запускається таймер кулдауну *(Cooldown Timer)* на час `T_cooldown` (наприклад, 5 секунд).
   - Шина та процесор повністю розвантажуються, інші здорові пристрої на шині отримують безперешкодний доступ.
   - Коли `T_cooldown` спливає, автомат переходить у стан `HALF-OPEN`.

3. **HALF-OPEN (Напіврозірваний — Пробний стан):**
   - Автомат дозволяє виконати рівно одну тестову транзакцію (наприклад, зчитування регістра ідентифікатора `WHO_AM_I`).
   - Якщо пробна транзакція завершилася успішно — датчик відновив працездатність! Автомат скидає лічильники та повертається у стан `CLOSED`.
   - Якщо пробна транзакція знову зазнала краху — чип досі мертвий. Автомат повертається у стан `OPEN` і подвоює час кулдауну (експоненційний кулдаун).

### Повна реалізація Circuit Breaker для вбудованого драйвера

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>

extern uint32_t platform_get_millis(void);

typedef enum {
    CB_STATE_CLOSED = 0,    /* Штатна робота */
    CB_STATE_OPEN,          /* Відмова, запити блокуються */
    CB_STATE_HALF_OPEN      /* Пробна перевірка */
} circuit_state_t;

typedef struct {
    circuit_state_t state;
    uint8_t  failure_count;
    uint8_t  failure_threshold;   /* Поріг відмов для розриву (наприклад, 5) */
    uint32_t state_change_time_ms;
    uint32_t cooldown_period_ms;  /* Час ізоляції чипа (наприклад, 5000 мс) */
    uint32_t total_errors_logged; /* Загальний лічильник для діагностики */
} circuit_breaker_t;

void cb_init(circuit_breaker_t *cb, uint8_t threshold, uint32_t cooldown_ms) {
    cb->state = CB_STATE_CLOSED;
    cb->failure_count = 0;
    cb->failure_threshold = threshold;
    cb->state_change_time_ms = 0;
    cb->cooldown_period_ms = cooldown_ms;
    cb->total_errors_logged = 0;
}

/* Перевірка, чи дозволено виконувати фізичну транзакцію */
bool cb_allow_transaction(circuit_breaker_t *cb) {
    uint32_t now = platform_get_millis();

    switch (cb->state) {
        case CB_STATE_CLOSED:
            return true;

        case CB_STATE_OPEN:
            /* Перевіряємо, чи минув час охолодження */
            if ((now - cb->state_change_time_ms) >= cb->cooldown_period_ms) {
                cb->state = CB_STATE_HALF_OPEN;
                return true; /* Дозволяємо одну пробну транзакцію */
            }
            return false; /* Швидка відмова: не навантажуємо шину */

        case CB_STATE_HALF_OPEN:
            /* Пробна транзакція вже в процесі */
            return false;

        default:
            return false;
    }
}

/* Фіксація успішного виконання транзакції */
void cb_report_success(circuit_breaker_t *cb) {
    cb->failure_count = 0;
    if (cb->state != CB_STATE_CLOSED) {
        cb->state = CB_STATE_CLOSED;
        cb->state_change_time_ms = platform_get_millis();
    }
}

/* Фіксація помилки виконання транзакції */
void cb_report_failure(circuit_breaker_t *cb) {
    cb->total_errors_logged++;
    uint32_t now = platform_get_millis();

    if (cb->state == CB_STATE_HALF_OPEN) {
        /* Проба провалилася: миттєво повертаємось в OPEN */
        cb->state = CB_STATE_OPEN;
        cb->state_change_time_ms = now;
        /* Можна подвоїти період очікування: cb->cooldown_period_ms *= 2; */
    } else if (cb->state == CB_STATE_CLOSED) {
        cb->failure_count++;
        if (cb->failure_count >= cb->failure_threshold) {
            cb->state = CB_STATE_OPEN;
            cb->state_change_time_ms = now;
        }
    }
}
```
```cpp
#include <cstdint>
#include <chrono>

extern uint32_t platform_get_millis() noexcept;

class CircuitBreaker {
public:
    enum class State : uint8_t {
        Closed = 0,
        Open,
        HalfOpen
    };

    constexpr CircuitBreaker(uint8_t threshold, std::chrono::milliseconds cooldown) noexcept
        : failure_threshold_(threshold),
          cooldown_period_ms_(static_cast<uint32_t>(cooldown.count())) {}

    [[nodiscard]] bool allow_transaction() noexcept {
        const uint32_t now = platform_get_millis();

        switch (state_) {
            case State::Closed:
                return true;

            case State::Open:
                if ((now - state_change_time_ms_) >= cooldown_period_ms_) {
                    state_ = State::HalfOpen;
                    return true;
                }
                return false;

            case State::HalfOpen:
                return false;

            default:
                return false;
        }
    }

    void report_success() noexcept {
        failure_count_ = 0;
        if (state_ != State::Closed) {
            state_ = State::Closed;
            state_change_time_ms_ = platform_get_millis();
        }
    }

    void report_failure() noexcept {
        ++total_errors_;
        const uint32_t now = platform_get_millis();

        if (state_ == State::HalfOpen) {
            state_ = State::Open;
            state_change_time_ms_ = now;
        } else if (state_ == State::Closed) {
            if (++failure_count_ >= failure_threshold_) {
                state_ = State::Open;
                state_change_time_ms_ = now;
            }
        }
    }

    [[nodiscard]] constexpr State state() const noexcept { return state_; }
    [[nodiscard]] constexpr uint32_t total_errors() const noexcept { return total_errors_; }

private:
    State    state_{State::Closed};
    uint8_t  failure_count_{0};
    uint8_t  failure_threshold_{5};
    uint32_t state_change_time_ms_{0};
    uint32_t cooldown_period_ms_{5000};
    uint32_t total_errors_{0};
};
```
:::

---

## Пастки DMA, RTOS-м'ютексів та взаємодія зі сторожовим таймером

При побудові промислових драйверів таймаути виходять далеко за межі простих опитувань бітів регістра. У складних прошивках взаємодія з периферією включає прямий доступ до пам'яті (DMA), розділення шини між задачами RTOS та координацію зі сторожовим таймером (Watchdog).

### 1. Таймаути транзакцій прямого доступу до пам'яті (DMA)

При використанні DMA процесор не бере участі в передачі байтів: налаштовується дескриптор потоку, вмикається канал DMA, і задача переходить у стан очікування семафора або прапорця завершення передачі `Transfer Complete (TC)`.

Якщо шина зависла або ведений чип обірвав передачу посеред пакета, лічильник кількості даних DMA (`NDTR`) зупиняється на ненульовому значенні, переривання `TC` не генерується ніколи, і потік RTOS залишається заблокованим назавжди.

Для захисту DMA-передач використовують зовнішній дедлайн:
- Потік очікує семафор завершення DMA з жорстким таймаутом `xSemaphoreTake(dma_sem, timeout_ticks)`.
- Якщо таймаут сплив раніше, ніж прийшло переривання `TC`, драйвер зобов'язаний виконати примусове аварійне відключення DMA:
  1. Вимкнути потік DMA (`DMA_Stream->CR &= ~DMA_SxCR_EN`).
  2. Зачекати скидання біта `EN` в нуль за мікросекундним таймаутом DWT (DMA потребує кількох тактів на зупинку внутрішнього конвеєра).
  3. Очистити всі апаратні прапорці помилок (`TEIF`, `FEIF`, `DMEIF`).
  4. Скинути периферійний блок (SPI/I2C) та повідомити верхній рівень про збій.

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>

/* Безпечне аварійне скасування завислої транзакції DMA */
bool dma_abort_transfer(DMA_Stream_TypeDef *dma_stream, timeout_dwt_t *guard) {
    /* Примусово скидаємо біт увімкнення потоку DMA */
    dma_stream->CR &= ~DMA_SxCR_EN;

    /* Чекаємо апаратного підтвердження зупинки конвеєра */
    while (dma_stream->CR & DMA_SxCR_EN) {
        if (timeout_dwt_expired(guard)) {
            /* Фатальний збій шинної матриці контролера DMA */
            return false;
        }
    }

    /* Очищаємо прапорці переривань потоку */
    return true;
}
```
```cpp
#include <cstdint>

struct DmaStreamRegisters {
    volatile uint32_t CR;
    volatile uint32_t NDTR;
    volatile uint32_t PAR;
    volatile uint32_t M0AR;
};

class DmaAbortGuard {
public:
    static bool abort(DmaStreamRegisters* stream, const DwtTimeout& timeout) noexcept {
        constexpr uint32_t STREAM_EN = (1UL << 0);
        stream->CR &= ~STREAM_EN;

        while ((stream->CR & STREAM_EN) != 0) {
            if (timeout.expired()) {
                return false;
            }
        }
        return true;
    }
};
```
:::

### 2. Запобігання інверсії пріоритетів та блокуванню шини в RTOS

На спільній шині I2C, до якої підключені кілька датчиків (наприклад, низькопріоритетний датчик вологості та критичний IMU системи стабілізації), доступ до фізичного драйвера захищається м'ютексом.

Якщо низькопріоритетна задача захоплює м'ютекс шини і застрягає в нескінченному опитуванні завислого датчика, високопріоритетна задача польотного контролера не зможе отримати доступ до IMU навіть через механізм успадкування пріоритетів *(Priority Inheritance)*.

Правило синхронізації RTOS:
- Захоплення м'ютексу шини **завжди** виконується з таймаутом: `xSemaphoreTake(bus_mutex, pdMS_TO_TICKS(10))`.
- Усі операції всередині критичної секції шини повинні мати сумарний таймаут, менший за максимальний квант затримки високопріоритетної задачі.

### 3. Дисципліна скидання сторожового таймера (Watchdog)

Сторожовий таймер *(Independent Watchdog — IWDG)* призначений для виявлення повної втрати працездатності програмного забезпечення.

Найгрубіша помилка архітектури — скидати сторожовий таймер (`IWDG->KR = 0xAAAA` або `HAL_IWDG_Refresh()`) всередині циклу очікування шини або всередині функції повторних спроб:

:::tabs
```c
/* ГРУБА ПОМИЛКА: Скидання WDT всередині циклу маскує зависання */
while (!(I2C1->SR1 & I2C_SR1_RXNE)) {
    IWDG->KR = 0xAAAA; /* WDT скидається, процесор висить вічно! */
}
```
```cpp
// Груба помилка у C++: скидання сторожового таймера всередині очікування периферії
while ((I2C1->SR1 & (1UL << 6)) == 0) {
    IWDG->KR = 0xAAAA; // Маскування зависання шини від сторонніх супервізорів
}
```
:::

Такий код унеможливлює апаратне виявлення збою мікроконтролера: периферія зависла, головна програма не виконується, але сторожовий таймер продовжує отримувати підтвердження «життя». 

Скидання апаратного сторожового таймера має право виконувати **виключно головний планувальник завдань** або супервізор системи наприкінці повного циклу верифікації здоров'я всіх підсистем. У багаторівневій архітектурі кожна задача веде власний лічильник виконаних циклів *(Task Heartbeat Counter)*. Якщо задача опитування датчиків застрягла або перевищила допустимий ліміт помилок Circuit Breaker, вона перестає оновлювати свій локальний лічильник. Головний супервізор під час перевірки фіксує зупинку лічильника задачі, блокує апаратне скидання IWDG і дозволяє таймеру безпечно перезавантажити мікроконтролер для повернення в контрольований початковий стан.

---

## Інтегрований виконавець транзакцій: Повний контур стійкості

Об'єднаємо всі рівні захисту — Circuit Breaker, апаратні таймаути, класифікацію помилок, процедуру відновлення шини та експоненційний ретрай — у єдину архітектурну функцію виконання транзакції драйвера:

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>

/* Тип покажчика на низькорівневу фізичну операцію шини */
typedef driver_status_t (*bus_transfer_fn_t)(void *context);

/* Уніфікований стійкий виконавець транзакцій */
driver_status_t resilient_transaction_execute(
    circuit_breaker_t *cb,
    retry_policy_t    *retry_policy,
    bus_transfer_fn_t  transfer_fn,
    void              *context
) {
    /* 1. Фаза перевірки здоров'я: Fast-Fail якщо чип в ізоляції */
    if (!cb_allow_transaction(cb)) {
        return DRIVER_ERR_BUS_TIMEOUT; /* Пристрій офлайн */
    }

    driver_status_t status = DRIVER_OK;
    uint8_t attempt = 0;

    while (attempt < retry_policy->max_attempts) {
        attempt++;

        /* 2. Фізичне виконання транзакції з апаратним таймаутом всередині */
        status = transfer_fn(context);

        /* 3. Успіх: фіксація здоров'я та негайне повернення */
        if (status == DRIVER_OK) {
            cb_report_success(cb);
            return DRIVER_OK;
        }

        /* 4. Аналіз та класифікація збою */
        error_action_t action = classify_driver_error(status);

        if (action == ACTION_CIRCUIT_BREAKER_HIT) {
            /* Фатальна помилка: негайний розрив без ретраїв */
            cb_report_failure(cb);
            return status;
        }

        if (action == ACTION_BUS_RECOVER) {
            /* Залипання шини: апаратне відновлення 9 імпульсами */
            i2c_hardware_bus_recover();
        }

        /* 5. Обчислення експоненційного відкату з джитером */
        if (attempt < retry_policy->max_attempts) {
            uint32_t delay_us = retry_calculate_delay_us(retry_policy, attempt);
            platform_delay_us(delay_us);
        }
    }

    /* Якщо всі спроби вичерпано — інформуємо Circuit Breaker про відмову */
    cb_report_failure(cb);
    return status;
}
```
```cpp
#include <cstdint>
#include <concepts>
#include <chrono>

extern void platform_delay_us(uint32_t us) noexcept;
extern bool i2c_hardware_bus_recover() noexcept;

template <typename TransferFn>
requires requires(TransferFn fn) { { fn() } -> std::same_as<DriverStatus>; }
class ResilientExecutor {
public:
    static DriverStatus execute(
        CircuitBreaker& cb,
        RetryPolicy& retry_policy,
        TransferFn&& transfer_fn
    ) noexcept {
        if (!cb.allow_transaction()) {
            return DriverStatus::BusTimeout;
        }

        DriverStatus status = DriverStatus::Ok;
        const uint8_t max_tries = retry_policy.max_attempts();

        for (uint8_t attempt = 1; attempt <= max_tries; ++attempt) {
            status = transfer_fn();

            if (status == DriverStatus::Ok) {
                cb.report_success();
                return DriverStatus::Ok;
            }

            const ErrorAction action = classify_error(status);

            if (action == ErrorAction::CircuitBreakerHit) {
                cb.report_failure();
                return status;
            }

            if (action == ErrorAction::BusRecover) {
                i2c_hardware_bus_recover();
            }

            if (attempt < max_tries) {
                const uint32_t delay_us = retry_policy.calculate_delay_us(attempt);
                platform_delay_us(delay_us);
            }
        }

        cb.report_failure();
        return status;
    }
};
```
:::

---

## Градуальна деградація та перехід у безпечний режим (Failsafe)

Коли Circuit Breaker фіксує відмову пристрою і переходить у стан `OPEN`, верхній рівень системи (прикладний контролер) повинен виконати детермінований перехід у режим деградації або аварійного захисту *(англ. Failsafe)*.

### Стратегії системної деградації

1. **Датчикова надлишковість (Sensor Redundancy):**
   - Якщо на борту встановлено два однакових акселерометри (Primary IMU та Secondary IMU), відмова першого викликає негайне автоматичне перемикання фільтра орієнтації на джерело даних з другого датчика.
2. **Зниження точності математичної моделі (Degraded Fusion):**
   - У разі відмови барометричного датчика висоти польотний контролер відключає барометричну корекцію у фільтрі Калмана і продовжує оцінку висоти за вертикальним інтегруванням акселерометра та даними супутникової навігації GNSS, збільшуючи діагональні елементи коваріаційної матриці шуму вимірювань `R`.
3. **Безпечна аварійна зупинка (Failsafe Action):**
   - Якщо відмовив критичний датчик, без якого керування фізично неможливе (наприклад, датчик струму інвертора електромобіля або датчик температури акумуляторної батареї):
     1. Виконавчі ШІМ-виходи комутаторів силових ключів негайно блокуються апаратним сигналом `Break / Fault`.
     2. Вмикається аварійна звукова та світлова сигналізація.
     3. Записується діагностичний код відмови в захищену область енергонезалежної пам'яті (Flash/EEPROM Blackbox).
     4. Система переходить у режим очікування технічного обслуговування або виконує керовану аварійну зупинку.

---

## Архітектурний чеклист відмовостійкого драйвера

Кожен професійний вбудований драйвер повинен відповідати семи інженерним правилам надійності:

1. **Жодного нескінченного циклу:** Кожен оператор `while` чи `do-while`, що перевіряє регістр або лінію GPIO, має бути апаратно обмежений дедлайном через DWT або SysTick.
2. **Незалежність від компілятора:** Час таймаутів розраховується у фізичних одиницях (мікросекунди, мілісекунди), а не в кількості ітерацій.
3. **Обов'язкова класифікація помилок:** Перед ухваленням рішення про ретрай драйвер класифікує помилку на транзиєнтну чи фатальну (ніколи не повторювати виклики з невірними вхідними параметрами або помилкою `WHO_AM_I`).
4. **Експоненційний відкат із джитером:** Повторні спроби виконуються з прогресивними паузами для розвантаження шини та запобігання колізіям.
5. **Ізоляція відмов через Circuit Breaker:** Після 3–5 послідовних збоїв драйвер припиняє звернення до мертвого чипа, повертаючи помилку за O(1) та звільняючи шину для інших вузлів.
6. **Апаратна підтримка очищення шини (Bus Recovery):** За наявності зависань I2C драйвер повинен мати функцію генерації 9 імпульсів SCL у режимі GPIO bit-bang для примусового скидання веденого автомата.
7. **Прозорість діагностики:** Кожен збій таймауту і кожне спрацьовування запобіжника збільшують відкриті діагностичні лічильники, доступні системі моніторингу та чорній скриньці.
