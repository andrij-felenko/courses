# 📋 Інтерфейс шейпера трафіку: Token Bucket Shaper API

Управління навантаженням на вході в мережу (Traffic Shaping та Traffic Policing) вимагає суворого дотримання узгодженого профілю трафіку (Traffic Contract). Шейпер трафіку на основі алгоритму жетонного відра (Token Bucket Shaper) призначений для згладжування сплесків інтенсивності (Burst Smoothing) і гарантування того, що середній потік даних не перевищує узгоджену норму `CIR` (Committed Information Rate), дозволяючи при цьому контрольовані короткочасні сплески обсягом до `CBS` (Committed Burst Size).

При фундаментальному порівнянні двох підходів до обмеження навантаження — Token Bucket та Leaky Bucket — проявляються принципові відмінності у обробці сплесків:
- **Leaky Bucket (Діряве відро):** вихідний потік формується із суворо фіксованою швидкістю. Пакети надходять у буферне відро і "витікають" через вузький отвір зі сталою швидкістю. Якщо вхідний сплеск перевищує місткість відра, надлишкові пакети відкидаються. Це гарантує абсолютно рівномірний трафік без жодних сплесків на виході.
- **Token Bucket (Жетонне відро):** у відро з визначеною місткістю `CBS` регулярно «капають» жетони зі швидкістю `CIR`. Пакет розміром `S` байт може проскочити мережевий інтерфейс миттєво без жодної затримки, якщо у відрі накопичено щонайменше `S` жетонів. Якщо жетонів недостатньо, пакет затримується у буфері (режим Shaping) або відкидається (режим Policing). Це дозволяє передавати пакунки сплесками з максимальною фізичною швидкістю середовища, зберігаючи обмеження на середню швидкість у довгостроковій перспективі.

---

## 1. Концептуальна модель та математичні рівняння

Алгоритм Token Bucket оперує двома основними параметрами:
1. `CIR` (Committed Information Rate): середня дозволена швидкість проходження даних у байтах за секунду (або бітах за секунду).
2. `CBS` (Committed Burst Size): максимальна ємність жетонного відра у байтах, що визначає найбільший дозволений сплеск трафіку.

Нехай `T(t)` позначає кількість жетонів (виміряну в байтах), наявну у відрі в момент часу `t`. Динаміка оновлення жетонів між двома послідовними подіями обробки пакетів у моменти `t_prev` та `t_curr` описується рівнянням:

```
T(t_curr) = min( CBS,  T(t_prev) + CIR · (t_curr - t_prev) )
```

Коли у момент `t_curr` надходить пакет розміром `L` байт, виконується перевірка умови допустимості:

```
Якщо T(t_curr) ≥ L:
    Пакет відправляється негайно
    T(t_curr) := T(t_curr) - L
Інакше:
    Дія залежить від обраного режиму (Shaping / Policing / Marking)
```

Врахування проміжного часу затримки `Δt = (L - T(t_curr)) / CIR` дозволяє обчислити точний час у мікросекундах, через який у відрі накопичиться необхідна кількість жетонів для відправки затриманого пакета.

---

## 2. Специфікація типів даних та конфігураційних структур

### Коди результатів обробки (`ShaperResult`)

Розроблюваний інтерфейс повертає точний статус для кожного переданого пакета, що дозволяє мережевому стеку приймати рішення про повторну постановку в чергу або сповіщення вищих рівнів.

:::tabs
```c
#define SHAPER_OK                   0   // Пакет успішно прийнято та відправлено
#define SHAPER_QUEUED               1   // Пакет затримано у буферній черзі
#define SHAPER_DROP_FULL            -1  // Пакет відкинуто через переповнення буфера
#define SHAPER_DROP_POLICED         -2  // Пакет відкинуто у режимі полісера
#define SHAPER_ERR_INVALID_PARAM    -3  // Некоректні параметри конфігурації
```
```cpp
enum class ShaperResult {
    Ok = 0,
    Queued = 1,
    DropFull = -1,
    DropPolicing = -2,
    ErrInvalidParam = -3
};
```
:::

### Режими роботи шейпера (`shaper_mode_t`)

Інтерфейс підтримує три класичні режими обмеження навантаження:

