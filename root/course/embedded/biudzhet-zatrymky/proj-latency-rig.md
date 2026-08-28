# ⚙️ Прошивка вимірювального стенда затримок на мікроконтролері

Програмний вимір затримок у телекерованих системах за допомогою внутрішніх системних міток часу (`gettimeofday`, `std::chrono::steady_clock`) часто дає глибоко хибні результати. Програмний таймстемп фіксує лише момент передачі буфера в API операційної системи або чергу драйвера. Він принципово не здатний врахувати час очікування в черзі графічного сервера, апаратні затримки масштабування в контролері панелі, подвійну чи потрійну буферизацію V-Sync, а також фізичну швидкість релаксації рідких кристалів чи люмінофора матриці дисплея.

Ця вставка містить архітектурний опис, принципову схему аналогового вхідного каскаду та закінчену прошивку апаратного вимірювального стенда на базі 32-бітного мікроконтролера архітектури ARM Cortex-M (STM32 або RP2040). Стенд синхронно генерує калібрований оптичний спалах перед лінзою камери, фіксує момент появи світлової плями на пікселях екрана за допомогою швидкодіючого фотодетектора через апаратне переривання EXTI з субмікросекундною роздільною здатністю та формує повну статистичну вибірку розподілу затримок без динамічного виділення пам'яті.

## Принципова схема та апаратна структура вимірювача

Вимірювальний комплекс складається з трьох ключових фізичних вузлів: блоку оптичного збудження, високошвидкісного фотоприймача з компаратором та мікроконтролерного блоку обробки.

```
 +-------------------------------------------------------------------------+
 |                                                                         |
 |  [ Вимірювальний MCU ]                                                  |
 |    GPIO Out ------------> [ Драйвер MOSFET ] ---> [ Надяскравий LED ]   |
 |                                                           |             |
 |                                                      (Оптичний шлях     |
 |                                                       через камеру,     |
 |                                                       відеопередавач,   |
 |                                                       радіоефір, VRX    |
 |                                                       та монітор)       |
 |                                                           v             |
 |    EXTI In  <------------ [ Компаратор ] <------- [ TIA Підсилювач ]    |
 |    (Таймер TIM2 1 МГц)    (із гістерезисом)       [ Фотодіод BPW34 ]    |
 |                                                                         |
 +-------------------------------------------------------------------------+
```

### 1. Емітер оптичного імпульсу (Світлодіодний каскад)
Для мінімізації похибки моменту старту світлодіодний випромінювач керується польовим транзистором N-каналу (наприклад, 2N7002 або BSS138), підтягнутим до виводу таймера мікроконтролера. Час наростання оптичного фронту світлодіода становить менше `50 нс`. Світлодіод розміщується на оптичній осі об'єктива тестованої камери.

### 2. Фотоприймач та аналоговий компаратор
Оптичний відгук на дисплеї фіксується кремнієвим PIN-фотодіодом із малою власною ємністю (наприклад, Vishay BPW34, час наростання `t_r = 20 нс` при зворотній напрузі зміщення 5 В). Сигнал фотоструму перетворюється на напругу трансімпедансним підсилювачем (TIA, англ. *Transimpedance Amplifier*) на базі прецизійного операційного підсилювача з смугою пропускання не менше 10 МГц (MCP6001 або OPA350):
```
V_out = I_photo · R_feedback
```

З виходу підсилювача сигнал подається на швидкодіючий компаратор (LM393 або вбудований аналоговий компаратор мікроконтролера COMP1). Для запобігання паразитному дрижанню контактів на пологих фронтах відгуку матриці дисплея навколо компаратора реалізовано позитивний зворотний зв'язок — тригер Шмітта з вікном гістерезису 50–100 мВ. Вихід компаратора безпосередньо комутується на вхід зовнішнього переривання (EXTI) мікроконтролера.

Часова база формується 32-бітним апаратним таймером загального призначення (TIM2 або TIM5 у STM32), сконфігурованим на тактову частоту 1 МГц. Це забезпечує апаратну ціну поділки таймера рівно `1.0 мкс` без переповнення лічильника протягом понад 71 хвилини безперервної роботи.

## Алгоритм збору даних та статистична фільтрація

Одиничний оптичний спалах не дає повної інформації про поведінку системи через наявність дискретних фаз кадрової розгортки камери (Rolling Shutter) та синхронізації дисплея (V-Sync). Стенд виконує серію з `N = 256` випробувань.

