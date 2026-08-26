# ⚙️ Програмний кондуктор бісекційної самодіагностики плати

Коли новозібрана плата або пристрій після відмови в полі не стартує у штатному режимі, налагодження без системного інструменту перетворюється на хаотичні здогадки: чи завис мікроконтролер, чи замкнуло зовнішню шину, чи просіло живлення під час ініціалізації радіомодуля. Цей проєкт розбирає архітектуру та повну реалізацію автономного діагностичного кондуктора (*Bisection Self-Test Conductor*), який методом покрокової бісекції послідовно ізолює апаратні вузли, перевіряє цілісність кристала, шин і пам'яті, локалізуючи дефектний каскад до конкретного функціонального блоку.

### Принцип сходів довіри та ізоляція шарів

Кондуктор побудований за принципом сходів довіри (*Trust Staircase*). У складній системі неможливо достовірно протестувати високорівневий протокол (наприклад, опитування сенсора по I2C або відправку пакета по SPI), якщо попередньо не доведено справність тактового генератора, ліній живлення та внутрішньої пам'яті MCU.

Тестування розбивається на незалежні рівні, розташовані від найнижчого (внутрішнє ядро мікроконтролера) до найвищого (RTOS-планувальник та мережевий стек). На кожному кроці кондуктор тестує рівно один ізольований шар, не спираючись на працездатність вищих підсистем:

1. **Рівень 0 (Кристал і базовий стек):** перевірка працездатності арифметично-логічного пристрою (ALU), цілісності базових регістрів процесора та сторожової мітки стеку (*Stack Canary*).
2. **Рівень 1 (Внутрішня SRAM):** неруйнівний бінарний маршовий тест пам'яті (March C- патерни `0x55AA` / `0xAA55`) для виявлення залипання адресних ліній та взаємного впливу сусідніх комірок.
3. **Рівень 2 (Шина живлення та тактування):** опитування внутрішніх компараторів PVD/BOD та перевірка стабільності PLL і кварцового резонатора HSE за апаратним таймером.
4. **Рівень 3 (Фізичний рівень цифрових шин):** перевірка стану ліній I2C/SPI в режимі GPIO (чи немає притискання SDA/SCL до землі або обриву ліній підтяжки без прямого звернення до мікросхем).
5. **Рівень 4 (Опитування ведених чипів):** бісекційне сканування адрес на шинах (Who-Am-I / Device ID) із захистом за жорстким апаратним таймаутом.
6. **Рівень 5 (Периферія та переривання):** вибірковий запуск обробників таймерів та перевірка латентності обробки переривань ISR.

### Реалізація тестового кондуктора

Утиліта підтримує два режими запуску:
- **Повна бісекційна діагностика (Auto-Bisection):** послідовне виконання сходинок із зупинкою на першому зламаному шарі та видачею точного діагнозу через аварійний UART або світлодіодний код помилки.
- **Ізольований бінарний тест (Subsystem Probe):** запуск конкретної ізольованої підсистеми з фіктивними вхідними даними (*Stub Injection*) для перевірки реакції алгоритмів обробки.

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

/* Коди результатів діагностичного тесту */
typedef enum {
    TEST_RES_PASS = 0,
    TEST_RES_FAIL_HARDWARE,
    TEST_RES_FAIL_TIMEOUT,
    TEST_RES_FAIL_INTEGRITY
} test_result_t;

/* Опис діагностичного ступеня */
typedef struct {
    const char *name;
    test_result_t (*run_test)(void);
    uint32_t timeout_us;
} diagnostic_step_t;

/* Сходинка 0: Перевірка сторожової мітки стеку та цілісності ALU */
static test_result_t test_core_and_stack(void) {
    volatile uint32_t canary = 0xDEADBEEF;
    volatile uint32_t a = 0x12345678;
    volatile uint32_t b = 0x87654321;
    
    if ((a ^ b) != 0x95511559) {
        return TEST_RES_FAIL_HARDWARE;
    }
    if (canary != 0xDEADBEEF) {
        return TEST_RES_FAIL_INTEGRITY;
    }
    return TEST_RES_PASS;
}

/* Сходинка 1: Маршовий тест локальної ділянки SRAM */
static test_result_t test_sram_patterns(void) {
    static volatile uint32_t test_buffer[32];
    const size_t len = sizeof(test_buffer) / sizeof(test_buffer[0]);
    
    /* Запис і перевірка шахового патерну 0x55555555 */
    for (size_t i = 0; i < len; ++i) {
        test_buffer[i] = 0x55555555UL;
    }
    for (size_t i = 0; i < len; ++i) {
        if (test_buffer[i] != 0x55555555UL) {
            return TEST_RES_FAIL_INTEGRITY;
        }
        test_buffer[i] = 0xAAAAAAAAUL; /* Інверсія */
    }
    for (size_t i = 0; i < len; ++i) {
        if (test_buffer[i] != 0xAAAAAAAAUL) {
            return TEST_RES_FAIL_INTEGRITY;
        }
    }
    return TEST_RES_PASS;
}