1. `SHAPER_MODE_SHAPE`: режим формувача трафіку. При нестачі жетонів пакет зберігається у внутрішній буферній черзі `max_queue_bytes`. Таймер системного драйвера викликає повторну спробу передачі через обчислений інтервал `wait_time_us`.
2. `SHAPER_MODE_POLICE`: режим полісера трафіку. При вичерпанні жетонів надлишковий пакет негайно відкидається без використання буферної пам'яті. Застосовується на вхідних портах провайдерів для захисту від зловмисного перевищення смуги.
3. `SHAPER_MODE_MARK`: режим триколірного маркування (RFC 2697 srTCM / RFC 2698 trTCM). Пакети, які виходять за межі `CBS`, не відкидаються, а маркуються встановленням прапорців ECN (Explicit Congestion Notification) у заголовку IP або зниженням пріоритету DSCP (Assured Forwarding Drop Precedence).

### Структура конфігурації

:::tabs
```c
typedef struct {
    uint64_t cir_bytes_per_sec; // Базова швидкість (Committed Information Rate, B/s)
    uint64_t cbs_bytes;          // Максимальний сплеск (Committed Burst Size, Bytes)
    uint64_t pir_bytes_per_sec; // Пікова швидкість (Peak Information Rate, optional)
    uint64_t ebs_bytes;          // Додатковий сплеск (Excess Burst Size, Bytes)
    size_t   max_queue_bytes;    // Максимальний розмір внутрішнього буфера
    uint8_t  mode;               // Режим роботи (SHAPER_MODE_SHAPE / POLICE / MARK)
} shaper_config_t;
```
```cpp
struct ShaperConfig {
    std::uint64_t cir_bytes_per_sec;
    std::uint64_t cbs_bytes;
    std::uint64_t pir_bytes_per_sec{0};
    std::uint64_t ebs_bytes{0};
    std::size_t max_queue_bytes{64 * 1024};
    ShaperMode mode{ShaperMode::Shape};
};
```
:::

---

## 3. Публічний інтерфейс та заголовні файли (C та C++)

Нижче наведено повну специфікацію API для мов C та C++. Декларації розроблені з урахуванням сумісності з розпаралеленими мережевими стеками.