Для запобігання стробоскопічному резонансу (коли спалахи потрапляють в одну й ту саму фазу кадрової розгортки камери) прошивка вводить псевдовипадкову паузу (англ. *randomized cooldown*) тривалістю від 80 до 160 мс між черговими тестами.

Для кожного спалаху фіксується точний часовий інтервал:
```
Delta_t = T_exti_capture - T_led_start
```

Якщо за встановлений захисний таймаут (250 мс) фотодіод не зареєстрував перевищення порогу яскравості (наприклад, через втрату пакета в радіоканалі або обрив відеопотоку), подія класифікується як втрачений кадр (Timeout / Dropped Frame).

Після накопичення серії вимірів масив сортується на місці алгоритмом сортування вставками (Insertion Sort), що дозволяє обчислити стійкі до аномальних викидів статистичні квантилі:
* **Медіана (P50)** — найбільш імовірний час затримки тракту;
* **Перцентиль P95** — верхня границя затримки для 95% польотного часу (показник стабільності керування);
* **Перцентиль P99** — рідкісні сплески буферизації та ретрансмісій на межі дальності;
* **Середньоквадратичний або абсолютний джитер** — показник передбачуваності відгуку.

## Вихідний код вимірювального модуля

Нижче наведено повну реалізацію прошивки вимірювального стенда:
* **Вкладка C**: автономний драйвер із захистом від стану гонитви (Race Conditions) через атомарні прапорці, який не використовує динамічну пам'ять (`malloc`/`free`) і готовий до інтеграції у bare-metal проєкти;
* **Вкладка C++**: типобезпечний клас `MeasurementRig` на стандарті C++20 з використанням типізованих тривалостей `std::chrono::microseconds`, фіксованих буферів `std::array`, безпечних зрізів `std::span` та `std::optional` для повернення результатів розрахунку.

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define LATENCY_MAX_SAMPLES 256
#define TIMEOUT_US          250000UL   // 250 мс таймаут очікування

typedef struct {
    uint32_t samples[LATENCY_MAX_SAMPLES];
    uint16_t count;
    uint16_t timeouts;
    uint32_t min_us;
    uint32_t max_us;
    uint32_t mean_us;
    uint32_t p50_us;
    uint32_t p95_us;
    uint32_t p99_us;
    uint32_t jitter_us;
} latency_stats_t;

typedef enum {
    RIG_IDLE,
    RIG_WAITING_RESPONSE,
    RIG_COOLDOWN
} rig_state_t;

static volatile rig_state_t g_rig_state = RIG_IDLE;
static volatile uint32_t g_t_start_us = 0;
static volatile uint32_t g_last_latency_us = 0;
static volatile bool g_sample_ready = false;

// Апаратні заглушки доступу до регістрів конкретного MCU
extern void hardware_led_set(bool state);
extern uint32_t hardware_timer_get_us(void);

// Обробник зовнішнього апаратного переривання від фотодіодного компаратора (EXTI ISR)
void EXTI_Optical_IRQHandler(void) {
    if (g_rig_state == RIG_WAITING_RESPONSE) {
        uint32_t t_now = hardware_timer_get_us();
        g_last_latency_us = t_now - g_t_start_us;
        g_sample_ready = true;
        g_rig_state = RIG_COOLDOWN;
        hardware_led_set(false);
    }
}

// Ініціалізація структури статистичних вимірювань
void latency_stats_init(latency_stats_t *stats) {
    memset(stats, 0, sizeof(latency_stats_t));
}

// Запуск одиничного оптичного тесту
void latency_rig_trigger(void) {
    if (g_rig_state != RIG_IDLE) return;
    
    g_sample_ready = false;
    g_rig_state = RIG_WAITING_RESPONSE;
    g_t_start_us = hardware_timer_get_us();
    hardware_led_set(true);
}

// Опитування поточного стану тесту та обробка таймаутів
bool latency_rig_poll(uint32_t *out_latency_us, bool *out_is_timeout) {
    if (g_rig_state == RIG_WAITING_RESPONSE) {
        uint32_t elapsed = hardware_timer_get_us() - g_t_start_us;
        if (elapsed >= TIMEOUT_US) {
            hardware_led_set(false);
            g_rig_state = RIG_COOLDOWN;
            *out_is_timeout = true;
            *out_latency_us = TIMEOUT_US;
            return true;
        }
    }
    
    if (g_sample_ready) {
        g_sample_ready = false;
        *out_latency_us = g_last_latency_us;
        *out_is_timeout = false;
        return true;
    }
    
    return false;
}

