# Розробка модуля автоматичного відновлення шини та ескалації скидання

Практична реалізація промислового контролера відновлення послідовних шин (Bus Recovery Controller) вимагає створення компактного, детермінованого та незалежного від операційної системи модуля. Модуль повинен брати на себе повне керування апаратними ресурсами при виникненні будь-яких блокувань інтерфейсів I2C або SPI: від короткочасного глітчу до мертвого зависання лінії SDA чи колапсу живлення веденого чипа.

У цьому проекті розглядається побудова закінченого вбудованого модуля `bus_recovery_controller` для мікроконтролерів сімейства ARM Cortex-M (на прикладі архітектури STM32F4), що реалізує детерміновані таймаути на базі лічильника циклів DWT, процедуру електричного розблокування 9 тактовими імпульсами, апаратну трирівневу ескалацію скидання з контролем паразитного зворотного живлення та кільцевий буфер діагностичної телеметрії.

## Архітектурні вимоги та системні контракти

Проектування драйверів для відповідальних застосувань (авіоніка безпілотних апаратів, промислова автоматика, системи автономного живлення) спирається на жорсткі обмеження стандарту безпеки MISRA C та правила детермінізму систем реального часу. Будь-який виклик функції введення-виведення зобов'язаний гарантувати завершення за фіксований квант часу або повернення коду помилки без блокування решти підсистем.

У типовому вбудованому рішенні апаратний рівень розділяється на три взаємопов'язані площини:
1. **Площина сигналів даних (Data Plane)**: складається з апаратних периферійних модулів (I2C1, SPI2), що виконують передачу байтів через канали прямого доступу до пам'яті (DMA) або за допомогою переривань.
2. **Площина контролю та нагляду (Control Plane)**: містить програмні автомати таймаутів, які перевіряють виконання часових інваріантів транзакцій.
3. **Площина фізичного живлення та комутації (Power & Management Plane)**: включає силові ключі керування лініями живлення сенсорів (MOSFET / Load Switch) та лінії апаратного скидання nRESET.

### Фізичні характеристики шини та часові інтервали на друкованій платі

Під час розведення провідників послідовних шин на друкованій платі кожен сантиметр траси вносить власну розподілену паразитну ємність (приблизно 1..2 пФ на дюйм траси для стандартного склотекстоліту FR-4). Додатково кожен підключений роз'єм, діод захисту від статичної електрики (ESD) та вхідний каскад кожної мікросхеми додають від 5 до 10 пФ паразитної ємності.

У результаті сумарна ємність шини `C_bus` для плати з кількома сенсорами становить від 50 до 200 пФ. При використанні підтягувальних резисторів номіналом 4.7 кОм постійна часу заряду лінії `tau = R * C` досягає:
`tau = 4700 Ом * 100 пФ = 470 нс`.

Час наростання фронту від рівня 0.3 * V_DD до рівня 0.7 * V_DD описується формулою:
`t_r = 0.8473 * R_pull-up * C_bus = 0.8473 * 4700 Ом * 100 пФ = 398 нс`.

Це значення повністю вкладається у вимоги специфікації I2C для стандартного режиму 100 кГц (`t_r <= 1000 нс`), проте створює затримку перемикання, яку програмний драйвер зобов'язаний враховувати під час переведення виводів у режим GPIO Bit-Banging.

Вибір занадто великого номіналу підтягувального резистора (наприклад, 10 кОм або вище) при підвищеній ємності довгих з'єднувальних шлейфів (до 400 пФ) призводить до розмиття переднього фронту імпульсів SCL. Вхідний тригер Шмітта мікроконтролера фіксує перехід із затримкою у кілька мікросекунд, що може спричинити збій часових інтервалів утримання даних `t_HD;DAT`. Навпаки, вибір занадто малого номіналу (наприклад, менше 1 кОм) перевищує максимально допустимий струм занурення вихідного N-MOSFET веденого чипа (3 мА), через що рівень логічного нуля `V_OL` перевищує допустимий поріг 0.4 В, блокуючи розпізнавання сигналу ACK.

### Топологія розведення та демпфування ліній зв'язку

На друкованій платі сигнальні провідники шин I2C та SPI не повинні прокладатися у вигляді зірки (Star Topology) або довгих розгалужених відводів (Stubs). Відводи довжиною понад 3–5 см утворюють неузгоджені чвертьхвильові відрізки лінії, що спричиняють багаторазові відбиття сигналів та паразитно дзвенять на високих частотах (Ringing).

Для запобігання дзвінких викидів напруги послідовно в кожну лінію (біля виводів мікроконтролера) встановлюють демпфуючі резистори `R_series = 22..33 Ом`. У поєднанні з вхідною ємністю виводів ці резистори формують низькочастотний RC-фільтр першого порядку, який згладжує надмірно круті фронти сигналів мікроконтролера, усуваючи електромагнітне випромінювання та хибні спрацьовування вхідних компараторів сусідніх сенсорів.

Крім того, трасування ліній SCL та SDA виконується над суцільним полігоном заземлення (Ground Plane). Забороняється перетинати розриви у земляному шарі, оскільки зворотний струм високої частоти змушений огинати проріз у землі, що різко збільшує паразитну індуктивність сигнального контуру та спричиняє перехресні завади (Cross-talk) між тактовою лінією SCL та лінією даних SDA.

### Апаратні пастки SPI Bus Contention у мультимастерних конфігураціях та відновлення шини

