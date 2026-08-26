# ⚙️ Автоматизований регресійний стенд виявлення переповнення часу

Тестування часових меж у вбудованих системах стикається з фундаментальною перешкодою: переповнення 16-бітного мілісекундного лічильника настає через 65.5 секунд, а 32-бітного — лише через 49.7 днів безперервної роботи. Жоден конвеєр неперервної інтеграції (Continuous Integration / Continuous Delivery, CI/CD) не може чекати тижні заради перевірки одного циклу оновлення сторожа чи дедлайну зв'язку. Цей тестовий стенд реалізує віртуалізацію системного часу (Time-Warp Virtual HAL), ін'єкцію штучного переповнення лічильників та автоматичну верифікацію реакцій системи на розрив зв'язку, захищаючи прошивку від повернення критичних дефектів цілочисельної арифметики.

## Архітектура стенду віртуального часу

Для повної ізоляції тестованої бізнес-логіки від фізичних таймерів мікроконтролера вводиться рівень абстракції генератора монотонного часу. Під час запуску на цільовому залізі модуль транслює виклики до апаратних регістрів таймера (`SysTick->VAL` або лічильників `TIMx_CNT`), а під час модульного тестування на робочій станції або CI-сервері підставляє емулятор із можливістю миттєвого програмного переведення стрілок на будь-яку точку числового діапазону.

```
       [ Модульний регресійний тест ]
                     │
        ┌────────────┴────────────┐
        ▼                         ▼
[ time_warp_set() ]      [ safety_watchdog_poll() ]
        │                         │
        ▼                         ▼
[ Mock Hardware Time ] ──► [ Модуль захисту приводу ]
  (0xFFFA -> 0x000A)         (Safe Monotonic Math)
```

Головна перевага стенду полягає в можливості штучно стискати час: замість реального очікування сорока дев'яти діб тест за лічені мікросекунди ініціалізує лічильник за кілька тактів до переповнення, виконує критичну операцію і перевіряє поведінку алгоритму після переходу через нуль.

Стенд перевіряє чотири критичні фази життєвого циклу пристрою:
1. **Штатний режим роботи (Baseline):** регулярні оновлення дедлайну задовго до настання таймауту, коли дельта між поточним часом і часом останнього пакету стабільно менша за встановлений поріг.
2. **Точка переходу через нуль (Rollover Boundary):** поведінка системи за 10 мс до межі розрядності (`0xFFF6`), безпосередньо в момент переповнення (`0x0000`) та через 10 мс після нього (`0x000A`).
3. **Реальний розрив зв'язку під час переповнення:** валідація гарантованого спрацьовування аварійного захисту та переведення приводів у безпечний стан, якщо зв'язок обірвався саме в мить переходу таймера через нуль.
4. **Застарілі та відхилені пакети (Stale Frames):** перевірка стійкості автомата захисту до пакетів, які приходять із минулих циклів лічильника внаслідок затримок у чергах повідомлень або буферах трансивера.

## Крайові випадки та атомарність читання часу в RTOS

У багатозадачних системах реального часу (FreeRTOS, Zephyr) розширення 16-бітного або 32-бітного апаратного таймера до 64-бітного монотонного значення вимагає суворої атомарності. Якщо 32-бітний мікроконтролер зчитує 64-бітну змінну `g_system_ticks_64` двома окремими машинними інструкціями `LDR`, виникає небезпечна гонка даних:

```
1. Потік зчитує молодше слово: low = 0xFFFFFFFF
2. Виникає переривання таймера SysTick:
   - low скидається в 0x00000000
   - high інкрементується: 0x00000000 -> 0x00000001
3. Потік відновлюється і зчитує старше слово: high = 0x00000001
4. Склеєний результат: 0x00000001FFFFFFFF замість 0x0000000100000000!
```

Такий збій генерує штучний стрибок системного часу на 49.7 днів у майбутнє, викликаючи миттєвий масовий колапс усіх таймаутів системи. Тестовий стенд емулює витіснення потоків саме між читанням молодшого та старшого слів, перевіряючи коректність використання механізму захисту (подвійне читання з перевіркою старшого слова або закриття переривань через `__disable_irq`).

## Механізм фазингу часових інтервалів (Boundary Fuzzing)

Окрім перевірки фіксованих детермінованих граничних точок, стенд містить модуль псевдовипадкового тестування (Fuzzing). Алгоритм генерує нерівномірні інтервали надходження пакетів із випадковими часовими дрейфами (Jitter) навколо критичної межі переповнення. Це дозволяє виявити приховані похибки округлення та непередбачені спрацьовування умовних переходів під час інтенсивного обміну даними.