:::tabs
```c
#ifndef TRAFFIC_SHAPER_H
#define TRAFFIC_SHAPER_H

#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef struct shaper_internal shaper_t;

/**
 * Створення та ініціалізація нового екземпляра Token Bucket Shaper.
 * 
 * @param config Вказівник на структуру конфігурації.
 * @return Вказівник на створений екземпляр або NULL при помилці.
 */
shaper_t* shaper_create(const shaper_config_t *config);

/**
 * Звільнення пам'яті та ресурсів шейпера.
 */
void shaper_destroy(shaper_t *shaper);

/**
 * Перераховує баланс жетонів на основі поточного таймера високої точності.
 * 
 * @param shaper Екземпляр шейпера.
 * @param now_us Поточний час у мікросекундах.
 */
void shaper_update_tokens(shaper_t *shaper, uint64_t now_us);

/**
 * Головний метод обробки пакету.
 * 
 * @param shaper Екземпляр шейпера.
 * @param packet_len_bytes Довжина вхідного пакета у байтах.
 * @param now_us Поточний час у мікросекундах.
 * @return Код результату (SHAPER_OK, SHAPER_QUEUED, SHAPER_DROP_*).
 */
int shaper_process_packet(shaper_t *shaper, size_t packet_len_bytes, uint64_t now_us);

/**
 * Обчислює час затримки у мікросекундах, необхідний для накопичення жетонів під пакет.
 */
uint64_t shaper_get_wait_time_us(const shaper_t *shaper, size_t packet_len_bytes, uint64_t now_us);

/**
 * Повертає поточний баланс жетонів (у байтах).
 */
uint64_t shaper_get_tokens(const shaper_t *shaper);

#ifdef __cplusplus
}
#endif

#endif // TRAFFIC_SHAPER_H
```
```cpp
#ifndef TRAFFIC_SHAPER_HPP
#define TRAFFIC_SHAPER_HPP

#include <cstdint>
#include <cstddef>
#include <vector>
#include <chrono>
#include <optional>
#include <stdexcept>

enum class ShaperMode {
    Shape,
    Police,
    Mark
};

enum class ShaperResult {
    Ok,
    Queued,
    DropFull,
    DropPolicing
};

struct ShaperConfig {
    std::uint64_t cir_bytes_per_sec;
    std::uint64_t cbs_bytes;
    std::size_t max_queue_bytes{64 * 1024};
    ShaperMode mode{ShaperMode::Shape};
};

class TokenBucketShaper {
public:
    explicit TokenBucketShaper(const ShaperConfig& config)
        : config_(config),
          tokens_bytes_(static_cast<double>(config.cbs_bytes)),
          current_queue_bytes_(0),
          last_update_us_(0) {
        if (config.cir_bytes_per_sec == 0 || config.cbs_bytes == 0) {
            throw std::invalid_argument("CIR та CBS повинні бути більше 0");
        }
    }

    void update_tokens(std::uint64_t now_us) {
        if (last_update_us_ == 0) {
            last_update_us_ = now_us;
            return;
        }

        std::uint64_t elapsed_us = now_us - last_update_us_;
        last_update_us_ = now_us;

        double added_tokens = (static_cast<double>(elapsed_us) * config_.cir_bytes_per_sec) / 1000000.0;
        tokens_bytes_ += added_tokens;

        if (tokens_bytes_ > static_cast<double>(config_.cbs_bytes)) {
            tokens_bytes_ = static_cast<double>(config_.cbs_bytes);
        }
    }

    ShaperResult process_packet(std::size_t packet_len_bytes, std::uint64_t now_us) {
        update_tokens(now_us);

        double len = static_cast<double>(packet_len_bytes);

        if (tokens_bytes_ >= len) {
            tokens_bytes_ -= len;
            return ShaperResult::Ok;
        }

        if (config_.mode == ShaperMode::Police) {
            return ShaperResult::DropPolicing;
        }

        if (current_queue_bytes_ + packet_len_bytes > config_.max_queue_bytes) {
            return ShaperResult::DropFull;
        }

        current_queue_bytes_ += packet_len_bytes;
        return ShaperResult::Queued;
    }

    std::uint64_t get_wait_time_us(std::size_t packet_len_bytes, std::uint64_t now_us) {
        update_tokens(now_us);

        if (tokens_bytes_ >= static_cast<double>(packet_len_bytes)) {
            return 0;
        }

        double needed = static_cast<double>(packet_len_bytes) - tokens_bytes_;
        double wait_seconds = needed / static_cast<double>(config_.cir_bytes_per_sec);
        return static_cast<std::uint64_t>(wait_seconds * 1000000.0);
    }

    double get_tokens() const noexcept {
        return tokens_bytes_;
    }

private:
    ShaperConfig config_;
    double tokens_bytes_;
    std::size_t current_queue_bytes_;
    std::uint64_t last_update_us_;
};

#endif // TRAFFIC_SHAPER_HPP
```
:::

---

## 4. Повний робочий код реалізації на C та C++

Наведені нижче реалізації включають симуляцію вхідного трафіку із перевіркою часових інтервалів у мікросекундах.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>

typedef struct {
    uint64_t cir_bytes_per_sec;
    uint64_t cbs_bytes;
    size_t max_queue_bytes;
} shaper_config_t;

typedef struct {
    shaper_config_t config;
    double tokens;
    size_t current_queue_bytes;
    uint64_t last_update_us;
} shaper_t;

shaper_t* shaper_create(const shaper_config_t *config) {
    if (!config || config->cir_bytes_per_sec == 0 || config->cbs_bytes == 0) {
        return NULL;
    }
    shaper_t *s = (shaper_t*)malloc(sizeof(shaper_t));
    if (!s) return NULL;

    s->config = *config;
    s->tokens = (double)config->cbs_bytes;
    s->current_queue_bytes = 0;
    s->last_update_us = 0;
    return s;
}

void shaper_destroy(shaper_t *s) {
    if (s) free(s);
}

void shaper_update_tokens(shaper_t *s, uint64_t now_us) {
    if (s->last_update_us == 0) {
        s->last_update_us = now_us;
        return;
    }
    uint64_t elapsed = now_us - s->last_update_us;
    s->last_update_us = now_us;

    double added = ((double)elapsed * (double)s->config.cir_bytes_per_sec) / 1000000.0;
    s->tokens += added;
    if (s->tokens > (double)s->config.cbs_bytes) {
        s->tokens = (double)s->config.cbs_bytes;
    }
}