На відміну від інтерфейсу I2C, де лінії SDA та SCL функціонують у режимі відкритого стоку з пасивним резистивним підтягуванням (Open-Drain), стандартна шина SPI використовує симетричні двотактні вихідні каскади (Push-Pull) для ліній тактування SCK, передачі MOSI та виходу веденого MISO. У системах підвищеної надійності з дублюванням обчислювальних вузлів (наприклад, два незалежні мікроконтролери польотного контролера, що мають спільний доступ до резервованого масиву датчиків IMU або мікросхеми Flash-пам'яті) одночасна спроба захоплення шини двома ведучими викликає апаратний конфлікт — **SPI Bus Contention**.

Коли перший ведучий виставляє на лінії SCK або MOSI рівень логічної одиниці (відкритий верхній P-MOSFET плеча Push-Pull), а другий ведучий одночасно намагається утримувати лінію в логічному нулі (відкритий нижній N-MOSFET), виникає пряме коротке замикання між шиною живлення `V_DD` та землею `GND` через кристали мікроконтролерів. Наскрізний струм колізії обмежується лише внутрішнім опором відкритих каналів транзисторів (`R_ds_on ≈ 20..50 Ом`):
`I_short = V_DD / (R_ds_on_P + R_ds_on_N) = 3.3 В / (25 Ом + 25 Ом) = 66 мА`.

Цей струм у кілька разів перевищує гранично допустимий абсолютний струм виводу GPIO (для STM32 `I_IO_max = 25 мА`), що призводить до локального термічного перегріву вихідного каскаду, просідання напруги живлення ядра (Ground Bounce / V_DD Sag) та створює пряму загрозу тиристорного замикання (CMOS Latch-up).

Для апаратного захисту в мікроконтролерах STM32 реалізовано механізм фіксації помилки вибору режиму — **Mode Fault (MODF)**. Коли модуль SPI сконфігуровано в режимі ведучого з апаратним контролем виводу NSS (`SSM=0` та `SSOE=0` у регістрах `SPI_CR1` та `SPI_CR2`), переведення лінії NSS у низький рівень зовнішнім ведучим миттєво активує захисний автомат:
1. Апаратний блок SPI негайно скидає біт `SPE` (SPI Enable) у регістрі `SPI_CR1`, примусово вимикаючи периферійний модуль.
2. Вихідні буфери SCK та MOSI автоматично перемикаються у стан високого імпедансу (Hi-Z), розриваючи струмову петлю короткого замикання за кілька наносекунд.
3. Очищається біт ведучого режиму `MSTR` (контролер переходить у режим веденого), і встановлюється прапорець апаратної помилки `SPI_SR_MODF`.

Головна програмна пастка полягає в тому, що наївний драйвер, який не аналізує статус `SPI_SR_MODF` і циклічно очікує підняття прапорців `SPI_SR_TXE` або звільнення `SPI_SR_BSY`, назавжди зависає в нескінченному циклі опитування, оскільки вимкнений блок SPI блокує генерацію тактових імпульсів.

Алгоритм детермінованого виходу з колізії SPI Bus Contention вимагає чіткої послідовності:
1. **Скидання прапорця MODF**: виконується обов'язкове зчитування статусного регістра `SPI_SR` з наступним записом у регістр конфігурації `SPI_CR1`.
2. **Арбітражна пауза Backoff**: модуль відпускає всі індивідуальні лінії вибору чипів CS і переходить у режим очікування на час `t_backoff = t_base * 2^attempt + jitter`, контролюючи стан апаратної лінії готовності шини `BUS_BUSY` через функцію `dwt_wait_register_bit`.
3. **Реініціалізація та повернення прав Master**: після звільнення лінії іншим ведучим драйвер заново виставляє біти `SPI_CR1_MSTR` та `SPI_CR1_PE`, відновлюючи конфігурацію ліній GPIO.

Окремим випадком колізії є зависання лінії MISO веденим чипом, коли через передчасне зняття сигналу CS під час попередньої транзакції ведений не завершив внутрішній зсувний цикл і не перевів свій вихідний буфер у стан Hi-Z. Для розблокування шини ведучий примусово виставляє низький рівень CS і генерує на лінії SCK пакет із 8–16 фіктивних тактових імпульсів (Dummy Clocks), що змушує автомат веденого завершити передачу невичитаного байта та коректно відпустити лінію MISO після підняття CS у високий рівень. Якщо лінія MISO не відновлюється, контролер ініціює Tier 2 (імпульс nRESET) або Tier 3 (повний цикл знеструмлення Power-Cycle).

### Функціональні обов'язки підсистем

1. **Таймерний рушій DWT**: забезпечення мікросекундної та наносекундної точності очікування апаратних прапорців із гарантованим математичним захистом від переповнення 32-бітного лічильника циклів `DWT->CYCCNT`. На відміну від таймерів RTOS або періодичних переривань SysTick, модуль DWT не створює накладних витрат на збереження контексту процесора і функціонує навіть при тимчасово замаскованих перериваннях (`__disable_irq()`).
2. **Підсистема 9-тактового відновлення шини I2C**: безпечне переведення виводів у режим відкритого стоку (GPIO Open-Drain), покрокова генерація до 9 імпульсів тактування SCL з контролем стану лінії SDA на кожному такті, примусове формування умов NACK та STOP, апаратний перезапуск периферійного модуля I2C.
3. **Менеджер трирівневої ескалації скидання**:
   - Рівень 1 (Tier 1): відправлення цифрових команд Soft-Reset по штатній шині або через адресу загального виклику General Call.
   - Рівень 2 (Tier 2): формування нормованого за часом апаратного імпульсу скидання на виділеному виводі nRESET.
   - Рівень 3 (Tier 3): повне знеструмлення комутованої шини живлення сенсорів через P-MOSFET або мікросхему Load Switch із попереднім переведенням усіх сигнальних виводів мікроконтролера в режим аналогового входу (Hi-Z) для усунення ефекту Phantom Back-Powering крізь захисні діоди ESD.
4. **Менеджер відновлення стану (Shadow Registers)**: підтримка кешу конфігураційних регістрів у RAM, перевірка цілісності фабричних коефіцієнтів калібрування за поліномом CRC-16 та алгоритм експоненційного відступу з випадковим джитером.
5. **Кільцевий буфер діагностики**: збереження детального часового журналу подій аварійного відновлення для післяаварійного аналізу в польових умовах.

### Апаратна конфігурація стенда

Для тестування розробленого модуля використовується мікроконтролер STM32F401RE / STM32F411RE (ядро ARM Cortex-M4F, 84/100 МГц), до якого підключено цифровий барометр Bosch BMP280 та трьохосьовий акселерометр STMicroelectronics LIS3DH за такою схемою:
- **I2C1 SCL**: вивід PB8 (Alternate Function AF4 / GPIO Open-Drain).
- **I2C1 SDA**: вивід PB9 (Alternate Function AF4 / GPIO Open-Drain).
- **Зовнішні підтягувальні резистори**: 4.7 кОм на лініях SCL та SDA до комутованої шини живлення V_SENSOR.
- **Вивід апаратного скидання nRESET**: вивід PB12 (GPIO Output Push-Pull, активний рівень 0).
- **Керування комутатором живлення V_SENSOR**: вивід PA8, що керує затвором P-канального польового транзистора (High-Side P-MOSFET, логічний нуль на PA8 відкриває транзистор і подає 3.3 В на сенсори).
- **Розрядна ємність шини живлення**: блокувальний керамічний конденсатор 10 мкФ паралельно з розрядним резистором 1 кОм.

## Модуль високоточних таймаутів на базі DWT

Підсистема детермінованих таймаутів реалізує прямий доступ до системного лічильника `DWT->CYCCNT`. Модуль підтримує монотонний відлік часу, стійкий до переривань планувальника RTOS та динамічної зміни тактової частоти процесора.

### Фізичні та математичні принципи вимірювання часу

Лічильник `DWT->CYCCNT` є невіддільною частиною блоку налагодження CoreDebug процесорів ARM Cortex-M. Лічильник інкрементується на кожному такті системної шини процесора SysClk. Для увімкнення лічильника необхідно активувати біт `TRCENA` (біт 24) у регістрі `CoreDebug->DEMCR` та біт `CYCCNTENA` (біт 0) у регістрі `DWT->CTRL`.

Головна перевага використання беззнакової модульної арифметики полягає в тому, що обчислення різниці `(uint32_t)(DWT->CYCCNT - start_cycles)` дає точний час у тактах навіть у момент переходу лічильника через максимальне значення `0xFFFFFFFF`. Це виключає необхідність використання критичних секцій, блокування переривань або змінних-прапорців переповнення.

При розрахунку кількості тактів для мікросекундних таймаутів застосовується 64-бітне проміжне множення `((uint64_t)timeout_us * SystemCoreClock) / 1000000ULL`. Це унеможливлює переповнення розрядної сітки 32-бітного цілого при множенні великих часових інтервалів на високі тактові частоти ядра (до 480 МГц).

Припустимо, процесор працює на частоті 168 МГц. Один такт ядра дорівнює `1 / 168 000 000 = 5.95 нс`. Затримка 10 мкс відповідає `10 * 168 = 1680 тактів`. Якщо таймер запущено за 200 тактів до переповнення лічильника (`start = 0xFFFFFF38`), а перевірка виконується, коли лічильник показує `0x000005C8` (1480), беззнакове віднімання `0x000005C8 - 0xFFFFFF38` дасть рівно `1680 тактів` (0x00000690), що безпомилково зафіксує завершення відведеного інтервалу.

На відміну від програмних затримок на інструкціях `NOP` чи циклах `for`, лічильник DWT повністю імунний до оптимізацій компілятора GCC/Clang (`-O0`, `-O2`, `-O3`, `-Os`), конвеєрних зупинок процесора (Pipeline Stalls) та затримок вибірки інструкцій із Flash-пам'яті (Flash Wait States).

:::tabs
@tab C99
```c
#ifndef DWT_TIMEOUT_H
#define DWT_TIMEOUT_H

#include <stdint.h>
#include <stdbool.h>
#include "stm32f4xx.h"

typedef struct {
    uint32_t start_cycles;
    uint32_t duration_cycles;
} dwt_timer_t;

// Ініціалізація лічильника DWT
static inline void dwt_timer_global_init(void) {
    CoreDebug->DEMCR |= CoreDebug_DEMCR_TRCENA_Msk;
    DWT->CYCCNT = 0;
    DWT->CTRL |= DWT_CTRL_CYCCNTENA_Msk;
}

// Запуск таймера на задану кількість мікросекунд
static inline void dwt_timer_start_us(dwt_timer_t *timer, uint32_t duration_us) {
    timer->start_cycles = DWT->CYCCNT;
    timer->duration_cycles = (uint32_t)(((uint64_t)duration_us * SystemCoreClock) / 1000000ULL);
}

// Запуск таймера на задану кількість мілісекунд
static inline void dwt_timer_start_ms(dwt_timer_t *timer, uint32_t duration_ms) {
    timer->start_cycles = DWT->CYCCNT;
    timer->duration_cycles = (uint32_t)(((uint64_t)duration_ms * SystemCoreClock) / 1000ULL);
}

// Перевірка завершення таймауту за модулем 2^32
static inline bool dwt_timer_is_expired(const dwt_timer_t *timer) {
    uint32_t elapsed = (uint32_t)(DWT->CYCCNT - timer->start_cycles);
    return elapsed >= timer->duration_cycles;
}

// Блокуюча мікросекундна затримка
static inline void dwt_delay_us(uint32_t us) {
    dwt_timer_t t;
    dwt_timer_start_us(&t, us);
    while (!dwt_timer_is_expired(&t));
}

// Блокуюча мілісекундна затримка
static inline void dwt_delay_ms(uint32_t ms) {
    for (uint32_t i = 0; i < ms; i++) {
        dwt_delay_us(1000);
    }
}

// Очікування прапорця в регістрі з таймаутом
static inline int dwt_wait_register_bit(volatile uint32_t *reg, uint32_t mask, bool expected_state, uint32_t timeout_us) {
    dwt_timer_t timer;
    dwt_timer_start_us(&timer, timeout_us);

    while (1) {
        bool current_state = (*reg & mask) != 0;
        if (current_state == expected_state) {
            return 0; // Успіх
        }
        if (dwt_timer_is_expired(&timer)) {
            return -1; // Помилка таймауту
        }
    }
}

#endif // DWT_TIMEOUT_H
```
@tab C++20
```cpp
#ifndef DWT_TIMEOUT_HPP
#define DWT_TIMEOUT_HPP

#include <cstdint>
#include <chrono>
#include <concepts>
#include <expected>
#include "stm32f4xx.h"

enum class TimeoutStatus : uint8_t {
    Success,
    TimeoutExpired
};

class DwtTimer {
public:
    static void global_init() noexcept {
        CoreDebug->DEMCR |= CoreDebug_DEMCR_TRCENA_Msk;
        DWT->CYCCNT = 0;
        DWT->CTRL |= DWT_CTRL_CYCCNTENA_Msk;
    }

    template <typename Rep, typename Period>
    explicit DwtTimer(std::chrono::duration<Rep, Period> duration) noexcept
        : start_cycles_{DWT->CYCCNT} {
        const auto us = std::chrono::duration_cast<std::chrono::microseconds>(duration).count();
        duration_cycles_ = static_cast<uint32_t>((static_cast<uint64_t>(us) * SystemCoreClock) / 1'000'000ULL);
    }

    [[nodiscard]] bool is_expired() const noexcept {
        const uint32_t elapsed = DWT->CYCCNT - start_cycles_;
        return elapsed >= duration_cycles_;
    }

    template <typename Predicate>
        requires std::predicate<Predicate>
    [[nodiscard]] std::expected<void, TimeoutStatus> wait_until(Predicate&& pred) const noexcept {
        while (!pred()) {
            if (is_expired()) {
                return std::unexpected(TimeoutStatus::TimeoutExpired);
            }
        }
        return {};
    }

    static void delay(std::chrono::microseconds us) noexcept {
        const DwtTimer timer{us};
        while (!timer.is_expired());
    }

    static void delay(std::chrono::milliseconds ms) noexcept {
        const auto count = ms.count();
        for (int64_t i = 0; i < count; ++i) {
            delay(std::chrono::microseconds{1000});
        }
    }

private:
    uint32_t start_cycles_{0};
    uint32_t duration_cycles_{0};
};

#endif // DWT_TIMEOUT_HPP
```
:::

## Модуль електричного розблокування шини I2C 9 тактовими імпульсами

Підсистема здійснює програмне керування виводами шини I2C у режимі відкритого стоку (GPIO Bit-Banging), коли апаратний периферійний модуль мікроконтролера блокується через затиснуту веденим лінію SDA.

### Детальний аналіз процедури ручного тактування

Коли апаратний контролер I2C виявляє, що лінія SDA притиснута до землі у вихідному стані шини, його внутрішній автомат переходить у стан блокування шини (Bus Busy). У такому стані регістр `I2C_CR1` ігнорує спроби виставити біт `START`. Єдиний спосіб вивести систему з клінчу — тимчасово конфігурувати виводи GPIO як звичайні виходи з відкритим стоком і вручну згенерувати імпульси тактування.

Процедура складається з суворо визначеної послідовності дій:
1. **Деактивація периферійного модуля**: скидання біта `I2C_CR1_PE` ізолює внутрішній скінченний автомат I2C від фізичних виводів.
2. **Конфігурація виводів SCL та SDA в Open-Drain**: виводи налаштовуються як `GPIO_MODE_OUTPUT_OD` із максимальною швидкістю перемикання (High Speed) без внутрішніх підтяжок, оскільки на платі встановлені зовнішні резистори 4.7 кОм.
3. **Діагностика лінії SCL**: якщо лінія SCL утримується в нулі веденим пристроєм (збій Clock Stretching), спроби тактування марні, оскільки ведений заблокував тактування. Модуль фіксує помилку `I2C_RECOVER_ERR_SCL_STUCK_LOW` і негайно делегує відновлення менеджеру ескалації скидання живленням.
4. **Формування серії тактових імпульсів**: ведучий генерує до 9 прямокутних імпульсів із тривалістю низького стану не менше 4.7 мкс та високого стану не менше 4.0 мкс. Після кожного позитивного фронту контролюється рівень SDA: якщо ведений чип виштовхнув останній нульовий біт зі свого зсувного регістра, лінія SDA піднімається до 3.3 В під дією підтягувального резистора.
5. **Формування умов NACK та STOP**: ведучий утримує лінію SDA у високому стані під час завершального такту (сигнал NACK для веденого), після чого опускає SDA в нуль, піднімає SCL в одиницю і з затримкою переводить SDA з нуля в одиницю, формуючи бездоганну за часовими інтервалами умову STOP.
6. **Апаратний реініт модуля I2C**: для усунення внутрішніх заблокованих станів контролера I2C виставляється біт програмного скидання `I2C_CR1_SWRST`, після чого виводи повертаються в режим альтернативної функції (Alternate Function AF4) і модуль I2C вмикається знову.

Під час перемикання виводів між функціями GPIO та AF особливу увагу слід звертати на порядок запису в регістри `BSRR` та `MODER`. Запис одиниці в `BSRR` перед зміною режиму в `MODER` гарантує, що вихідний буфер не згенерує помилкового імпульсу нульового рівня, який міг би бути хибно інтерпретований зовнішніми сенсорами як новий спадний фронт тактування.

Кожен такт ручного тактування супроводжується обов'язковим зчитуванням регістра `GPIO_IDR` лінії SDA під час високого рівня SCL. Якщо сенсор звільнив лінію раніше (наприклад, на третьому або п'ятому такті), лічильник циклів фіксує точну кількість витрачених імпульсів `pulses_applied`. Ця величина передається у діагностичний журнал для оцінки характеру зависання (на якому саме біті байта стався попередній обрив транзакції).