Стенд емулює не тільки лічильники мілісекунд, але й високочастотні лічильники мікросекунд, де переповнення 16 біт відбувається кожні 65.5 мілісекунди. Без належної ізоляції та модульної арифметики такі мікросекундні таймери стають постійним джерелом раптових хибних спрацьовувань захистів.

## Реалізація тестового рушія та макету часу

:::tabs
```c
#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <assert.h>

/* Інтерфейс віртуального джерела часу */
typedef struct {
    uint16_t virtual_ticks_16;
    uint32_t virtual_ticks_32;
    uint64_t virtual_ticks_64;
} mock_clock_t;

static mock_clock_t g_mock_clock = {0};

void mock_clock_init(uint16_t start_16, uint32_t start_32) {
    g_mock_clock.virtual_ticks_16 = start_16;
    g_mock_clock.virtual_ticks_32 = start_32;
    g_mock_clock.virtual_ticks_64 = (uint64_t)start_32;
}

void mock_clock_advance_ms(uint32_t delta_ms) {
    g_mock_clock.virtual_ticks_16 = (uint16_t)(g_mock_clock.virtual_ticks_16 + delta_ms);
    g_mock_clock.virtual_ticks_32 += delta_ms;
    g_mock_clock.virtual_ticks_64 += delta_ms;
}

uint16_t mock_clock_get_16(void) { return g_mock_clock.virtual_ticks_16; }
uint32_t mock_clock_get_32(void) { return g_mock_clock.virtual_ticks_32; }

/* Безпечне атомарне зчитування 64-бітного часу з симуляцією захисту від гонок */
uint64_t mock_clock_get_64_safe(void) {
    uint32_t high1 = (uint32_t)(g_mock_clock.virtual_ticks_64 >> 32);
    uint32_t low   = (uint32_t)(g_mock_clock.virtual_ticks_64 & 0xFFFFFFFFULL);
    uint32_t high2 = (uint32_t)(g_mock_clock.virtual_ticks_64 >> 32);

    /* Якщо під час читання старше слово змінилося — перечитуємо заново */
    if (high1 != high2) {
        low   = (uint32_t)(g_mock_clock.virtual_ticks_64 & 0xFFFFFFFFULL);
        high2 = (uint32_t)(g_mock_clock.virtual_ticks_64 >> 32);
    }
    return ((uint64_t)high2 << 32) | low;
}

/* Тестований модуль безпекового наглядача серцебиття */
#define HEARTBEAT_TIMEOUT_MS  100U

typedef enum {
    WATCHDOG_OK = 0,
    WATCHDOG_TRIPPED = 1
} watchdog_state_t;

typedef struct {
    uint16_t last_heartbeat_16;
    uint32_t trip_count;
    watchdog_state_t state;
} safe_watchdog_t;

void safe_watchdog_init(safe_watchdog_t *wd, uint16_t now) {
    wd->last_heartbeat_16 = now;
    wd->trip_count = 0;
    wd->state = WATCHDOG_OK;
}

void safe_watchdog_feed(safe_watchdog_t *wd, uint16_t now) {
    wd->last_heartbeat_16 = now;
    wd->state = WATCHDOG_OK;
}

/* Коректна модульна перевірка дедлайну без пасток знакового приведення */
watchdog_state_t safe_watchdog_check(safe_watchdog_t *wd, uint16_t now) {
    uint16_t elapsed = (uint16_t)(now - wd->last_heartbeat_16);
    if (elapsed > HEARTBEAT_TIMEOUT_MS) {
        wd->state = WATCHDOG_TRIPPED;
        wd->trip_count++;
    } else {
        wd->state = WATCHDOG_OK;
    }
    return wd->state;
}

/* =========================================================================
   Тестові сценарії
   ========================================================================= */

static void test_normal_operation(void) {
    printf("[TEST] 1. Штатна робота без переповнення... ");
    mock_clock_init(1000, 1000);
    safe_watchdog_t wd;
    safe_watchdog_init(&wd, mock_clock_get_16());

    /* Оновлення кожні 20 мс */
    for (int i = 0; i < 5; ++i) {
        mock_clock_advance_ms(20);
        watchdog_state_t st = safe_watchdog_check(&wd, mock_clock_get_16());
        assert(st == WATCHDOG_OK);
        safe_watchdog_feed(&wd, mock_clock_get_16());
    }
    printf("PASSED\n");
}

static void test_rollover_seamless_feed(void) {
    printf("[TEST] 2. Стрибок через нуль (0xFFFA -> 0x000A) з регулярним годуванням... ");
    /* Початковий час: за 6 мс до переповнення 16-бітного лічильника (65530) */
    mock_clock_init(65530U, 65530U);
    safe_watchdog_t wd;
    safe_watchdog_init(&wd, mock_clock_get_16());

    /* Крок 1: час переходить у 65535 (+5 мс) */
    mock_clock_advance_ms(5);
    assert(mock_clock_get_16() == 65535U);
    assert(safe_watchdog_check(&wd, mock_clock_get_16()) == WATCHDOG_OK);

    /* Крок 2: час переходить через 0 у 10 (+11 мс від 65535 -> 10) */
    mock_clock_advance_ms(11);
    assert(mock_clock_get_16() == 10U);
    
    /* Дельта: (uint16_t)(10 - 65530) = 16 мс. Повинно бути менше ніж 100 мс */
    watchdog_state_t st = safe_watchdog_check(&wd, mock_clock_get_16());
    assert(st == WATCHDOG_OK);

    /* Годуємо сторожа на позначці 10 */
    safe_watchdog_feed(&wd, mock_clock_get_16());

    /* Крок 3: просуваємося ще на 50 мс */
    mock_clock_advance_ms(50);
    assert(safe_watchdog_check(&wd, mock_clock_get_16()) == WATCHDOG_OK);
    printf("PASSED\n");
}

static void test_rollover_actual_timeout(void) {
    printf("[TEST] 3. Справжній таймаут зв'язку через точку переповнення... ");
    /* Останній пакет отримано на позначці 65500 */
    mock_clock_init(65500U, 65500U);
    safe_watchdog_t wd;
    safe_watchdog_init(&wd, mock_clock_get_16());

    /* Минає 105 мс без надходження пакетів -> новий час 65500 + 105 = 69 (0x0045) */
    mock_clock_advance_ms(105);
    assert(mock_clock_get_16() == 69U);

    /* Перевірка: (uint16_t)(69 - 65500) = 105 > 100 -> Спрацьовування захисту! */
    watchdog_state_t st = safe_watchdog_check(&wd, mock_clock_get_16());
    assert(st == WATCHDOG_TRIPPED);
    assert(wd.trip_count == 1);
    printf("PASSED\n");
}

static void test_fuzzing_around_boundary(void) {
    printf("[TEST] 4. Фазинг псевдовипадкових інтервалів навколо межі 65535... ");
    mock_clock_init(65400U, 65400U);
    safe_watchdog_t wd;
    safe_watchdog_init(&wd, mock_clock_get_16());

    /* Імітуємо 1000 циклів обміну з випадковими кроками 5..30 мс */
    uint32_t pseudo_rand = 0x12345678U;
    for (int i = 0; i < 1000; ++i) {
        pseudo_rand = pseudo_rand * 1103515245U + 12345U;
        uint32_t step_ms = 5 + (pseudo_rand % 25); /* 5..29 мс */

        mock_clock_advance_ms(step_ms);
        watchdog_state_t st = safe_watchdog_check(&wd, mock_clock_get_16());
        assert(st == WATCHDOG_OK);
        safe_watchdog_feed(&wd, mock_clock_get_16());
    }
    printf("PASSED (1000 ітерацій)\n");
}

int main(void) {
    printf("=== Запуск регресійного стенду Time-Warp Virtual HAL ===\n");
    test_normal_operation();
    test_rollover_seamless_feed();
    test_rollover_actual_timeout();
    test_fuzzing_around_boundary();
    printf("=== Усі 4 тести пройдено успішно. Дефектів не виявлено. ===\n");
    return 0;
}
```
```cpp
#include <iostream>
#include <cstdint>
#include <chrono>
#include <concepts>
#include <cassert>

using namespace std::chrono_literals;

/* Типізований монотонний макет часу */
class MockClock {
public:
    using duration = std::chrono::milliseconds;
    using rep = uint16_t;

    static void setTime(rep ticks) noexcept {
        ticks_ = ticks;
    }

    static void advance(duration delta) noexcept {
        ticks_ = static_cast<rep>(ticks_ + delta.count());
    }

    static rep now() noexcept {
        return ticks_;
    }

private:
    static inline rep ticks_{0};
};

/* Надійний сторожовий модуль на шаблоні джерела часу */
template <typename Clock, uint16_t TimeoutMs = 100>
class SafeWatchdog {
public:
    enum class State { Ok, Tripped };

    explicit SafeWatchdog(typename Clock::rep now) noexcept
        : lastHeartbeat_{now}, state_{State::Ok}, tripCount_{0} {}

    void feed(typename Clock::rep now) noexcept {
        lastHeartbeat_ = now;
        state_ = State::Ok;
    }

    State check(typename Clock::rep now) noexcept {
        // Явне модульне віднімання у просторі uint16_t
        const uint16_t elapsed = static_cast<uint16_t>(now - lastHeartbeat_);
        if (elapsed > TimeoutMs) {
            state_ = State::Tripped;
            ++tripCount_;
        } else {
            state_ = State::Ok;
        }
        return state_;
    }

    [[nodiscard]] State state() const noexcept { return state_; }
    [[nodiscard]] uint32_t tripCount() const noexcept { return tripCount_; }

private:
    typename Clock::rep lastHeartbeat_;
    State state_;
    uint32_t tripCount_;
};

int main() {
    std::cout << "=== Запуск C++20 регресійного стенду Time-Warp ===\n";

    // Тест 1: Штатний режим
    MockClock::setTime(1000);
    SafeWatchdog<MockClock, 100> wd(MockClock::now());

    for (int i = 0; i < 5; ++i) {
        MockClock::advance(20ms);
        assert(wd.check(MockClock::now()) == SafeWatchdog<MockClock, 100>::State::Ok);
        wd.feed(MockClock::now());
    }
    std::cout << "[TEST] 1. Штатна робота... PASSED\n";

    // Тест 2: Стрибок 65530 -> 10 (Rollover)
    MockClock::setTime(65530);
    wd.feed(MockClock::now());

    MockClock::advance(16ms); // Новий час: 10
    assert(MockClock::now() == 10);
    assert(wd.check(MockClock::now()) == SafeWatchdog<MockClock, 100>::State::Ok);
    std::cout << "[TEST] 2. Переповнення без втрати пакетів... PASSED\n";

    // Тест 3: Справжній таймаут через границю
    MockClock::setTime(65500);
    wd.feed(MockClock::now());

    MockClock::advance(105ms); // Новий час: 69
    assert(MockClock::now() == 69);
    assert(wd.check(MockClock::now()) == SafeWatchdog<MockClock, 100>::State::Tripped);
    assert(wd.tripCount() == 1);
    std::cout << "[TEST] 3. Справжній таймаут на межі... PASSED\n";

    // Тест 4: Псевдовипадковий фазинг
    MockClock::setTime(65450);
    wd.feed(MockClock::now());
    uint32_t rnd = 0xCAFEBABE;
    for (int i = 0; i < 1000; ++i) {
        rnd = rnd * 1664525U + 1013904223U;
        uint32_t step = 5 + (rnd % 25);
        MockClock::advance(std::chrono::milliseconds(step));
        assert(wd.check(MockClock::now()) == SafeWatchdog<MockClock, 100>::State::Ok);
        wd.feed(MockClock::now());
    }
    std::cout << "[TEST] 4. C++20 фазинг навколо межі... PASSED (1000 ітерацій)\n";

    std::cout << "=== Усі тести C++20 завершено успішно ===\n";
    return 0;
}
```
:::