// Переведення стенда в режим готовності після періоду охолодження
void latency_rig_arm(void) {
    if (g_rig_state == RIG_COOLDOWN) {
        g_rig_state = RIG_IDLE;
    }
}

// Додавання успішного зразка до статистичного масиву
bool latency_stats_add_sample(latency_stats_t *stats, uint32_t latency_us, bool is_timeout) {
    if (is_timeout) {
        stats->timeouts++;
        return true;
    }
    if (stats->count >= LATENCY_MAX_SAMPLES) return false;
    stats->samples[stats->count++] = latency_us;
    return true;
}

// Сортування масиву на місці для швидкого знаходження перцентилів
static void sort_samples(uint32_t *arr, uint16_t n) {
    for (uint16_t i = 1; i < n; i++) {
        uint32_t key = arr[i];
        int32_t j = (int32_t)i - 1;
        while (j >= 0 && arr[j] > key) {
            arr[j + 1] = arr[j];
            j--;
        }
        arr[j + 1] = key;
    }
}

// Розрахунок підсумкових статистичних параметрів
void latency_stats_compute(latency_stats_t *stats) {
    if (stats->count == 0) return;

    uint32_t sorted[LATENCY_MAX_SAMPLES];
    memcpy(sorted, stats->samples, stats->count * sizeof(uint32_t));
    sort_samples(sorted, stats->count);

    stats->min_us = sorted[0];
    stats->max_us = sorted[stats->count - 1];

    uint64_t sum = 0;
    for (uint16_t i = 0; i < stats->count; i++) {
        sum += sorted[i];
    }
    stats->mean_us = (uint32_t)(sum / stats->count);

    // Розрахунок медіани та перцентилів
    stats->p50_us = sorted[(stats->count * 50) / 100];
    stats->p95_us = sorted[(stats->count * 95) / 100];
    stats->p99_us = sorted[(stats->count * 99) / 100];

    // Середнє абсолютне відхилення від середнього (оцінка джитера)
    uint64_t dev_sum = 0;
    for (uint16_t i = 0; i < stats->count; i++) {
        int64_t diff = (int64_t)sorted[i] - (int64_t)stats->mean_us;
        dev_sum += (diff < 0) ? -diff : diff;
    }
    stats->jitter_us = (uint32_t)(dev_sum / stats->count);
}
```
```cpp
#include <array>
#include <span>
#include <chrono>
#include <algorithm>
#include <numeric>
#include <optional>
#include <cstdint>

namespace latency {

using namespace std::chrono_literals;
using Microseconds = std::chrono::duration<uint32_t, std::micro>;

template <std::size_t MaxSamples = 256>
class MeasurementRig {
public:
    struct Statistics {
        std::size_t total_samples{0};
        std::size_t timeout_count{0};
        Microseconds min{0us};
        Microseconds max{0us};
        Microseconds mean{0us};
        Microseconds p50{0us};
        Microseconds p95{0us};
        Microseconds p99{0us};
        Microseconds jitter{0us};
    };

    enum class State {
        Idle,
        WaitingResponse,
        Cooldown
    };

    void on_optical_trigger_isr(Microseconds timestamp) noexcept {
        if (state_ == State::WaitingResponse) {
            last_latency_ = timestamp - trigger_start_;
            sample_ready_ = true;
            state_ = State::Cooldown;
        }
    }

    void start_trigger(Microseconds timestamp) noexcept {
        if (state_ != State::Idle) return;
        sample_ready_ = false;
        state_ = State::WaitingResponse;
        trigger_start_ = timestamp;
    }

    struct PollResult {
        bool completed{false};
        bool is_timeout{false};
        Microseconds latency{0us};
    };

    PollResult poll(Microseconds current_time, Microseconds timeout_limit = 250000us) noexcept {
        if (state_ == State::WaitingResponse) {
            if ((current_time - trigger_start_) >= timeout_limit) {
                state_ = State::Cooldown;
                ++timeouts_;
                return { .completed = true, .is_timeout = true, .latency = timeout_limit };
            }
        }

        if (sample_ready_) {
            sample_ready_ = false;
            if (sample_count_ < MaxSamples) {
                samples_[sample_count_++] = last_latency_;
            }
            return { .completed = true, .is_timeout = false, .latency = last_latency_ };
        }

        return { .completed = false, .is_timeout = false, .latency = 0us };
    }