int shaper_process_packet(shaper_t *s, size_t packet_len, uint64_t now_us) {
    shaper_update_tokens(s, now_us);

    double len = (double)packet_len;
    if (s->tokens >= len) {
        s->tokens -= len;
        return 0; // SHAPER_OK
    }

    if (s->current_queue_bytes + packet_len > s->config.max_queue_bytes) {
        return -1; // SHAPER_DROP_FULL
    }

    s->current_queue_bytes += packet_len;
    return 1; // SHAPER_QUEUED
}

int main(void) {
    shaper_config_t cfg = {
        .cir_bytes_per_sec = 100000, // 100 КБ/с
        .cbs_bytes = 10000,          // 10 КБ сплеск
        .max_queue_bytes = 50000
    };

    shaper_t *s = shaper_create(&cfg);
    if (!s) {
        printf("Помилка створення шейпера\n");
        return 1;
    }

    uint64_t time_us = 0;
    printf("Старт: Жетонів = %.0f B\n", s->tokens);

    // Відправляємо пакет 8000 B
    int res1 = shaper_process_packet(s, 8000, time_us);
    printf("Пакет 1 (8000 B): результат = %d, залишок жетонів = %.0f B\n", res1, s->tokens);

    // Відправляємо другий пакет 5000 B при нехватці жетонів
    int res2 = shaper_process_packet(s, 5000, time_us);
    printf("Пакет 2 (5000 B): результат = %d, залишок жетонів = %.0f B\n", res2, s->tokens);

    // Прокручуємо час на 50 мс (50000 мкс) -> додається 5000 B жетонів
    time_us += 50000;
    int res3 = shaper_process_packet(s, 5000, time_us);
    printf("Пакет 3 через 50 мс (5000 B): результат = %d, залишок жетонів = %.0f B\n", res3, s->tokens);

    shaper_destroy(s);
    return 0;
}
```
```cpp
#include <iostream>
#include <cstdint>
#include <memory>