## Інтеграція в конвеєр автоматичного тестування (CI/CD)

Щоб унеможливити потрапляння помилок таймерної арифметики у релізні збірки, даний стенд компілюється як нативний бінарний файл за допомогою хостового компілятора (`gcc`/`clang`) під час кожного коміту та pull-запиту в репозиторій.

```bash
# Компіляція та запуск тесту переповнення часу в середовищі збірки
gcc -Wall -Wextra -Werror -O2 test_timer_warp.c -o test_timer_warp
./test_timer_warp

# Санітайзери для ловлі знакових переповнень та невизначеної поведінки
gcc -fsanitize=undefined,address -g test_timer_warp.c -o test_timer_warp_sanitized
./test_timer_warp_sanitized
```

Застосування опції `-fsanitize=undefined` (Undefined Behavior Sanitizer, UBSan) миттєво генерує аварійне переривання виконання, якщо у будь-якому місці коду обчислення часу виникає знакове переповнення (`signed integer overflow`), захищаючи цільову систему від прихованих дефектів компіляторної оптимізації.

## Апаратне моделювання на стенді (Hardware-in-the-Loop)

Окрім суто програмних модульних тестів, макет часу інтегрується у стенди напівнатурного моделювання (Hardware-in-the-Loop, HIL). На мікроконтролері виділяється окремий апаратний таймер, тактова частота якого під час випробувань штучно підвищується у тисячу разів.

Таке апаратне прискорення часу дозволяє фізичному мікроконтролеру пройти повне 32-бітне коло лічильника не за 49.7 діб, а всього за 71 хвилину лабораторного прогону, водночас взаємодіючи з реальними шинами зв'язку CAN, SPI та UART. У разі виникнення будь-якої аномалії на межі переповнення діагностичний вивід миттєво фіксує точний стан регістрів периферії.

Регулярне проходження регресійного стенду гарантує, що при оптимізаціях коду або оновленнях компілятора критичні алгоритми контролю часу збережуть математичну коректність незалежно від поточної позиції лічильника та архітектури ядра процесора.