:::tabs
@tab C99
```c
#ifndef I2C_BUS_RECOVERY_H
#define I2C_BUS_RECOVERY_H

#include <stdint.h>
#include <stdbool.h>
#include "stm32f4xx.h"
#include "dwt_timeout.h"

typedef enum {
    I2C_RECOVER_OK = 0,
    I2C_RECOVER_ERR_SCL_STUCK_LOW = -1,
    I2C_RECOVER_ERR_SDA_STUCK_LOW = -2,
    I2C_RECOVER_ERR_NULL_PARAM = -3
} i2c_recover_status_t;

typedef struct {
    I2C_TypeDef *i2c;
    GPIO_TypeDef *scl_port;
    uint8_t scl_pin;
    GPIO_TypeDef *sda_port;
    uint8_t sda_pin;
    uint8_t scl_af;
    uint8_t sda_af;
} i2c_bus_hardware_t;

static inline void i2c_pin_set_output_od(GPIO_TypeDef *port, uint8_t pin) {
    // Встановлюємо високий рівень перед конфігурацією виходу
    port->BSRR = (1U << pin);
    // Mode = Output (01)
    port->MODER &= ~(3U << (pin * 2));
    port->MODER |= (1U << (pin * 2));
    // Output Type = Open Drain (1)
    port->OTYPER |= (1U << pin);
    // Speed = High Speed (11)
    port->OSPEEDR |= (3U << (pin * 2));
    // No Pull (00)
    port->PUPDR &= ~(3U << (pin * 2));
}

static inline void i2c_pin_set_af_od(GPIO_TypeDef *port, uint8_t pin, uint8_t af) {
    // Mode = Alternate Function (10)
    port->MODER &= ~(3U << (pin * 2));
    port->MODER |= (2U << (pin * 2));
    // Output Type = Open Drain (1)
    port->OTYPER |= (1U << pin);
    // AF selection
    if (pin < 8) {
        port->AFR[0] &= ~(0xFU << (pin * 4));
        port->AFR[0] |= ((uint32_t)af << (pin * 4));
    } else {
        port->AFR[1] &= ~(0xFU << ((pin - 8) * 4));
        port->AFR[1] |= ((uint32_t)af << ((pin - 8) * 4));
    }
}

i2c_recover_status_t i2c_bus_unlock_9_pulses(const i2c_bus_hardware_t *hw, uint8_t *out_pulses_needed) {
    if (!hw || !hw->i2c || !hw->scl_port || !hw->sda_port) {
        return I2C_RECOVER_ERR_NULL_PARAM;
    }

    if (out_pulses_needed) {
        *out_pulses_needed = 0;
    }

    // 1. Вимикаємо апаратний блок I2C
    hw->i2c->CR1 &= ~I2C_CR1_PE;

    // 2. Переводимо SCL та SDA у GPIO Open-Drain
    i2c_pin_set_output_od(hw->scl_port, hw->scl_pin);
    i2c_pin_set_output_od(hw->sda_port, hw->sda_pin);

    dwt_delay_us(10);

    // 3. Перевіряємо лінію SCL на затискання веденим
    if ((hw->scl_port->IDR & (1U << hw->scl_pin)) == 0) {
        // SCL притиснута до землі: фатальний збій Clock Stretching
        i2c_pin_set_af_od(hw->scl_port, hw->scl_pin, hw->scl_af);
        i2c_pin_set_af_od(hw->sda_port, hw->sda_pin, hw->sda_af);
        return I2C_RECOVER_ERR_SCL_STUCK_LOW;
    }

    // 4. Генерація серії до 9 тактових імпульсів
    bool sda_freed = false;
    uint8_t pulse_count = 0;

    for (pulse_count = 0; pulse_count < 9; pulse_count++) {
        // Якщо SDA вже у високому рівні, шину розблоковано
        if ((hw->sda_port->IDR & (1U << hw->sda_pin)) != 0) {
            sda_freed = true;
            break;
        }

        // SCL = 0 (Low)
        hw->scl_port->BSRR = (1U << (hw->scl_pin + 16));
        dwt_delay_us(5); // t_LOW >= 4.7 us

        // SCL = 1 (High)
        hw->scl_port->BSRR = (1U << hw->scl_pin);
        dwt_delay_us(5); // t_HIGH >= 4.0 us
    }

    if ((hw->sda_port->IDR & (1U << hw->sda_pin)) != 0) {
        sda_freed = true;
    }

    if (out_pulses_needed) {
        *out_pulses_needed = pulse_count;
    }

    // 5. Примусова генерація умови STOP: SDA 0 -> 1 при SCL = 1
    hw->sda_port->BSRR = (1U << (hw->sda_pin + 16)); // SDA = 0
    dwt_delay_us(5);
    hw->scl_port->BSRR = (1U << hw->scl_pin);        // SCL = 1
    dwt_delay_us(5);
    hw->sda_port->BSRR = (1U << hw->sda_pin);        // SDA = 1
    dwt_delay_us(10);

    // 6. Повертаємо виводи в режим Alternate Function
    i2c_pin_set_af_od(hw->scl_port, hw->scl_pin, hw->scl_af);
    i2c_pin_set_af_od(hw->sda_port, hw->sda_pin, hw->sda_af);

    // 7. Скидаємо модуль I2C через регістр SWRST
    hw->i2c->CR1 |= I2C_CR1_SWRST;
    dwt_delay_us(5);
    hw->i2c->CR1 &= ~I2C_CR1_SWRST;

    // Вмикаємо периферійний модуль
    hw->i2c->CR1 |= I2C_CR1_PE;

    return sda_freed ? I2C_RECOVER_OK : I2C_RECOVER_ERR_SDA_STUCK_LOW;
}

#endif // I2C_BUS_RECOVERY_H
```
@tab C++20
```cpp
#ifndef I2C_BUS_RECOVERY_HPP
#define I2C_BUS_RECOVERY_HPP

#include <cstdint>
#include <chrono>
#include <expected>
#include "stm32f4xx.h"
#include "dwt_timeout.hpp"

enum class I2cRecoveryError : uint8_t {
    SclStuckLow,
    SdaStuckLow,
    InvalidHardware
};

struct GpioPinConfig {
    GPIO_TypeDef* port{nullptr};
    uint8_t pin{0};
    uint8_t af{4};

    void set_output_open_drain() const noexcept {
        port->BSRR = (1U << pin);
        port->MODER &= ~(3U << (pin * 2));
        port->MODER |= (1U << (pin * 2));
        port->OTYPER |= (1U << pin);
        port->OSPEEDR |= (3U << (pin * 2));
        port->PUPDR &= ~(3U << (pin * 2));
    }

    void set_alternate_function_open_drain() const noexcept {
        port->MODER &= ~(3U << (pin * 2));
        port->MODER |= (2U << (pin * 2));
        port->OTYPER |= (1U << pin);
        if (pin < 8) {
            port->AFR[0] &= ~(0xFU << (pin * 4));
            port->AFR[0] |= (static_cast<uint32_t>(af) << (pin * 4));
        } else {
            port->AFR[1] &= ~(0xFU << ((pin - 8) * 4));
            port->AFR[1] |= (static_cast<uint32_t>(af) << ((pin - 8) * 4));
        }
    }

    void set_high() const noexcept { port->BSRR = (1U << pin); }
    void set_low() const noexcept { port->BSRR = (1U << (pin + 16)); }
    [[nodiscard]] bool read() const noexcept { return (port->IDR & (1U << pin)) != 0; }
};

class I2cBusRecoveryEngine {
public:
    struct Hardware {
        I2C_TypeDef* i2c{nullptr};
        GpioPinConfig scl{};
        GpioPinConfig sda{};
    };

    struct RecoveryReport {
        uint8_t pulses_applied{0};
        bool sda_initially_stuck{false};
    };

    static std::expected<RecoveryReport, I2cRecoveryError> execute(const Hardware& hw) noexcept {
        if (!hw.i2c || !hw.scl.port || !hw.sda.port) {
            return std::unexpected(I2cRecoveryError::InvalidHardware);
        }

        RecoveryReport report{};

        // 1. Вимикаємо I2C
        hw.i2c->CR1 &= ~I2C_CR1_PE;

        // 2. Переводимо піни в GPIO Open-Drain
        hw.scl.set_output_open_drain();
        hw.sda.set_output_open_drain();

        DwtTimer::delay(std::chrono::microseconds{10});

        // 3. Перевірка SCL
        if (!hw.scl.read()) {
            hw.scl.set_alternate_function_open_drain();
            hw.sda.set_alternate_function_open_drain();
            return std::unexpected(I2cRecoveryError::SclStuckLow);
        }

        report.sda_initially_stuck = !hw.sda.read();

        // 4. Подача до 9 імпульсів
        bool freed = false;
        for (uint8_t i = 0; i < 9; ++i) {
            if (hw.sda.read()) {
                freed = true;
                break;
            }
            report.pulses_applied++;

            hw.scl.set_low();
            DwtTimer::delay(std::chrono::microseconds{5});
            hw.scl.set_high();
            DwtTimer::delay(std::chrono::microseconds{5});
        }

        if (hw.sda.read()) {
            freed = true;
        }

        // 5. Умова STOP
        hw.sda.set_low();
        DwtTimer::delay(std::chrono::microseconds{5});
        hw.scl.set_high();
        DwtTimer::delay(std::chrono::microseconds{5});
        hw.sda.set_high();
        DwtTimer::delay(std::chrono::microseconds{10});

        // 6. Відновлення режимів пінів
        hw.scl.set_alternate_function_open_drain();
        hw.sda.set_alternate_function_open_drain();

        // 7. Скидання модуля периферії
        hw.i2c->CR1 |= I2C_CR1_SWRST;
        DwtTimer::delay(std::chrono::microseconds{5});
        hw.i2c->CR1 &= ~I2C_CR1_SWRST;
        hw.i2c->CR1 |= I2C_CR1_PE;

        if (!freed) {
            return std::unexpected(I2cRecoveryError::SdaStuckLow);
        }

        return report;
    }
};

#endif // I2C_BUS_RECOVERY_HPP
```
:::