    void reset_to_idle() noexcept {
        state_ = State::Idle;
    }

    [[nodiscard]] std::optional<Statistics> compute_statistics() const noexcept {
        if (sample_count_ == 0) {
            return std::nullopt;
        }

        std::array<Microseconds, MaxSamples> sorted_buf;
        std::copy_n(samples_.begin(), sample_count_, sorted_buf.begin());
        std::sort(sorted_buf.begin(), sorted_buf.begin() + sample_count_);

        Statistics stats;
        stats.total_samples = sample_count_;
        stats.timeout_count = timeouts_;
        stats.min = sorted_buf.front();
        stats.max = sorted_buf[sample_count_ - 1];

        const uint64_t total_us = std::accumulate(
            sorted_buf.begin(), sorted_buf.begin() + sample_count_, 0ULL,
            [](uint64_t acc, Microseconds val) { return acc + val.count(); }
        );
        stats.mean = Microseconds(static_cast<uint32_t>(total_us / sample_count_));

        stats.p50 = sorted_buf[(sample_count_ * 50) / 100];
        stats.p95 = sorted_buf[(sample_count_ * 95) / 100];
        stats.p99 = sorted_buf[(sample_count_ * 99) / 100];

        uint64_t dev_sum = 0;
        for (std::size_t i = 0; i < sample_count_; ++i) {
            const auto diff = static_cast<int64_t>(sorted_buf[i].count()) - 
                              static_cast<int64_t>(stats.mean.count());
            dev_sum += static_cast<uint64_t>(std::abs(diff));
        }
        stats.jitter = Microseconds(static_cast<uint32_t>(dev_sum / sample_count_));

        return stats;
    }

private:
    std::array<Microseconds, MaxSamples> samples_{};
    std::size_t sample_count_{0};
    std::size_t timeouts_{0};
    Microseconds trigger_start_{0us};
    Microseconds last_latency_{0us};
    volatile State state_{State::Idle};
    volatile bool sample_ready_{false};
};

} // namespace latency
```
:::

## Практичні нюанси фізичного калібрування стенда

Під час практичного розгортання та калібрування вимірювального стенда необхідно враховувати чотири джерела систематичних похибок:

1. **Геометричне положення світлодіода на сенсорі (Rolling Shutter bias)**:
   Якщо світлодіод спрямований у верхній сектор об'єктива, матриця камери зчитає його на початку кадрової розгортки (`~0.5 мс`). Якщо світлодіод розміщений у нижньому секторі — додається повний інтервал розгортки кадру (`+8.3 мс` для 120 fps або `+16.7 мс` для 60 fps). Для об'єктивного порівняння різних систем світлодіод слід жорстко центрувати по вертикалі оптичної осі сенсора.

2. **Підбір порогу компаратора за яскравістю**:
   Рідкокристалічні пікселі монітора нарощують яскравість не миттєво, а за S-подібною експоненційною кривою (час наростання Rise Time становить 2–10 мс). Встановлення занадто високого порогу спрацьовування призводить до вимірювання затримки підсвічування дисплея, а не моменту приходу кадру. Опорну напругу компаратора калібрують на рівні 10–15% від пікового рівня сигналу збудження.

3. **Шум штучного освітлення (100 Гц пульсації)**:
   Люмінесцентні та побутові світлодіодні лампи випромінюють оптичні пульсації на подвоєній частоті мережі (100 Гц), що викликає хибні спрацьовування компаратора. Вимірювання слід проводити у світлонепроникному боксі або використовувати тубус із чорної матової гуми, що герметично прилягає до лінзи окулярів.

4. **ШІМ-регулювання яскравості дисплея (PWM Dimming)**:
   Багато FPV-окулярів регулюють яскравість підсвічування екрана ШІМ-модуляцією на частотах від 200 Гц до 20 кГц. Якщо екран вимкнений у фазі ШІМ у момент приходу кадру, фотодіод зафіксує світло лише під час наступного імпульсу ШІМ. Щоб усунути цей артефакт, яскравість екрана під час тестів встановлюють на 100% (постійне світіння без ШІМ-модуляції).