/* Сходинка 2: Ізольована перевірка стану ліній шини I2C (GPIO probe) */
static test_result_t test_i2c_bus_idle(void) {
    /* Симуляція читання фізичного стану ліній SDA / SCL перед стартом модуля.
       У реальному MCU: gpio_get_level(SDA_PIN) && gpio_get_level(SCL_PIN) */
    volatile bool sda_high = true;
    volatile bool scl_high = true;

    if (!sda_high || !scl_high) {
        /* Лінія затиснута до землі: апаратне КЗ або завислий ведений чип */
        return TEST_RES_FAIL_HARDWARE;
    }
    return TEST_RES_PASS;
}

/* Сходинка 3: Опитування ID сенсора з жорстким лічильником таймауту */
static test_result_t test_sensor_id_ping(void) {
    uint32_t timeout_counter = 10000;
    volatile uint8_t device_id = 0x00;
    
    /* Імітація обміну: читання регістра WHO_AM_I */
    while (timeout_counter > 0) {
        timeout_counter--;
        /* Запис/читання шини. Для тесту емулюємо успішну відповідь 0x68 */
        device_id = 0x68;
        if (device_id == 0x68) {
            return TEST_RES_PASS;
        }
    }
    return TEST_RES_FAIL_TIMEOUT;
}

/* Таблиця сходинок бісекційного кондуктора */
static const diagnostic_step_t DIAG_SUITE[] = {
    { "Core & Stack Integrity", test_core_and_stack, 100 },
    { "Internal SRAM March",    test_sram_patterns,   500 },
    { "I2C Bus Physical Lines", test_i2c_bus_idle,    200 },
    { "Sensor ID Verification", test_sensor_id_ping,  2000 }
};

/* Головний виконавець бісекційної самоперевірки */
int run_bisection_diagnostics(void) {
    const size_t total_steps = sizeof(DIAG_SUITE) / sizeof(DIAG_SUITE[0]);
    
    for (size_t i = 0; i < total_steps; ++i) {
        test_result_t res = DIAG_SUITE[i].run_test();
        if (res != TEST_RES_PASS) {
            /* Локалізовано дефект: рівень i ізолює винуватця */
            return (int)(i + 1); /* Повертаємо номер зламаної сходинки */
        }
    }
    return 0; /* Усі ізольовані тести пройдено успішно */
}
```
```cpp
#include <cstdint>
#include <cstddef>
#include <span>
#include <string_view>
#include <array>

namespace diag {

enum class Result : uint8_t {
    Pass = 0,
    FailHardware,
    FailTimeout,
    FailIntegrity
};

struct Step {
    std::string_view name;
    Result (*run)();
    uint32_t timeout_us;
};

class BisectionConductor {
public:
    static Result testCoreAndStack() noexcept {
        constexpr uint32_t expected_xor = 0x12345678UL ^ 0x87654321UL;
        volatile uint32_t canary = 0xDEADBEEFUL;
        volatile uint32_t a = 0x12345678UL;
        volatile uint32_t b = 0x87654321UL;

        if ((a ^ b) != expected_xor) {
            return Result::FailHardware;
        }
        if (canary != 0xDEADBEEFUL) {
            return Result::FailIntegrity;
        }
        return Result::Pass;
    }

    static Result testSramPatterns() noexcept {
        std::array<volatile uint32_t, 32> buffer{};
        
        for (auto& word : buffer) {
            word = 0x55555555UL;
        }
        for (auto& word : buffer) {
            if (word != 0x55555555UL) {
                return Result::FailIntegrity;
            }
            word = 0xAAAAAAAAUL;
        }
        for (const auto& word : buffer) {
            if (word != 0xAAAAAAAAUL) {
                return Result::FailIntegrity;
            }
        }
        return Result::Pass;
    }

    static Result testI2cBusIdle() noexcept {
        volatile bool sda_high = true;
        volatile bool scl_high = true;

        if (!sda_high || !scl_high) {
            return Result::FailHardware;
        }
        return Result::Pass;
    }

    static Result testSensorIdPing() noexcept {
        uint32_t timeout_counter = 10000;
        volatile uint8_t device_id = 0x00;

        while (timeout_counter > 0) {
            --timeout_counter;
            device_id = 0x68;
            if (device_id == 0x68) {
                return Result::Pass;
            }
        }
        return Result::FailTimeout;
    }