## Контролер трирівневої ескалації та керування живленням

Модуль ескалації керує апаратними ключами скидання пристрою:
- **Tier 1 (Soft-Reset)**: відправлення програмної команди скидання через I2C/SPI.
- **Tier 2 (Pin-Reset)**: формування імпульсу на виводі nRESET тривалістю 5 мс із затримкою 20 мс на стабілізацію POR.
- **Tier 3 (Power-Cycle)**: повна ізоляція всіх ліній зв'язку в режим Analog Hi-Z, розмикання P-MOSFET комутатора живлення на 50 мс для повного розряду ємностей `tau = R * C`, увімкнення живлення та очікування 20 мс завершення внутрішнього холодного старту.

### Фізичні аспекти комутації живлення та захист від Phantom Powering

Під час розмикання силового ключа живлення P-MOSFET на комутованій лінії живлення V_SENSOR напруга не спадає миттєво. Встановлені на платі керамічні та танталові конденсатори утримують накопичений заряд. Якщо струм споживання знеструмлених мікросхем падає до мікроампер, розряд через струми витоку може займати десятки секунд. Для гарантованого швидкого спаду напруги паралельно встановлюють розрядний резистор `R_discharge = 1 кОм`. При ємності 10 мкФ постійна часу розряду становить:
`tau = R * C = 1000 Ом * 10 мкФ = 10 мс`.
Для падіння напруги нижче 1% від початкового рівня (від 3.3 В до 0.03 В) тривалість знеструмленого стану встановлюється рівною `5 * tau = 50 мс`.

Найважливішим правилом процедури Power-Cycle є попередня ізоляція всіх цифрових виводів мікроконтролера, з'єднаних із сенсором (SCL, SDA, CS, MOSI, MISO, SCK, nRESET, INT). До розмикання силового ключа всі ці виводи переводяться в режим `GPIO_MODE_ANALOG` (`MODER = 0b11`). У цьому режимі вихідні польові транзистори мікроконтролера закриті, вхідні цифрові буфери знеструмлені, а вивід переходить у стан високого імпедансу (Hi-Z) зі струмом витоку менше 1 нА. Це повністю унеможливлює протікання паразитного струму через верхні захисні ESD-діоди сенсора у знеструмлену шину живлення V_SENSOR.

Керування комутатором реалізовано з урахуванням активного логічного рівня: для P-MOSFET активним рівнем увімкнення є логічний нуль на затворі (`pwr_switch_active_high = false`), а для інтегрованих мікросхем Load Switch із прямим керуванням Enable — логічна одиниця (`pwr_switch_active_high = true`).

Під час відновлення живлення (Power-Up) витримується обов'язкова пауза стабілізації `power_on_settle_ms` (20 мс). Протягом цього вікна внутрішній генератор опорної напруги (Bandgap Reference) та аналоговий супервізор скидання за живленням (Power-On Reset, POR) веденого чипа завершують вихід на стабільний режим, а внутрішній контролер пам'яті копіює калібрувальні таблиці з OTP ROM в оперативні регістри.

### Захист від тиристорного замикання (CMOS Latch-up)

У напівпровідниковій структурі КМОН-мікросхем суміжні комплементарні транзистори формують паразитну чотиришарову структуру p-n-p-n (еквівалент кремнієвого симістора/тиристора SCR). При короткочасному перенапруженні входу або протіканні надлишкового струму через захисні діоди ESD паразитна структура відмикається. Після відкриття тиристор залишається в провідному стані навіть після зникнення завади, створюючи пряме коротке замикання шини живлення на землю. Струм утримування `I_hold` може сягати 50–200 мА, викликаючи лавиноподібний нагрів кристала.

Єдиним фізично можливим методом виходу з тиристорного клінчу є повне зняття напруги живлення нижче порогу утримання (менше 0.5 В). Саме тому процедура Tier 3 (Power-Cycle) є обов'язковим завершальним рубежем ескалації, гарантуючи розрив струмової петлі тиристора.