int main() {
    ShaperConfig cfg;
    cfg.cir_bytes_per_sec = 100000; // 100 КБ/с
    cfg.cbs_bytes = 10000;          // 10 КБ
    cfg.max_queue_bytes = 50000;
    cfg.mode = ShaperMode::Shape;

    TokenBucketShaper shaper(cfg);

    std::uint64_t time_us = 0;
    std::cout << "Старт: Жетонів = " << shaper.get_tokens() << " B\n";

    auto r1 = shaper.process_packet(8000, time_us);
    std::cout << "Пакет 1 (8000 B): код = " << static_cast<int>(r1)
              << ", залишок = " << shaper.get_tokens() << " B\n";

    auto r2 = shaper.process_packet(5000, time_us);
    std::cout << "Пакет 2 (5000 B): код = " << static_cast<int>(r2)
              << ", залишок = " << shaper.get_tokens() << " B\n";

    time_us += 50000; // +50 мс
    auto r3 = shaper.process_packet(5000, time_us);
    std::cout << "Пакет 3 через 50 мс (5000 B): код = " << static_cast<int>(r3)
              << ", залишок = " << shaper.get_tokens() << " B\n";

    return 0;
}
```
:::

---

## 5. Крайові випадки, джиттер годинника та оптимізація продуктивності

При інтеграції шейпера у реальні мережеві драйвери або користувацькі мережеві стеки (наприклад, DPDK або io_uring) виникають наступні інженерні проблеми:

1. **Джиттер системного таймера (Timer Jitter):** виклики `shaper_update_tokens` залежать від точності системного годинника `clock_gettime(CLOCK_MONOTONIC)`. У високонавантажених системах дискретність квантів часу ОС (1–10 мс) може призводити до нерівномірного нарахування жетонів великими порціями. Для захисту від цього `CBS` має бути підібраний так, щоб вміщати щонайменше 2–3 максимальні сплески трафіку за період квантування таймера (`CBS ≥ CIR · Δt_quantum`).
2. **Переповнення при тривалих паузах (Long Idle Overflow):** якщо потік не надсилав даних тривалий час (наприклад, декілька годин), обчислення `elapsed_us * CIR` може викликати арифметичне переповнення 64-бітного цілого числа. Тому додавання жетонів затискається через верхню межу `CBS` одразу після розрахунку ділення.
3. **Багатопотокова синхронізація (Multi-threaded Lock Contention):** при обробці трафіку з кількох мережевих черг (NIC RSS queues) декількома ядрами процесора прямий доступ до єдиного об'єкта `shaper_t` через блоки засувок (Spinlock / Mutex) спричиняє вичерпання продуктивності (Cache Bouncing). Рекомендованою архітектурною альтернативою є використання окремого шейпера на кожну апаратну чергу RX/TX з пропорційним діленням загального `CIR`.
4. **Інтеграція з підсистемою Linux Traffic Control (tc):** у ядрах Linux Token Bucket Filter реалізовано у вигляді бек-енд дисципліни черг `qdisc tbf`. Налаштування виконується командою:
   ```bash
   tc qdisc add dev eth0 root tbf rate 100mbit burst 32k latency 40ms
   ```
   де `rate` відповідає `CIR`, `burst` — `CBS`, а `latency` визначає максимальний дозволений час перебування затриманого пакета у внутрішній черзі до його відкидання.

---

## 6. Дворежимне маркування та триколірні шейпери (srTCM / trTCM)

У високошвидкісних backbone-мережах та обладнанні з підтримкою QoS (Quality of Service) класичного однорежимного відра недостатньо для диференціації пріоритетів трафіку. Для цього стандартами RFC 2697 та RFC 2698 введено дворежимні (Dual Token Bucket) триколірні алгоритми:

1. **srTCM (Single Rate Three Color Marker, RFC 2697):** підтримує одне значення швидкості `CIR` і два розміри відер — `CBS` (Committed Burst Size) та `EBS` (Excess Burst Size).
   - Пакет маркується **зеленим (Green)**, якщо він вміщається у жетони відра `CBS`.
   - Пакет маркується **жовтим (Yellow)**, якщо жетонів у `CBS` бракує, але достатньо жетонів у відрі `EBS`.
   - Пакет маркується **червоним (Red)**, якщо жетонів немає у жодному відрі (такий пакет негайно відкидається).

2. **trTCM (Two Rate Three Color Marker, RFC 2698):** підтримує дві незалежні швидкості — базову `CIR` та пікову `PIR` (Peak Information Rate), а також дві ємності відер — `CBS` та `PBS` (Peak Burst Size).
   - Жетони у відро `PBS` надходять зі швидкістю `PIR`, а у відро `CBS` — зі швидкістю `CIR`.
   - Якщо пакет перевищує по поточній ємності відро `PBS`, він маркується червоним.
   - Якщо пакет вкладається у `PBS`, але перевищує `CBS`, він маркується жовтим.
   - Якщо пакет вкладається в обидва відра, він маркується зеленим.

Цей підхід дозволяє провайдерам гарантувати безумовну доставку зелених пакетів, пропускати жовті пакети при наявності вільної ємності мережі і першими відкидати їх під час наближення заторів.

---

## 7. Моніторинг, простеження та метрики продуктивності

Для спостереження за станом шейпера у реальному часі мережеві підсистеми надають інтерфейси простеження через `sysfs`, `procfs` та метрики Prometheus.

Ключові метрики моніторингу:
- `shaper_tokens_current_bytes`: поточний рівень жетонів у відрі (допомагає оцінити завантаженість каналу).
- `shaper_queued_packets_total`: лічильник пакетів, затриманих у черзі через брак жетонів.
- `shaper_dropped_packets_total`: лічильник відкинутих пакетів у режимі Policing або при переповненні буфера.
- `shaper_sojourn_time_seconds`: середня затримка перебування пакетів у внутрішньому буфері.

Приклад команди перегляду статистики шейпера в Linux:
```bash
tc -s -d qdisc show dev eth0
```
Вивід цієї команди надає інформацію про кількість переданих байтів, сплесків, втрат через вичерпання жетонів (`overlimits`) та затримок у черзі, що є основним інструментом для мережевого адміністрування та налагодження QoS.