    static size_t runDiagnosticSuite(std::span<const Step> suite) noexcept {
        for (size_t idx = 0; idx < suite.size(); ++idx) {
            if (suite[idx].run() != Result::Pass) {
                return idx + 1; // Номер шару, де ланцюг обірвано
            }
        }
        return 0; // Всі підсистеми справні
    }
};

constexpr std::array<Step, 4> DiagnosticSuite{{
    { "Core & Stack Integrity", &BisectionConductor::testCoreAndStack, 100 },
    { "Internal SRAM March",    &BisectionConductor::testSramPatterns,   500 },
    { "I2C Bus Physical Lines", &BisectionConductor::testI2cBusIdle,    200 },
    { "Sensor ID Verification", &BisectionConductor::testSensorIdPing,  2000 }
}};

} // namespace diag

extern "C" int run_bisection_diagnostics_cpp() {
    return static_cast<int>(diag::BisectionConductor::runDiagnosticSuite(diag::DiagnosticSuite));
}
```
:::

### Відновлення завислої шини та скидання периферії

Якщо сходинка `test_i2c_bus_idle` виявляє затиснуту в нуль лінію SDA, кондуктор не переходить до опитування регістрів, а запускає процедуру апаратного відновлення шини (*Bus Recovery Sequence*):

1. Переведення виводів SCL та SDA в режим GPIO Open-Drain з внутрішньою або зовнішньою підтяжкою.
2. Генерація 9 тактових імпульсів на лінії SCL із частотою 100 кГц. Якщо ведений чип завис посеред байта читання й тримає SDA в нулі, чекаючи на черговий фронт тактового сигналу, дев'ять імпульсів змушують його завершити поточний байт і відпустити лінію SDA.
3. Формування умовного сигналу STOP (перехід SDA з низького рівня у високий при високому рівні SCL).
4. Повторне зчитування стану ліній: якщо лінія піднялася до 3.3 В — шину відновлено, дефект мав програмно-протокольний характер. Якщо лінія лишилася на 0 В — на платі присутнє фізичне коротке замикання або пробитий ESD-супресор.

### Аварійна телеметрія: фіксація діагнозу при мертвій периферії

Найскладніша ситуація під час самодіагностики — коли виявлено збій, але підсистема виводу (UART, USB, дисплей або мережевий інтерфейс) ще не ініціалізована або сама є пошкодженою. Кондуктор застосовує три рівні аварійної фіксації коду відмови (POST Code):

1. **Енергонезалежні регістри домену бекапу (RTC Backup Registers):** збереження номера зламаної сходинки та значення регістрів процесора в пам'ять `RTC->BKPxR`. Ця область живиться від резервної батарейки або іоністора й не очищується при звичайному програмному скиданні (`NVIC_SystemReset`).
2. **Морзе-спалахи або двійковий код на тестовому GPIO:** якщо консоль недоступна, номер помилки транслюється прямою зміною рівня одного виводу зі світлодіодом (наприклад, серія коротких спалахів із паузою, де 3 спалахи позначають падіння на сходинці 3 — фізична лінія I2C).
3. **Запис у спеціальну секцію SRAM (No-Init RAM):** виділення 64 байтів у пам'яті з атрибутом `__attribute__((section(".noinit")))`. Після виявлення відмови кондуктор записує туди сигнатуру дефекту, викликає програмне перезавантаження, і після рестарту завантажувач перевіряє цю ділянку до старту основної прошивки.

### Пастки та крайові випадки кондуктора

1. **Тестування пам'яті без руйнування стеку:** якщо запускати маршовий тест по всій оперативній пам'яті, функція зітре власний стек і покажчик повернення. Маршові тести в кондукторі повинні або запускатися з окремо виділеного статичного буфера (`static volatile`), або виконуватися на асемблері в `Reset_Handler` до ініціалізації секцій BSS і стеку.
2. **Вплив завислих шин на тактування ядра:** якщо помилка на шині I2C призводить до зависання апаратного контролера периферії, звичайний виклик `HAL_I2C_Init()` може намертво заблокувати ядро. Кондуктор спершу завжди перевіряє фізичні рівні ліній як звичайні GPIO, перш ніж передавати керування спеціалізованому апаратному блоку I2C.
3. **Обмеження таймаутів без використання переривань:** якщо системний таймер `SysTick` або таймери RTOS ще не перевірено, таймаут не може спиратися на `HAL_Delay()` чи лічильник мілісекунд. У кондукторі всі таймаути базових ступенів реалізуються як строгі циклічні лічильники (*Cycle Spin Loops*), які не залежать від стану системи переривань.
4. **Недеструктивність самодіагностики:** діагностичний кондуктор не повинен змінювати вміст енергонезалежної пам'яті (Flash / EEPROM) без явного прапорця команди, щоб не затерти журнал помилок або калібрувальні константи пристрою.