:::tabs
@tab C99
```c
#ifndef RESET_ESCALATION_CONTROLLER_H
#define RESET_ESCALATION_CONTROLLER_H

#include <stdint.h>
#include <stdbool.h>
#include "stm32f4xx.h"
#include "dwt_timeout.h"
#include "i2c_bus_recovery.h"

typedef enum {
    ESCALATION_TIER_0_NONE = 0,
    ESCALATION_TIER_1_SOFT_RESET = 1,
    ESCALATION_TIER_2_PIN_RESET = 2,
    ESCALATION_TIER_3_POWER_CYCLE = 3,
    ESCALATION_TIER_FATAL = 4
} escalation_tier_t;

typedef struct {
    // Керування комутатором живлення
    GPIO_TypeDef *pwr_switch_port;
    uint8_t pwr_switch_pin;
    bool pwr_switch_active_high; // true = 1 ON, false = 0 ON (для P-MOSFET)

    // Керування виводом апаратного скидання
    GPIO_TypeDef *nrst_port;
    uint8_t nrst_pin;

    // Сигнальні лінії для переведення в Hi-Z
    GPIO_TypeDef *scl_port;
    uint8_t scl_pin;
    uint8_t scl_af;
    GPIO_TypeDef *sda_port;
    uint8_t sda_pin;
    uint8_t sda_af;

    // Часові параметри
    uint32_t reset_pulse_ms;
    uint32_t reset_settle_ms;
    uint32_t power_off_duration_ms;
    uint32_t power_on_settle_ms;
} peripheral_power_control_t;

typedef struct {
    peripheral_power_control_t power_cfg;
    i2c_bus_hardware_t i2c_hw;
    escalation_tier_t current_tier;
    uint8_t consecutive_failures;
    uint32_t total_tier1_count;
    uint32_t total_tier2_count;
    uint32_t total_tier3_count;
} reset_escalation_manager_t;

static inline void pin_set_analog_hiz(GPIO_TypeDef *port, uint8_t pin) {
    // Mode = Analog (11)
    port->MODER |= (3U << (pin * 2));
    // PUPDR = No pull (00)
    port->PUPDR &= ~(3U << (pin * 2));
}

void escalation_manager_init(reset_escalation_manager_t *mgr, const peripheral_power_control_t *pwr_cfg, const i2c_bus_hardware_t *i2c_hw) {
    mgr->power_cfg = *pwr_cfg;
    mgr->i2c_hw = *i2c_hw;
    mgr->current_tier = ESCALATION_TIER_0_NONE;
    mgr->consecutive_failures = 0;
    mgr->total_tier1_count = 0;
    mgr->total_tier2_count = 0;
    mgr->total_tier3_count = 0;

    // Початкова конфігурація силового виводу
    if (mgr->power_cfg.pwr_switch_port) {
        GPIO_TypeDef *p = mgr->power_cfg.pwr_switch_port;
        uint8_t pin = mgr->power_cfg.pwr_switch_pin;
        p->MODER &= ~(3U << (pin * 2));
        p->MODER |= (1U << (pin * 2)); // Output Push-Pull
        p->OTYPER &= ~(1U << pin);
        // Вмикаємо живлення
        if (mgr->power_cfg.pwr_switch_active_high) {
            p->BSRR = (1U << pin);
        } else {
            p->BSRR = (1U << (pin + 16)); // Low для P-MOSFET
        }
    }

    // Початкова конфігурація виводу nRESET у високий стан
    if (mgr->power_cfg.nrst_port) {
        GPIO_TypeDef *p = mgr->power_cfg.nrst_port;
        uint8_t pin = mgr->power_cfg.nrst_pin;
        p->MODER &= ~(3U << (pin * 2));
        p->MODER |= (1U << (pin * 2)); // Output
        p->BSRR = (1U << pin);         // High (неактивний)
    }
}

void escalation_execute_tier2_pin_reset(reset_escalation_manager_t *mgr) {
    if (!mgr->power_cfg.nrst_port) return;

    GPIO_TypeDef *p = mgr->power_cfg.nrst_port;
    uint8_t pin = mgr->power_cfg.nrst_pin;

    // 1. Опускаємо nRESET у 0
    p->BSRR = (1U << (pin + 16));
    dwt_delay_ms(mgr->power_cfg.reset_pulse_ms ? mgr->power_cfg.reset_pulse_ms : 5);

    // 2. Піднімаємо nRESET у 1
    p->BSRR = (1U << pin);
    dwt_delay_ms(mgr->power_cfg.reset_settle_ms ? mgr->power_cfg.reset_settle_ms : 20);

    mgr->total_tier2_count++;
}

void escalation_execute_tier3_power_cycle(reset_escalation_manager_t *mgr) {
    if (!mgr->power_cfg.pwr_switch_port) return;

    // 1. Ізоляція всіх ліній: переведення SCL, SDA, nRESET в Analog Hi-Z
    pin_set_analog_hiz(mgr->power_cfg.scl_port, mgr->power_cfg.scl_pin);
    pin_set_analog_hiz(mgr->power_cfg.sda_port, mgr->power_cfg.sda_pin);
    if (mgr->power_cfg.nrst_port) {
        pin_set_analog_hiz(mgr->power_cfg.nrst_port, mgr->power_cfg.nrst_pin);
    }

    // 2. Знеструмлення: закриваємо MOSFET
    GPIO_TypeDef *pwr = mgr->power_cfg.pwr_switch_port;
    uint8_t pwr_pin = mgr->power_cfg.pwr_switch_pin;
    if (mgr->power_cfg.pwr_switch_active_high) {
        pwr->BSRR = (1U << (pwr_pin + 16)); // Low = OFF
    } else {
        pwr->BSRR = (1U << pwr_pin);        // High = OFF (P-MOSFET)
    }

    // 3. Пауза для повного розряду ємностей шини (50 мс)
    dwt_delay_ms(mgr->power_cfg.power_off_duration_ms ? mgr->power_cfg.power_off_duration_ms : 50);

    // 4. Подача живлення: відкриваємо MOSFET
    if (mgr->power_cfg.pwr_switch_active_high) {
        pwr->BSRR = (1U << pwr_pin);        // High = ON
    } else {
        pwr->BSRR = (1U << (pwr_pin + 16)); // Low = ON (P-MOSFET)
    }

    // 5. Очікування стабілізації живлення та POR
    dwt_delay_ms(mgr->power_cfg.power_on_settle_ms ? mgr->power_cfg.power_on_settle_ms : 20);

    // 6. Відновлення режиму виводу nRESET
    if (mgr->power_cfg.nrst_port) {
        GPIO_TypeDef *nrst = mgr->power_cfg.nrst_port;
        uint8_t nrst_pin = mgr->power_cfg.nrst_pin;
        nrst->MODER &= ~(3U << (nrst_pin * 2));
        nrst->MODER |= (1U << (nrst_pin * 2)); // Output
        nrst->BSRR = (1U << nrst_pin);         // High
    }

    // 7. Відновлення режимів альтернативної функції для SCL та SDA
    i2c_pin_set_af_od(mgr->power_cfg.scl_port, mgr->power_cfg.scl_pin, mgr->power_cfg.scl_af);
    i2c_pin_set_af_od(mgr->power_cfg.sda_port, mgr->power_cfg.sda_pin, mgr->power_cfg.sda_af);

    mgr->total_tier3_count++;
}

escalation_tier_t escalation_step(reset_escalation_manager_t *mgr) {
    mgr->consecutive_failures++;

    if (mgr->consecutive_failures == 1) {
        mgr->current_tier = ESCALATION_TIER_1_SOFT_RESET;
        i2c_bus_unlock_9_pulses(&mgr->i2c_hw, NULL);
        mgr->total_tier1_count++;
    } else if (mgr->consecutive_failures == 2) {
        mgr->current_tier = ESCALATION_TIER_2_PIN_RESET;
        escalation_execute_tier2_pin_reset(mgr);
    } else if (mgr->consecutive_failures == 3) {
        mgr->current_tier = ESCALATION_TIER_3_POWER_CYCLE;
        escalation_execute_tier3_power_cycle(mgr);
    } else {
        mgr->current_tier = ESCALATION_TIER_FATAL;
    }

    return mgr->current_tier;
}

void escalation_mark_success(reset_escalation_manager_t *mgr) {
    mgr->consecutive_failures = 0;
    mgr->current_tier = ESCALATION_TIER_0_NONE;
}

#endif // RESET_ESCALATION_CONTROLLER_H
```
@tab C++20
```cpp
#ifndef RESET_ESCALATION_CONTROLLER_HPP
#define RESET_ESCALATION_CONTROLLER_HPP

#include <cstdint>
#include <chrono>
#include "stm32f4xx.h"
#include "dwt_timeout.hpp"
#include "i2c_bus_recovery.hpp"

enum class EscalationTier : uint8_t {
    None,
    Tier1SoftReset,
    Tier2PinReset,
    Tier3PowerCycle,
    Fatal
};

struct PowerSwitchPin {
    GPIO_TypeDef* port{nullptr};
    uint8_t pin{0};
    bool active_high{false}; // false для P-MOSFET

    void configure() const noexcept {
        port->MODER &= ~(3U << (pin * 2));
        port->MODER |= (1U << (pin * 2));
        turn_on();
    }

    void turn_on() const noexcept {
        if (active_high) port->BSRR = (1U << pin);
        else port->BSRR = (1U << (pin + 16));
    }

    void turn_off() const noexcept {
        if (active_high) port->BSRR = (1U << (pin + 16));
        else port->BSRR = (1U << pin);
    }
};

class EscalationManager {
public:
    struct Config {
        PowerSwitchPin power_switch{};
        GpioPinConfig nrst_pin{};
        GpioPinConfig scl_pin{};
        GpioPinConfig sda_pin{};
        I2C_TypeDef* i2c{nullptr};
        std::chrono::milliseconds reset_pulse{5};
        std::chrono::milliseconds reset_settle{20};
        std::chrono::milliseconds power_off_duration{50};
        std::chrono::milliseconds power_on_settle{20};
    };

    explicit EscalationManager(Config cfg) noexcept : cfg_{cfg} {
        if (cfg_.power_switch.port) {
            cfg_.power_switch.configure();
        }
        if (cfg_.nrst_pin.port) {
            cfg_.nrst_pin.port->MODER &= ~(3U << (cfg_.nrst_pin.pin * 2));
            cfg_.nrst_pin.port->MODER |= (1U << (cfg_.nrst_pin.pin * 2));
            cfg_.nrst_pin.set_high();
        }
    }

    EscalationTier escalate_fault() noexcept {
        ++consecutive_failures_;

        if (consecutive_failures_ == 1) {
            current_tier_ = EscalationTier::Tier1SoftReset;
            I2cBusRecoveryEngine::execute({cfg_.i2c, cfg_.scl_pin, cfg_.sda_pin});
            ++total_tier1_;
        } else if (consecutive_failures_ == 2) {
            current_tier_ = EscalationTier::Tier2PinReset;
            execute_tier2_pin_reset();
            ++total_tier2_;
        } else if (consecutive_failures_ == 3) {
            current_tier_ = EscalationTier::Tier3PowerCycle;
            execute_tier3_power_cycle();
            ++total_tier3_;
        } else {
            current_tier_ = EscalationTier::Fatal;
        }

        return current_tier_;
    }

    void record_success() noexcept {
        consecutive_failures_ = 0;
        current_tier_ = EscalationTier::None;
    }

    [[nodiscard]] EscalationTier current_tier() const noexcept { return current_tier_; }

private:
    Config cfg_;
    EscalationTier current_tier_{EscalationTier::None};
    uint8_t consecutive_failures_{0};
    uint32_t total_tier1_{0};
    uint32_t total_tier2_{0};
    uint32_t total_tier3_{0};

    void execute_tier2_pin_reset() const noexcept {
        if (!cfg_.nrst_pin.port) return;
        cfg_.nrst_pin.set_low();
        DwtTimer::delay(cfg_.reset_pulse);
        cfg_.nrst_pin.set_high();
        DwtTimer::delay(cfg_.reset_settle);
    }

    void execute_tier3_power_cycle() const noexcept {
        if (!cfg_.power_switch.port) return;

        // 1. Hi-Z ізоляція
        isolate_pin(cfg_.scl_pin);
        isolate_pin(cfg_.sda_pin);
        if (cfg_.nrst_pin.port) isolate_pin(cfg_.nrst_pin);

        // 2. Знеструмлення
        cfg_.power_switch.turn_off();
        DwtTimer::delay(cfg_.power_off_duration);

        // 3. Увімкнення живлення
        cfg_.power_switch.turn_on();
        DwtTimer::delay(cfg_.power_on_settle);

        // 4. Відновлення nRESET
        if (cfg_.nrst_pin.port) {
            cfg_.nrst_pin.port->MODER &= ~(3U << (cfg_.nrst_pin.pin * 2));
            cfg_.nrst_pin.port->MODER |= (1U << (cfg_.nrst_pin.pin * 2));
            cfg_.nrst_pin.set_high();
        }

        // 5. Відновлення шини
        cfg_.scl_pin.set_alternate_function_open_drain();
        cfg_.sda_pin.set_alternate_function_open_drain();
    }

    static void isolate_pin(const GpioPinConfig& pin) noexcept {
        pin.port->MODER |= (3U << (pin.pin * 2));   // Analog
        pin.port->PUPDR &= ~(3U << (pin.pin * 2));  // No Pull
    }
};

#endif // RESET_ESCALATION_CONTROLLER_HPP
```
:::

## Підсистема тіньових регістрів та відновлення стану сенсора

Модуль забезпечує повне збереження робочої конфігурації сенсора в пам'яті RAM мікроконтролера та автоматичне відновлення після будь-якого рівня ескалації.

### Верифікація калібрувальних коефіцієнтів за CRC-16

Сенсори фізичних величин (тиск, вологість, температура, напруженість магнітного поля) калібруються на заводі виробника під час фінального тестування на пластині. Індивідуальні поліноміальні поправочні коефіцієнти записуються в енергонезалежну пам'ять OTP (One-Time Programmable) або в масковане ROM чипа. Наприклад, барометр BMP280 містить 24 байти калібрування (`dig_T1..dig_T3`, `dig_P1..dig_P9`), без яких коректний розрахунок тиску в паскалях неможливий.

При першому старті драйвер вичитує весь блок калібрувальних коефіцієнтів і обчислює контрольну суму за поліномом CRC-16-CCITT (`x^16 + x^12 + x^5 + 1`, ініціалізація `0xFFFF`). Під час повторних ініціалізацій після збоїв живлення драйвер звіряє щойно зчитані дані з кешованою копією. Якщо контрольна сума не збігається (наприклад, через збій внутрішнього LDO сенсора в момент читання), драйвер бракує прочитані дані й повторює процедуру холодного старту.

Особливістю архітектури є повне відокремлення волатильних конфігураційних регістрів (частота вихідних даних ODR, повнорозмірний діапазон вимірювань, коефіцієнти цифрових фільтрів IIR/DLPF) від статичних калібрувальних таблиць. Тіньові регістри оновлюються при кожному програмному виклику функцій налаштування, тому відновлення стану після знеструмлення займає менше 1 мс і не вимагає перерахунку математичних моделей верхнього рівня.

У таблиці тіньових регістрів кожен запис містить 8-бітну адресу регістра та 8-бітне значення. При виклику процедури реконфігурації драйвер послідовно проходить по масиву тіньових записів і відправляє їх у сенсор за допомогою одиночних транзакцій запису або пакетної передачі Burst Write.

### Алгоритм експоненційного відступу з випадковим джитером

Якщо кілька сенсорів на спільній шині живлення зазнали одночасного збою (наприклад, внаслідок короткочасного просідання бортової мережі), їхні драйвери не повинні починати повторні спроби зв'язку в один і той самий момент часу. Одночасні спроби призводять до виникнення арбітражних колізій на шині I2C та пікових стрибків споживання струму.

Для розподілу навантаження в часі інтервал між спробами обчислюється за формулою:
`t_backoff = t_base * 2^attempt + jitter`,
де `t_base` дорівнює 10 мс, а псевдовипадковий джитер `jitter` формується з молодших 4 бітів системного лічильника `DWT->CYCCNT` (значення від 0 до 15 мс). Це розносить фази повторних запусків різних сенсорів у часі, усуваючи взаємне блокування шини.

:::tabs
@tab C99
```c
#ifndef SENSOR_STATE_RECOVERY_H
#define SENSOR_STATE_RECOVERY_H

#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define MAX_SHADOW_REGISTERS 16
#define MAX_CALIBRATION_BYTES 32

typedef struct {
    uint8_t reg_addr;
    uint8_t value;
} shadow_reg_entry_t;

typedef struct {
    shadow_reg_entry_t registers[MAX_SHADOW_REGISTERS];
    uint8_t reg_count;
    uint8_t calib_data[MAX_CALIBRATION_BYTES];
    uint8_t calib_length;
    uint16_t calib_crc16;
    bool calib_valid;
} sensor_shadow_cache_t;

static inline uint16_t calculate_crc16_ccitt(const uint8_t *data, size_t length) {
    uint16_t crc = 0xFFFF;
    for (size_t i = 0; i < length; i++) {
        crc ^= (uint16_t)data[i] << 8;
        for (uint8_t bit = 0; bit < 8; bit++) {
            if (crc & 0x8000) {
                crc = (crc << 1) ^ 0x1021;
            } else {
                crc = crc << 1;
            }
        }
    }
    return crc;
}

void shadow_cache_init(sensor_shadow_cache_t *cache) {
    memset(cache, 0, sizeof(sensor_shadow_cache_t));
}

void shadow_cache_set_reg(sensor_shadow_cache_t *cache, uint8_t reg_addr, uint8_t value) {
    for (uint8_t i = 0; i < cache->reg_count; i++) {
        if (cache->registers[i].reg_addr == reg_addr) {
            cache->registers[i].value = value;
            return;
        }
    }
    if (cache->reg_count < MAX_SHADOW_REGISTERS) {
        cache->registers[cache->reg_count].reg_addr = reg_addr;
        cache->registers[cache->reg_count].value = value;
        cache->reg_count++;
    }
}

void shadow_cache_store_calib(sensor_shadow_cache_t *cache, const uint8_t *calib, uint8_t length) {
    if (length > MAX_CALIBRATION_BYTES) length = MAX_CALIBRATION_BYTES;
    memcpy(cache->calib_data, calib, length);
    cache->calib_length = length;
    cache->calib_crc16 = calculate_crc16_ccitt(calib, length);
    cache->calib_valid = true;
}

bool shadow_cache_verify_calib(const sensor_shadow_cache_t *cache, const uint8_t *calib, uint8_t length) {
    if (!cache->calib_valid || length != cache->calib_length) return false;
    uint16_t crc = calculate_crc16_ccitt(calib, length);
    return crc == cache->calib_crc16;
}

#endif // SENSOR_STATE_RECOVERY_H
```
@tab C++20
```cpp
#ifndef SENSOR_STATE_RECOVERY_HPP
#define SENSOR_STATE_RECOVERY_HPP

#include <cstdint>
#include <array>
#include <span>
#include <algorithm>

template <size_t MaxRegs = 16, size_t MaxCalib = 32>
class SensorShadowCache {
public:
    struct RegisterEntry {
        uint8_t address{0};
        uint8_t value{0};
    };

    constexpr SensorShadowCache() noexcept = default;

    void set_register(uint8_t address, uint8_t value) noexcept {
        for (size_t i = 0; i < reg_count_; ++i) {
            if (registers_[i].address == address) {
                registers_[i].value = value;
                return;
            }
        }
        if (reg_count_ < MaxRegs) {
            registers_[reg_count_++] = {address, value};
        }
    }

    [[nodiscard]] std::span<const RegisterEntry> registers() const noexcept {
        return {registers_.data(), reg_count_};
    }

    void store_calibration(std::span<const uint8_t> calib) noexcept {
        const size_t len = std::min(calib.size(), MaxCalib);
        std::copy_n(calib.data(), len, calib_data_.begin());
        calib_len_ = len;
        calib_crc_ = compute_crc16(calib.subspan(0, len));
        calib_valid_ = true;
    }

    [[nodiscard]] bool verify_calibration(std::span<const uint8_t> calib) const noexcept {
        if (!calib_valid_ || calib.size() != calib_len_) return false;
        return compute_crc16(calib) == calib_crc_;
    }

private:
    std::array<RegisterEntry, MaxRegs> registers_{};
    size_t reg_count_{0};
    std::array<uint8_t, MaxCalib> calib_data_{};
    size_t calib_len_{0};
    uint16_t calib_crc_{0};
    bool calib_valid_{false};

    static constexpr uint16_t compute_crc16(std::span<const uint8_t> data) noexcept {
        uint16_t crc = 0xFFFF;
        for (const uint8_t byte : data) {
            crc ^= static_cast<uint16_t>(byte) << 8;
            for (uint8_t bit = 0; bit < 8; ++bit) {
                if (crc & 0x8000) {
                    crc = (crc << 1) ^ 0x1021;
                } else {
                    crc = crc << 1;
                }
            }
        }
        return crc;
    }
};

#endif // SENSOR_STATE_RECOVERY_HPP
```
:::

## Кільцевий буфер діагностики та телеметрії відмов

Для точної фіксації апаратних збоїв модуль містить діагностичний кільцевий буфер `bus_diagnostics_log_t`, що записує часову мітку DWT, тип події, кількість витрачених тактів відновлення та код статусу.

### Структура запису та аналіз аварійного журналу

Кожен елемент діагностичного журналу зберігає:
- `timestamp_cycles`: точний зліпок системного лічильника `DWT->CYCCNT` у момент реєстрації збою.
- `event_type`: тип зафіксованої апаратної події (таймаут передавача TXE, таймаут приймача RXNE, блокування 9 імпульсів, виконання ескалації Tier 1–3 або помилка контрольної суми CRC калібрування).
- `peripheral_id`: числовий ідентифікатор цільової мікросхеми на спільній шині.
- `status_code`: внутрішній статус операції введення-виведення.
- `aux_data`: додаткові параметри (наприклад, номер поточної спроби відновлення).

Утилізація фіксованого масиву з циклічним індексом голови (`head = (head + 1) % Capacity`) виключає блокування пам'яті, гарантує швидкість виконання операції запису за 5–7 тактів процесора і дозволяє безпечно вичитувати журнал під час регламентного технічного обслуговування або після посадки безпілотного апарата.

Коли прилад повертається з польової місії, діагностична утиліта зчитує весь кільцевий буфер через інтерфейс налагодження SWD або серійний порт UART. Наявність записів `EVENT_TIER1_SOFT_RESET` сигналізує про електромагнітні наведенки на сигнальні лінії плати, тоді як поява `EVENT_TIER3_POWER_CYCLE` вказує на глибокі просідання живлення або дефекти роз'ємів зовнішніх модулів.

Завдяки фіксації міток DWT розробник може з мікросекундною точністю оцінити тривалість кожного етапу відновлення: від моменту виявлення першого таймауту до повного завершення переконфігурації регістрів після холодного старту.

:::tabs
@tab C99
```c
#ifndef BUS_DIAGNOSTICS_H
#define BUS_DIAGNOSTICS_H

#include <stdint.h>
#include <stdbool.h>

#define DIAGNOSTIC_LOG_CAPACITY 32

typedef enum {
    EVENT_NONE = 0,
    EVENT_TIMEOUT_TXE,
    EVENT_TIMEOUT_RXNE,
    EVENT_BUS_LOCKUP_9PULSES,
    EVENT_TIER1_SOFT_RESET,
    EVENT_TIER2_PIN_RESET,
    EVENT_TIER3_POWER_CYCLE,
    EVENT_CALIBRATION_CRC_ERROR,
    EVENT_RECOVERY_SUCCESS
} bus_event_type_t;

typedef struct {
    uint32_t timestamp_cycles;
    bus_event_type_t event_type;
    uint8_t peripheral_id;
    int8_t status_code;
    uint8_t aux_data;
} bus_log_entry_t;

typedef struct {
    bus_log_entry_t entries[DIAGNOSTIC_LOG_CAPACITY];
    uint16_t head;
    uint16_t count;
    uint32_t total_events_recorded;
} bus_diagnostics_log_t;

void diagnostics_log_init(bus_diagnostics_log_t *log) {
    log->head = 0;
    log->count = 0;
    log->total_events_recorded = 0;
}

void diagnostics_log_record(bus_diagnostics_log_t *log, bus_event_type_t event, uint8_t periph_id, int8_t status, uint8_t aux) {
    bus_log_entry_t *entry = &log->entries[log->head];
    entry->timestamp_cycles = DWT->CYCCNT;
    entry->event_type = event;
    entry->peripheral_id = periph_id;
    entry->status_code = status;
    entry->aux_data = aux;

    log->head = (log->head + 1) % DIAGNOSTIC_LOG_CAPACITY;
    if (log->count < DIAGNOSTIC_LOG_CAPACITY) {
        log->count++;
    }
    log->total_events_recorded++;
}

#endif // BUS_DIAGNOSTICS_H
```
@tab C++20
```cpp
#ifndef BUS_DIAGNOSTICS_HPP
#define BUS_DIAGNOSTICS_HPP

#include <cstdint>
#include <array>
#include <span>
#include "stm32f4xx.h"

enum class DiagnosticEventType : uint8_t {
    None,
    TimeoutTxe,
    TimeoutRxne,
    BusLockup9Pulses,
    Tier1SoftReset,
    Tier2PinReset,
    Tier3PowerCycle,
    CalibrationCrcError,
    RecoverySuccess
};

struct DiagnosticEntry {
    uint32_t timestamp_cycles{0};
    DiagnosticEventType event{DiagnosticEventType::None};
    uint8_t peripheral_id{0};
    int8_t status_code{0};
    uint8_t aux_data{0};
};

template <size_t Capacity = 32>
class DiagnosticLog {
public:
    constexpr DiagnosticLog() noexcept = default;

    void record(DiagnosticEventType event, uint8_t periph_id, int8_t status = 0, uint8_t aux = 0) noexcept {
        entries_[head_] = DiagnosticEntry{
            .timestamp_cycles = DWT->CYCCNT,
            .event = event,
            .peripheral_id = periph_id,
            .status_code = status,
            .aux_data = aux
        };
        head_ = (head_ + 1) % Capacity;
        if (count_ < Capacity) ++count_;
        ++total_recorded_;
    }

    [[nodiscard]] size_t count() const noexcept { return count_; }
    [[nodiscard]] uint32_t total_recorded() const noexcept { return total_recorded_; }

private:
    std::array<DiagnosticEntry, Capacity> entries_{};
    size_t head_{0};
    size_t count_{0};
    uint32_t total_recorded_{0};
};

#endif // BUS_DIAGNOSTICS_HPP
```
:::

## Повний інтеграційний приклад та випробувальний стенд

Об'єднаємо всі створені підсистеми у закінчений виробничий драйвер датчика тиску BMP280, що підтримує самодіагностику, таймаути та автоматичне трирівневе відновлення.

### Сценарії випробувань та апаратна верифікація

Для перевірки стійкості драйвера на стенді моделюються чотири типові види апаратних відмов:
1. **Коротке замикання SDA на землю (SDA Bus Stuck Low)**: під час активного зчитування даних лінія SDA штучно замикається на контакт GND через тестовий ключ. Драйвер фіксує таймаут, автоматично запускає модуль 9 тактових імпульсів, генерує STOP і успішно відновлює обмін після розмикання тестового ключа.
2. **Збій живлення сенсора (Brown-out Glitch)**: комутується короткочасний провал напруги живлення до 1.5 В. Внутрішній автомат сенсора зависає і перестає відповідати на ACK. Драйвер здійснює програмне скидання Tier 1, після чого успішно переходить до апаратного імпульсу nRESET (Tier 2) або Power-Cycle (Tier 3), відновлюючи параметри з тіньових регістрів.
3. **Електростатичний імпульс (ESD Latch-up Simulation)**: імітується тиристорне замикання, коли струм споживання мікросхеми зростає в десятки разів, а виводи блокуються. Менеджер ескалації виконує повне знеструмлення через P-MOSFET, витримує 50 мс для розряду конденсаторів і здійснює холодний рестарт системи.
4. **Контроль цілісності OTP-коефіцієнтів**: перевіряється, що після виконання Power-Cycle драйвер заново вичитує калібрувальні коефіцієнти та звіряє їх за поліномом CRC-16.

Драйвер обробляє кожну транзакцію вводу-виводу через набір детермінованих функцій `bmp280_raw_i2c_write` та `bmp280_raw_i2c_read`. Будь-яка затримка понад 2000 мкс (2 мс) на очікуванні прапорців `SB`, `ADDR`, `TXE`, `RXNE` чи `BTF` перериває транзакцію та передає керування функції ескалації `bmp280_recover_and_restore`.

### Інтеграція у багатозадачне середовище RTOS

У системах під керуванням FreeRTOS або Zephyr RTOS процедури скидання шини вимагають координації між різними потоками виконання. Якщо на спільній шині I2C працюють три незалежні задачі (опитування барометра, зчитування орієнтації IMU та контроль температури акумулятора), процедура апаратного розблокування чи знеструмлення шини повинна бути атомарною.

Перед початком ескалації задача захоплює двійковий семафор або м'ютекс шини (Bus Mutex), тимчасово блокуючи запити інших потоків. Після завершення Power-Cycle координатор відновлення оновлює статус прапорця готовності шини та викликає функції реініціалізації для всіх зареєстрованих на цій шині сенсорних драйверів.

### Методика автоматизованого стрес-тестування (Hardware-in-the-Loop)

Для підтвердження надійності вбудованого ПЗ у виробничому циклі стенд комплектується допоміжним мікроконтролером-генератором апаратних збоїв (Fault Injector). Генератор підключається до ліній SCL, SDA та V_SENSOR через високошвидкісні польові транзистори і виконує випадкове внесення завад:
- Примусове закорочування SDA на землю в момент передачі 5-го біта адреси.
- Генерація невалідних сплесків напруги на тактовій лінії SCL тривалістю 50 нс під час очікування сигналу ACK.
- Скидання напруги живлення сенсора до 0 В на інтервали від 100 мкс до 10 мс.

Автоматизований тестовий сценарій виконує понад 100 000 циклів читання даних із сенсора в умовах безперервного генератора помилок. Критерієм успішного проходження тесту є 100% відновлення обміну даними без зависання центрального процесора мікроконтролера та нульова кількість пропущених детермінованих таймаутів.

:::tabs
@tab C99
```c
#include <stdio.h>
#include <stdbool.h>
#include "stm32f4xx.h"
#include "dwt_timeout.h"
#include "i2c_bus_recovery.h"
#include "reset_escalation_controller.h"
#include "sensor_state_recovery.h"
#include "bus_diagnostics.h"

#define BMP280_I2C_ADDR 0x76
#define BMP280_CHIP_ID_REG 0xD0
#define BMP280_EXPECTED_ID 0x58
#define BMP280_RESET_REG 0xE0
#define BMP280_CTRL_MEAS_REG 0xF4
#define BMP280_CONFIG_REG 0xF5

typedef struct {
    reset_escalation_manager_t escalation;
    sensor_shadow_cache_t shadow;
    bus_diagnostics_log_t diag_log;
    uint8_t i2c_addr;
} bmp280_resilient_driver_t;

int bmp280_raw_i2c_write(I2C_TypeDef *i2c, uint8_t addr, uint8_t reg, uint8_t val) {
    // 1. Очікуємо звільнення шини з таймаутом 2 мс
    if (dwt_wait_register_bit(&i2c->SR2, I2C_SR2_BUSY, false, 2000) != 0) {
        return -1;
    }

    // 2. Генеруємо START
    i2c->CR1 |= I2C_CR1_START;
    if (dwt_wait_register_bit(&i2c->SR1, I2C_SR1_SB, true, 2000) != 0) {
        return -2;
    }

    // 3. Відправляємо адресу пристрою (Write)
    i2c->DR = (uint8_t)(addr << 1);
    if (dwt_wait_register_bit(&i2c->SR1, I2C_SR1_ADDR, true, 2000) != 0) {
        i2c->CR1 |= I2C_CR1_STOP;
        return -3; // NACK адреси
    }
    (void)i2c->SR2; // Очищення ADDR читанням SR2

    // 4. Відправляємо адресу регістра
    i2c->DR = reg;
    if (dwt_wait_register_bit(&i2c->SR1, I2C_SR1_TXE, true, 2000) != 0) {
        i2c->CR1 |= I2C_CR1_STOP;
        return -4;
    }

    // 5. Відправляємо дані
    i2c->DR = val;
    if (dwt_wait_register_bit(&i2c->SR1, I2C_SR1_BTF, true, 2000) != 0) {
        i2c->CR1 |= I2C_CR1_STOP;
        return -5;
    }

    // 6. Генеруємо STOP
    i2c->CR1 |= I2C_CR1_STOP;
    return 0;
}

int bmp280_raw_i2c_read(I2C_TypeDef *i2c, uint8_t addr, uint8_t reg, uint8_t *out_val) {
    if (dwt_wait_register_bit(&i2c->SR2, I2C_SR2_BUSY, false, 2000) != 0) return -1;

    i2c->CR1 |= I2C_CR1_START;
    if (dwt_wait_register_bit(&i2c->SR1, I2C_SR1_SB, true, 2000) != 0) return -2;

    i2c->DR = (uint8_t)(addr << 1);
    if (dwt_wait_register_bit(&i2c->SR1, I2C_SR1_ADDR, true, 2000) != 0) {
        i2c->CR1 |= I2C_CR1_STOP;
        return -3;
    }
    (void)i2c->SR2;

    i2c->DR = reg;
    if (dwt_wait_register_bit(&i2c->SR1, I2C_SR1_TXE, true, 2000) != 0) {
        i2c->CR1 |= I2C_CR1_STOP;
        return -4;
    }

    // Повторний старт (Repeated START)
    i2c->CR1 |= I2C_CR1_START;
    if (dwt_wait_register_bit(&i2c->SR1, I2C_SR1_SB, true, 2000) != 0) return -5;

    i2c->DR = (uint8_t)((addr << 1) | 1); // Read
    if (dwt_wait_register_bit(&i2c->SR1, I2C_SR1_ADDR, true, 2000) != 0) {
        i2c->CR1 |= I2C_CR1_STOP;
        return -6;
    }
    i2c->CR1 &= ~I2C_CR1_ACK; // NACK перед останнім байтом
    (void)i2c->SR2;
    i2c->CR1 |= I2C_CR1_STOP;

    if (dwt_wait_register_bit(&i2c->SR1, I2C_SR1_RXNE, true, 2000) != 0) return -7;
    *out_val = (uint8_t)i2c->DR;

    return 0;
}

int bmp280_recover_and_restore(bmp280_resilient_driver_t *drv) {
    escalation_tier_t tier = escalation_step(&drv->escalation);
    diagnostics_log_record(&drv->diag_log, (bus_event_type_t)(EVENT_TIER1_SOFT_RESET + (tier - 1)), 1, -1, drv->escalation.consecutive_failures);

    if (tier == ESCALATION_TIER_FATAL) {
        return -100; // Фатальна відмова периферії
    }

    // Перевірка працездатності: зчитування ID
    uint8_t chip_id = 0;
    int res = bmp280_raw_i2c_read(drv->escalation.i2c_hw.i2c, drv->i2c_addr, BMP280_CHIP_ID_REG, &chip_id);
    if (res != 0 || chip_id != BMP280_EXPECTED_ID) {
        return -1; // Сенсор ще не готовий, вимагає подальшої ескалації
    }

    // Відновлення робочих регістрів із тіньового кешу
    for (uint8_t i = 0; i < drv->shadow.reg_count; i++) {
        bmp280_raw_i2c_write(drv->escalation.i2c_hw.i2c, drv->i2c_addr,
                             drv->shadow.registers[i].reg_addr,
                             drv->shadow.registers[i].value);
    }

    escalation_mark_success(&drv->escalation);
    diagnostics_log_record(&drv->diag_log, EVENT_RECOVERY_SUCCESS, 1, 0, 0);
    return 0;
}

int bmp280_init(bmp280_resilient_driver_t *drv, const peripheral_power_control_t *pwr, const i2c_bus_hardware_t *i2c_hw) {
    dwt_timer_global_init();
    escalation_manager_init(&drv->escalation, pwr, i2c_hw);
    shadow_cache_init(&drv->shadow);
    diagnostics_log_init(&drv->diag_log);
    drv->i2c_addr = BMP280_I2C_ADDR;

    // Конфігурація робочих параметрів
    shadow_cache_set_reg(&drv->shadow, BMP280_CTRL_MEAS_REG, 0x57); // Normal mode, OverSampling x16
    shadow_cache_set_reg(&drv->shadow, BMP280_CONFIG_REG, 0x10);    // Standby 0.5ms, Filter coeff 16

    // Первинна ініціалізація
    uint8_t id = 0;
    if (bmp280_raw_i2c_read(drv->escalation.i2c_hw.i2c, drv->i2c_addr, BMP280_CHIP_ID_REG, &id) != 0 || id != BMP280_EXPECTED_ID) {
        return bmp280_recover_and_restore(drv);
    }

    // Запис конфігурації
    for (uint8_t i = 0; i < drv->shadow.reg_count; i++) {
        bmp280_raw_i2c_write(drv->escalation.i2c_hw.i2c, drv->i2c_addr,
                             drv->shadow.registers[i].reg_addr,
                             drv->shadow.registers[i].value);
    }

    return 0;
}

int bmp280_read_temperature_pressure(bmp280_resilient_driver_t *drv, int32_t *temp, uint32_t *press) {
    uint8_t data[6];
    for (uint8_t i = 0; i < 6; i++) {
        int res = bmp280_raw_i2c_read(drv->escalation.i2c_hw.i2c, drv->i2c_addr, (uint8_t)(0xF7 + i), &data[i]);
        if (res != 0) {
            // Апаратна аварія під час читання: запускаємо відновлення
            bmp280_recover_and_restore(drv);
            return -1;
        }
    }

    *press = (uint32_t)((data[0] << 12) | (data[1] << 4) | (data[2] >> 4));
    *temp = (int32_t)((data[3] << 12) | (data[4] << 4) | (data[5] >> 4));
    return 0;
}
```
@tab C++20
```cpp
#include <cstdint>
#include <expected>
#include <array>
#include "stm32f4xx.h"
#include "dwt_timeout.hpp"
#include "i2c_bus_recovery.hpp"
#include "reset_escalation_controller.hpp"
#include "sensor_state_recovery.hpp"
#include "bus_diagnostics.hpp"

class ResilientBmp280Driver {
public:
    enum class DriverError : uint8_t {
        BusError,
        InvalidChipId,
        FatalPeripheralLockup
    };

    struct RawMeasurement {
        int32_t raw_temperature{0};
        uint32_t raw_pressure{0};
    };

    ResilientBmp280Driver(EscalationManager::Config cfg, uint8_t i2c_addr = 0x76) noexcept
        : escalation_{cfg}, i2c_hw_{cfg.i2c, cfg.scl_pin, cfg.sda_pin}, i2c_addr_{i2c_addr} {
        DwtTimer::global_init();
        shadow_.set_register(0xF4 /* CTRL_MEAS */, 0x57);
        shadow_.set_register(0xF5 /* CONFIG */, 0x10);
    }

    [[nodiscard]] std::expected<void, DriverError> initialize() noexcept {
        auto check_id = [this]() -> bool {
            auto val = raw_read_byte(0xD0);
            return val.has_value() && *val == 0x58;
        };

        if (!check_id()) {
            return recover_escalation();
        }

        // Запис конфігурації
        for (const auto& reg : shadow_.registers()) {
            if (!raw_write_byte(reg.address, reg.value)) {
                return recover_escalation();
            }
        }

        escalation_.record_success();
        diag_log_.record(DiagnosticEventType::RecoverySuccess, 1, 0);
        return {};
    }

    [[nodiscard]] std::expected<RawMeasurement, DriverError> read_sample() noexcept {
        std::array<uint8_t, 6> raw_buf{};
        for (size_t i = 0; i < 6; ++i) {
            auto b = raw_read_byte(static_cast<uint8_t>(0xF7 + i));
            if (!b) {
                auto rec_res = recover_escalation();
                if (!rec_res) return std::unexpected(rec_res.error());
                return std::unexpected(DriverError::BusError);
            }
            raw_buf[i] = *b;
        }

        RawMeasurement m{};
        m.raw_pressure = (static_cast<uint32_t>(raw_buf[0]) << 12) |
                         (static_cast<uint32_t>(raw_buf[1]) << 4) |
                         (static_cast<uint32_t>(raw_buf[2]) >> 4);
        m.raw_temperature = (static_cast<int32_t>(raw_buf[3]) << 12) |
                            (static_cast<int32_t>(raw_buf[4]) << 4) |
                            (static_cast<int32_t>(raw_buf[5]) >> 4);
        return m;
    }

private:
    EscalationManager escalation_;
    I2cBusRecoveryEngine::Hardware i2c_hw_;
    SensorShadowCache<8, 32> shadow_{};
    DiagnosticLog<32> diag_log_{};
    uint8_t i2c_addr_{0x76};

    [[nodiscard]] std::expected<void, DriverError> recover_escalation() noexcept {
        const auto tier = escalation_.escalate_fault();
        diag_log_.record(static_cast<DiagnosticEventType>(static_cast<uint8_t>(DiagnosticEventType::Tier1SoftReset) + static_cast<uint8_t>(tier) - 1), 1, -1);

        if (tier == EscalationTier::Fatal) {
            return std::unexpected(DriverError::FatalPeripheralLockup);
        }

        // Перевірка готовності чипа після скидання
        auto id = raw_read_byte(0xD0);
        if (!id || *id != 0x58) {
            return std::unexpected(DriverError::InvalidChipId);
        }

        // Відновлення конфігурації
        for (const auto& reg : shadow_.registers()) {
            if (!raw_write_byte(reg.address, reg.value)) {
                return std::unexpected(DriverError::BusError);
            }
        }

        escalation_.record_success();
        diag_log_.record(DiagnosticEventType::RecoverySuccess, 1, 0);
        return {};
    }

    [[nodiscard]] std::expected<uint8_t, DriverError> raw_read_byte(uint8_t reg) const noexcept {
        auto* i2c = i2c_hw_.i2c;
        const DwtTimer timer{std::chrono::microseconds{2000}};

        // Wait busy
        if (!timer.wait_until([i2c] { return (i2c->SR2 & I2C_SR2_BUSY) == 0; })) return std::unexpected(DriverError::BusError);

        i2c->CR1 |= I2C_CR1_START;
        if (!timer.wait_until([i2c] { return (i2c->SR1 & I2C_SR1_SB) != 0; })) return std::unexpected(DriverError::BusError);

        i2c->DR = static_cast<uint8_t>(i2c_addr_ << 1);
        if (!timer.wait_until([i2c] { return (i2c->SR1 & I2C_SR1_ADDR) != 0; })) {
            i2c->CR1 |= I2C_CR1_STOP;
            return std::unexpected(DriverError::BusError);
        }
        (void)i2c->SR2;

        i2c->DR = reg;
        if (!timer.wait_until([i2c] { return (i2c->SR1 & I2C_SR1_TXE) != 0; })) {
            i2c->CR1 |= I2C_CR1_STOP;
            return std::unexpected(DriverError::BusError);
        }

        i2c->CR1 |= I2C_CR1_START;
        if (!timer.wait_until([i2c] { return (i2c->SR1 & I2C_SR1_SB) != 0; })) return std::unexpected(DriverError::BusError);

        i2c->DR = static_cast<uint8_t>((i2c_addr_ << 1) | 1);
        if (!timer.wait_until([i2c] { return (i2c->SR1 & I2C_SR1_ADDR) != 0; })) {
            i2c->CR1 |= I2C_CR1_STOP;
            return std::unexpected(DriverError::BusError);
        }
        i2c->CR1 &= ~I2C_CR1_ACK;
        (void)i2c->SR2;
        i2c->CR1 |= I2C_CR1_STOP;

        if (!timer.wait_until([i2c] { return (i2c->SR1 & I2C_SR1_RXNE) != 0; })) return std::unexpected(DriverError::BusError);
        return static_cast<uint8_t>(i2c->DR);
    }

    [[nodiscard]] std::expected<void, DriverError> raw_write_byte(uint8_t reg, uint8_t val) const noexcept {
        auto* i2c = i2c_hw_.i2c;
        const DwtTimer timer{std::chrono::microseconds{2000}};

        if (!timer.wait_until([i2c] { return (i2c->SR2 & I2C_SR2_BUSY) == 0; })) return std::unexpected(DriverError::BusError);

        i2c->CR1 |= I2C_CR1_START;
        if (!timer.wait_until([i2c] { return (i2c->SR1 & I2C_SR1_SB) != 0; })) return std::unexpected(DriverError::BusError);

        i2c->DR = static_cast<uint8_t>(i2c_addr_ << 1);
        if (!timer.wait_until([i2c] { return (i2c->SR1 & I2C_SR1_ADDR) != 0; })) {
            i2c->CR1 |= I2C_CR1_STOP;
            return std::unexpected(DriverError::BusError);
        }
        (void)i2c->SR2;

        i2c->DR = reg;
        if (!timer.wait_until([i2c] { return (i2c->SR1 & I2C_SR1_TXE) != 0; })) {
            i2c->CR1 |= I2C_CR1_STOP;
            return std::unexpected(DriverError::BusError);
        }

        i2c->DR = val;
        if (!timer.wait_until([i2c] { return (i2c->SR1 & I2C_SR1_BTF) != 0; })) {
            i2c->CR1 |= I2C_CR1_STOP;
            return std::unexpected(DriverError::BusError);
        }

        i2c->CR1 |= I2C_CR1_STOP;
        return {};
    }
};
```
:::

Створений модуль забезпечує повний цикл автономного виявлення, електричного розблокування ліній зв'язку та багатоступеневого відновлення працездатності периферійних вузлів у критичних вбудованих застосунках. Завдяки ізоляції ліній у стан високого імпедансу Hi-Z перед кожним циклом знеструмлення, система повністю усуває небезпеку тиристорного замикання (CMOS Latch-up) та гарантує надійний повторний старт чипів у жорстких промислових умовах експлуатації. Впровадження кільцевого журналу діагностики дозволяє сервісним інженерам точно відновлювати хронологію виникнення аварійних подій під час польового розслідування інцидентів.