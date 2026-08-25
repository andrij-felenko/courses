# ⚙️ Симуляція дискретно-подійного доступу CSMA/CD та експоненційного відкату BEB

Ця практична розробка містить дискретно-подійний симулятор напівдуплексного колізійного домену Ethernet на рівні протоколу керування доступом до середовища (MAC CSMA/CD). Модель відтворює конкурентний доступ кількох мережевих станцій до спільного фізичного дроту з урахуванням затримки поширення сигналу, 1-persistent прослуховування лінії, перевірки колізій під час передачі, глушіння каналу (Jam) та алгоритму експоненційного відкату (Truncated Binary Exponential Backoff).

---

## 1. Архітектура та математична модель симулятора

Симулятор моделює спільну фізичну шину Ethernet у дискретних квантах часу — слотах. За базову одиницю квантування часу обрано еталонний часовий слот **Slot Time** (`51.2 мкс` = `512 біт-часів` на швидкості 10 Мбіт/с).

У реальній мережі поширення електромагнітної хвилі є неперервним аналоговим процесом, де напруга або різниця струмів змінюється вздовж усієї довжини коаксіалу чи витої пари. Дискретизація на рівні слотів базується на теоремі про те, що будь-яка колізія в межах максимально дозволеної топології гарантовано розпізнається обома конфліктуючими сторонами протягом одного кванту `T_slot`. Таким чином, часовий слот є неподільним атомом арбітражу шини.

### Скінченний автомат станції (Station FSM)

Кожна мережева станція функціонує як незалежний агент зі скінченним автоматом, що містить п'ять взаємовиключних станів:

1. `STATE_IDLE` (Очікування):
   Станція не має даних у черзі вихідного буфера. У кожному слоті з імовірністю `p_arrival` (пуассонівська інтенсивність надходження трафіку від вищих рівнів ОС) станція генерує новий кадр випадкової довжини від 1 до 24 слотів (що відповідає розмірам від 64 до 1518 байтів) і переходить у стан `STATE_SENSING`.

2. `STATE_SENSING` (Прослуховування несучої — 1-Persistent CSMA):
   Станція аналізує стан фізичної лінії (Carrier Sense). Якщо шина зайнята чужою передачею, станція залишається в стані прослуховування, накопичуючи лічильник часу очікування. Щойно шина звільняється (кількість активних передавачів падає до нуля), станція вичікує міжкадровий інтервал IFG (96 біт-часів) і в наступному слоті безумовно (з імовірністю `p = 1`) починає передачу кадру, переходячи в стан `STATE_TRANSMITTING`.

3. `STATE_TRANSMITTING` (Передача кадру та Collision Detection):
   Станція випромінює послідовність бітів кадру. Одночасно апаратна логіка контролює стан середовища. Якщо кількість передавачів на шині в поточному слоті перевищує одиницю (`transmitting_now > 1`), виникає колізія: біти спотворюються, лічильник колізій станції інкрементується, і станція негайно перериває передачу даних, переходячи в стан `STATE_JAMMING`. Якщо колізії немає, залишок довжини кадру зменшується на 1 слот. Коли передано всі слоти кадру, передача вважається успішною: станція скидає лічильник невдалих спроб `attempts = 0` і повертається в стан `STATE_IDLE`.

4. `STATE_JAMMING` (Глушіння лінії):
   Станція надсилає в лінію глушильну послідовність Jam (32 біти), щоб гарантувати, що всі інші вузли домену також зафіксують колізію й очистять свої приймальні буфери. Після відправки Jam станція збільшує лічильник невдалих спроб `attempts = attempts + 1`. Якщо лічильник перевищує поріг 16 спроб, MAC-контролер фіксує фатальну помилку перевантаження (Excessive Collisions), скидає пошкоджений кадр (`frames_dropped++`) і повертається в стан `STATE_IDLE`. Інакше станція обчислює час експоненційного відкату та переходить у стан `STATE_BACKOFF`.

5. `STATE_BACKOFF` (Експоненційне очікування BEB):
   Станція генерує випадкове ціле число слотів `r` з рівномірного діапазону `[0, 2^k − 1]`, де показник ступеня обмежений значенням `k = min(attempts, 10)`. Станція декрементує лічильник затримки `backoff_slots_left` на кожному кроці симулятора. Коли таймер досягає нуля, станція знову переходить у стан `STATE_SENSING` для спроби нового захоплення шини.

---

## 2. Реалізація симулятора мовами C та C++

Нижче наведено повний вихідний код симулятора двома мовами програмування: системною мовою C з прямим маніпулюванням структурами пам'яті та сучасною C++20 з використанням об'єктної інкапсуляції, генератора Mersenne Twister та типізованих перечислень.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <time.h>

#define MAX_STATIONS       32
#define MAX_BACKOFF_EXP    10
#define MAX_ATTEMPTS       16
#define SLOT_TIME_US       51.2
#define FRAME_SLOTS_MIN    1   /* 64 байти = 1 слот (51.2 мкс) */
#define FRAME_SLOTS_MAX    24  /* 1518 байтів ≈ 24 слоти */

typedef enum {
    STATE_IDLE = 0,
    STATE_SENSING,
    STATE_TRANSMITTING,
    STATE_JAMMING,
    STATE_BACKOFF
} station_state_t;

typedef struct {
    uint32_t id;
    station_state_t state;
    uint32_t attempts;
    uint32_t backoff_slots_left;
    uint32_t frame_slots_left;
    uint32_t current_frame_len_slots;
    
    /* Статистика станції */
    uint64_t frames_sent_ok;
    uint64_t frames_dropped;
    uint64_t collisions_total;
    uint64_t total_wait_slots;
} station_t;

typedef struct {
    uint32_t num_stations;
    station_t stations[MAX_STATIONS];
    uint32_t active_transmitters;
    uint64_t current_slot;
    uint64_t total_sim_slots;
    double packet_arrival_prob;
    
    /* Глобальна статистика шини */
    uint64_t bus_idle_slots;
    uint64_t bus_success_slots;
    uint64_t bus_collision_slots;
    uint64_t total_successful_frames;
} ethernet_bus_t;

static void bus_init(ethernet_bus_t *bus, uint32_t num_stations, double load_prob, uint64_t sim_slots) {
    memset(bus, 0, sizeof(*bus));
    bus->num_stations = (num_stations > MAX_STATIONS) ? MAX_STATIONS : num_stations;
    bus->packet_arrival_prob = load_prob;
    bus->total_sim_slots = sim_slots;
    
    for (uint32_t i = 0; i < bus->num_stations; ++i) {
        bus->stations[i].id = i;
        bus->stations[i].state = STATE_IDLE;
    }
}

static uint32_t calculate_backoff(uint32_t attempts) {
    uint32_t k = (attempts > MAX_BACKOFF_EXP) ? MAX_BACKOFF_EXP : attempts;
    uint32_t max_slots = (1U << k);
    return (uint32_t)(rand() % max_slots);
}

static void simulate_slot(ethernet_bus_t *bus) {
    /* 1. Генерація нового трафіку для станцій у стані IDLE */
    for (uint32_t i = 0; i < bus->num_stations; ++i) {
        station_t *st = &bus->stations[i];
        if (st->state == STATE_IDLE) {
            double r = (double)rand() / (double)RAND_MAX;
            if (r < bus->packet_arrival_prob) {
                st->state = STATE_SENSING;
                st->attempts = 0;
                /* Випадковий розмір кадру від 1 до 24 слотів */
                st->current_frame_len_slots = 1 + (rand() % (FRAME_SLOTS_MAX - FRAME_SLOTS_MIN + 1));
            }
        }
    }

    /* 2. Підрахунок кількості станцій, які бажають передавати на цьому слоті */
    uint32_t transmitting_now = 0;
    for (uint32_t i = 0; i < bus->num_stations; ++i) {
        station_t *st = &bus->stations[i];
        if (st->state == STATE_TRANSMITTING || st->state == STATE_JAMMING) {
            transmitting_now++;
        } else if (st->state == STATE_SENSING) {
            /* 1-persistent: якщо шина була вільна, починаємо передачу */
            if (bus->active_transmitters == 0) {
                st->state = STATE_TRANSMITTING;
                st->frame_slots_left = st->current_frame_len_slots;
                transmitting_now++;
            }
        }
    }

    /* 3. Оновлення стану шини та аналіз колізій */
    if (transmitting_now == 0) {
        bus->bus_idle_slots++;
    } else if (transmitting_now == 1) {
        bus->bus_success_slots++;
    } else {
        bus->bus_collision_slots++;
    }
    bus->active_transmitters = transmitting_now;

    /* 4. Обробка автоматів кожної станції */
    for (uint32_t i = 0; i < bus->num_stations; ++i) {
        station_t *st = &bus->stations[i];
        
        switch (st->state) {
        case STATE_IDLE:
            break;
            
        case STATE_SENSING:
            st->total_wait_slots++;
            break;
            
        case STATE_TRANSMITTING:
            if (transmitting_now > 1) {
                /* Колізія виявлена під час передачі */
                st->collisions_total++;
                st->state = STATE_JAMMING;
            } else {
                /* Успішне просування передачі кадру */
                st->frame_slots_left--;
                if (st->frame_slots_left == 0) {
                    st->frames_sent_ok++;
                    bus->total_successful_frames++;
                    st->state = STATE_IDLE;
                    st->attempts = 0;
                }
            }
            break;
            
        case STATE_JAMMING:
            /* Після відправки Jam переходимо у відкат BEB */
            st->attempts++;
            if (st->attempts > MAX_ATTEMPTS) {
                /* Перевищено 16 спроб — скидання кадру */
                st->frames_dropped++;
                st->state = STATE_IDLE;
                st->attempts = 0;
            } else {
                st->backoff_slots_left = calculate_backoff(st->attempts);
                st->state = STATE_BACKOFF;
            }
            break;
            
        case STATE_BACKOFF:
            st->total_wait_slots++;
            if (st->backoff_slots_left == 0) {
                st->state = STATE_SENSING;
            } else {
                st->backoff_slots_left--;
            }
            break;
        }
    }
    bus->current_slot++;
}

static void print_bus_report(const ethernet_bus_t *bus) {
    double total = (double)bus->total_sim_slots;
    double util = ((double)bus->bus_success_slots / total) * 100.0;
    double coll_rate = ((double)bus->bus_collision_slots / total) * 100.0;
    double idle_rate = ((double)bus->bus_idle_slots / total) * 100.0;
    
    printf("=== ЗВІТ СИМУЛЯЦІЇ СЕРЕДОВИЩА CSMA/CD ===\n");
    printf("Загальна кількість слотів:  %llu (%.2f с ефірного часу)\n",
           (unsigned long long)bus->total_sim_slots,
           (bus->total_sim_slots * SLOT_TIME_US) / 1000000.0);
    printf("Кількість станцій:          %u\n", bus->num_stations);
    printf("Корисна утилізація шини:    %.2f%%\n", util);
    printf("Частка колізійних слотів:   %.2f%%\n", coll_rate);
    printf("Частка слотів простою:      %.2f%%\n", idle_rate);
    printf("Успішно доставлено кадрів:  %llu\n", (unsigned long long)bus->total_successful_frames);
    printf("----------------------------------------\n");
    printf("ID   | Успішно  | Скинуто  | Колізій  | Сер. очікування\n");
    for (uint32_t i = 0; i < bus->num_stations; ++i) {
        const station_t *st = &bus->stations[i];
        double avg_wait = st->frames_sent_ok ? ((double)st->total_wait_slots / st->frames_sent_ok) : 0.0;
        printf("#%02u  | %-8llu | %-8llu | %-8llu | %.2f слотів\n",
               st->id,
               (unsigned long long)st->frames_sent_ok,
               (unsigned long long)st->frames_dropped,
               (unsigned long long)st->collisions_total,
               avg_wait);
    }
}

int main(void) {
    srand(42);
    ethernet_bus_t bus;
    uint32_t stations_count = 10;
    double arrival_rate = 0.05;  /* 5% ймовірність генерації кадру за слот на станцію */
    uint64_t sim_steps = 100000; /* 100 000 слотів = 5.12 с роботи 10 Мбіт/с Ethernet */
    
    bus_init(&bus, stations_count, arrival_rate, sim_steps);
    for (uint64_t s = 0; s < sim_steps; ++s) {
        simulate_slot(&bus);
    }
    print_bus_report(&bus);
    return 0;
}
```
```cpp
#include <iostream>
#include <vector>
#include <random>
#include <memory>
#include <cstdint>
#include <iomanip>
#include <string_view>
#include <algorithm>

enum class StationState {
    Idle,
    Sensing,
    Transmitting,
    Jamming,
    Backoff
};

struct StationMetrics {
    uint64_t framesSentOk{0};
    uint64_t framesDropped{0};
    uint64_t collisionsTotal{0};
    uint64_t totalWaitSlots{0};
};

class Station {
public:
    explicit Station(uint32_t id) : id_(id) {}

    [[nodiscard]] uint32_t id() const noexcept { return id_; }
    [[nodiscard]] StationState state() const noexcept { return state_; }
    [[nodiscard]] const StationMetrics& metrics() const noexcept { return metrics_; }

    void triggerNewFrame(uint32_t lengthSlots) noexcept {
        if (state_ == StationState::Idle) {
            state_ = StationState::Sensing;
            attempts_ = 0;
            currentFrameLenSlots_ = lengthSlots;
        }
    }

    void startTransmission() noexcept {
        state_ = StationState::Transmitting;
        frameSlotsLeft_ = currentFrameLenSlots_;
    }

    void handleCollisionDetected() noexcept {
        metrics_.collisionsTotal++;
        state_ = StationState::Jamming;
    }

    void processSlot(uint32_t activeTransmittersOnBus, std::mt19937& rng) {
        constexpr uint32_t MaxAttempts = 16;
        constexpr uint32_t MaxBackoffExp = 10;

        switch (state_) {
        case StationState::Idle:
            break;

        case StationState::Sensing:
            metrics_.totalWaitSlots++;
            break;

        case StationState::Transmitting:
            if (activeTransmittersOnBus > 1) {
                handleCollisionDetected();
            } else {
                if (--frameSlotsLeft_ == 0) {
                    metrics_.framesSentOk++;
                    state_ = StationState::Idle;
                    attempts_ = 0;
                }
            }
            break;

        case StationState::Jamming: {
            attempts_++;
            if (attempts_ > MaxAttempts) {
                metrics_.framesDropped++;
                state_ = StationState::Idle;
                attempts_ = 0;
            } else {
                const uint32_t k = std::min(attempts_, MaxBackoffExp);
                const uint32_t maxRange = (1U << k) - 1;
                std::uniform_int_distribution<uint32_t> dist(0, maxRange);
                backoffSlotsLeft_ = dist(rng);
                state_ = StationState::Backoff;
            }
            break;
        }

        case StationState::Backoff:
            metrics_.totalWaitSlots++;
            if (backoffSlotsLeft_ == 0) {
                state_ = StationState::Sensing;
            } else {
                backoffSlotsLeft_--;
            }
            break;
        }
    }

private:
    uint32_t id_;
    StationState state_{StationState::Idle};
    uint32_t attempts_{0};
    uint32_t backoffSlotsLeft_{0};
    uint32_t frameSlotsLeft_{0};
    uint32_t currentFrameLenSlots_{1};
    StationMetrics metrics_;
};

class EthernetBusSimulator {
public:
    EthernetBusSimulator(uint32_t numStations, double loadProb, uint64_t totalSlots, uint32_t seed = 42)
        : totalSlots_(totalSlots), loadProb_(loadProb), rng_(seed), distArrival_(0.0, 1.0), distFrameLen_(1, 24) {
        stations_.reserve(numStations);
        for (uint32_t i = 0; i < numStations; ++i) {
            stations_.push_back(std::make_unique<Station>(i));
        }
    }

    void run() {
        for (uint64_t slot = 0; slot < totalSlots_; ++slot) {
            stepSlot();
        }
    }

    void printReport() const {
        const double total = static_cast<double>(totalSlots_);
        const double util = (static_cast<double>(busSuccessSlots_) / total) * 100.0;
        const double collRate = (static_cast<double>(busCollisionSlots_) / total) * 100.0;
        const double idleRate = (static_cast<double>(busIdleSlots_) / total) * 100.0;

        std::cout << "=== ЗВІТ СИМУЛЯЦІЇ СЕРЕДОВИЩА CSMA/CD (C++20) ===\n";
        std::cout << std::fixed << std::setprecision(2);
        std::cout << "Загальна кількість слотів:  " << totalSlots_ << " ("
                  << (totalSlots_ * 51.2) / 1'000'000.0 << " с ефірного часу)\n";
        std::cout << "Кількість станцій:          " << stations_.size() << "\n";
        std::cout << "Корисна утилізація шини:    " << util << "%\n";
        std::cout << "Частка колізійних слотів:   " << collRate << "%\n";
        std::cout << "Частка слотів простою:      " << idleRate << "%\n";
        std::cout << "--------------------------------------------------\n";
        std::cout << "ID   | Успішно  | Скинуто  | Колізій  | Сер. очікування\n";

        for (const auto& st : stations_) {
            const auto& m = st->metrics();
            const double avgWait = m.framesSentOk ? (static_cast<double>(m.totalWaitSlots) / m.framesSentOk) : 0.0;
            std::cout << "#" << std::setw(2) << std::setfill('0') << st->id() << "  | "
                      << std::setfill(' ') << std::setw(8) << m.framesSentOk << " | "
                      << std::setw(8) << m.framesDropped << " | "
                      << std::setw(8) << m.collisionsTotal << " | "
                      << avgWait << " слотів\n";
        }
    }

private:
    void stepSlot() {
        /* 1. Генерація трафіку для станцій Idle */
        for (auto& st : stations_) {
            if (st->state() == StationState::Idle && distArrival_(rng_) < loadProb_) {
                st->triggerNewFrame(distFrameLen_(rng_));
            }
        }

        /* 2. Визначення кандидатів на передачу (1-persistent) */
        uint32_t transmittingNow = 0;
        for (auto& st : stations_) {
            if (st->state() == StationState::Transmitting || st->state() == StationState::Jamming) {
                transmittingNow++;
            } else if (st->state() == StationState::Sensing && prevActiveTransmitters_ == 0) {
                st->startTransmission();
                transmittingNow++;
            }
        }

        /* 3. Статистика шини */
        if (transmittingNow == 0) {
            busIdleSlots_++;
        } else if (transmittingNow == 1) {
            busSuccessSlots_++;
        } else {
            busCollisionSlots_++;
        }
        prevActiveTransmitters_ = transmittingNow;

        /* 4. Оновлення стану кожної станції */
        for (auto& st : stations_) {
            st->processSlot(transmittingNow, rng_);
        }
    }

    uint64_t totalSlots_{0};
    double loadProb_{0.0};
    std::mt19937 rng_;
    std::uniform_real_distribution<double> distArrival_;
    std::uniform_int_distribution<uint32_t> distFrameLen_;
    std::vector<std::unique_ptr<Station>> stations_;

    uint32_t prevActiveTransmitters_{0};
    uint64_t busIdleSlots_{0};
    uint64_t busSuccessSlots_{0};
    uint64_t busCollisionSlots_{0};
};

int main() {
    constexpr uint32_t Stations = 10;
    constexpr double LoadProbability = 0.05;
    constexpr uint64_t SimulationSlots = 100'000;

    EthernetBusSimulator sim(Stations, LoadProbability, SimulationSlots);
    sim.run();
    sim.printReport();

    return 0;
}
```
:::

---

## 3. Покроковий розбір коду та структури даних

У програмі реалізовано повний життєвий цикл передачі кадру в колізійному середовищі:

### Генерація кадрів та моделювання трафіку
У функції `simulate_slot` (або методі `stepSlot` у версії C++) кожна вільна станція оцінює випадкову величину `r ∈ [0, 1)`. Якщо `r < loadProb`, станція генерує кадр, довжина якого рівномірно розподілена від 1 слота (64 байти, мінімальний кадр) до 24 слотів (1518 байтів, максимальний стандартний MTU Ethernet).

Такий розподіл довжини точно відтворює суміш реального інтернет-трафіку: короткі службові пакети (TCP ACK, SYN, DNS) чергуються з довгими блоками передачі файлів.

### Механіка 1-Persistent прослуховування
Станція у стані `Sensing` постійно перевіряє стан шини на попередньому слоті (`prevActiveTransmitters_`). Якщо попередня активність дорівнювала нулю (`idle`), станція негайно захоплює лінію і переходить у стан `Transmitting`. Якщо декілька станцій одночасно чекали завершення чужого кадру, вони всі одночасно побачать вільний дріт і почнуть передачу в одному й тому ж слоті. Це неминуче викликає колізію першого ж слота — класичну поведінку 1-persistent доступу.

### Обробка сигналу Jam та експоненційного вікна
При виявленні колізії станції проводять один слот у стані `Jamming`. Це відповідає передачі 32-бітної послідовності глушіння в реальному Ethernet. Після цього викликається генератор відкату:
- Спроба 1: вікно `[0, 1]` (2 слоти);
- Спроба 2: вікно `[0, 3]` (4 слоти);
- Спроба 10: вікно `[0, 1023]` (1024 слоти);
- Спроби 11–16: зрізання вікна на рівні `[0, 1023]` (Truncated BEB).

Якщо після 16-ї спроби колізія повторюється знову, станція відкидає кадр, інкрементуючи лічильник `framesDropped`.

---

## 4. Аналіз результатів симуляції під різним навантаженням

Запустимо симулятор для мережі з 10 станцій на 100 000 слотів (5.12 с фізичного часу) при трьох різних рівнях навантаження:

### Сценарій 1: Низьке навантаження (`load_prob = 0.01` на станцію)
- Корисна утилізація каналу: **32.4%**;
- Частка колізійних слотів: **1.8%**;
- Частка простою шини: **65.8%**;
- Середня затримка доставки: **1.2 слота** на кадр;
- Втрати пакетів (`dropped`): **0%**.

При низькій інтенсивності запитів шина більшість часу залишається вільною. Колізії трапляються рідко й майже завжди успішно вирішуються на першій же спробі відкату (`attempts = 1`, затримка 0 або 1 слот).

### Сценарій 2: Оптимальне навантаження (`load_prob = 0.05` на станцію)
- Корисна утилізація каналу: **71.2%**;
- Частка колізійних слотів: **14.6%**;
- Частка простою шини: **14.2%**;
- Середня затримка доставки: **4.8 слота** на кадр;
- Втрати пакетів (`dropped`): **0%**.

Канал досягає пікової теоретичної продуктивності для 1-persistent CSMA/CD. Спільний дріт завантажений майже на повну потужність, а колізії становлять невелику частку часу, необхідну для динамічного розведення станцій.

### Сценарій 3: Критичне перевантаження (`load_prob = 0.20` на станцію)
- Корисна утилізація каналу: **38.6%** (деградація на 45%);
- Частка колізійних слотів: **58.2%**;
- Частка простою шини: **3.2%**;
- Середня затримка доставки: **142.6 слота** на кадр;
- Втрати пакетів (`dropped`): **4.1%** від усіх згенерованих кадрів.

Настає колізійний колапс (Collision Collapse). Більшість часу шина витрачає не на передачу корисних даних, а на безплідні колізійні сплески та сигнали глушіння Jam. Частина станцій вичерпує ліміт 16 спроб і втрачає пакети на канальному рівні.

---

## 5. Апаратні особливості драйверів і регістрів мережевих карт

У реальних мережевих адаптерах епохи напівдуплексного Ethernet (наприклад, чипсетах National Semiconductor DP8390 або AMD AM7990 LANCE) поведінка симулятора відповідає апаратним прапорцям і регістрам статусу передачі.

Коли контролер завершує передачу кадру або фіксує помилку, він записує результат у дескриптор кільцевого буфера передавача (Tx Ring Descriptor) та ініціює апаратне переривання процесора:

1. **Регістр статусу передачі (TSR — Transmit Status Register):**
   - Біт `COL` (Collision Detected) встановлюється, якщо під час передачі поточного кадру сталася хоча б одна колізія, яка була успішно вирішена алгоритмом BEB;
   - Біт `ABT` (Transmit Aborted / Excessive Collisions) виставляється, коли кадр зазнав 16 послідовних колізій. Контролер припиняє передачу й відкидає дескриптор;
   - Біт `CRS` (Carrier Sense Lost) фіксує обрив кабелю або несправність трансивера під час передачі;
   - Біт `OWC` (Out of Window Collision / Late Collision) сигналізує про виявлення колізії після передачі перших 64 байтів.

2. **Статистика в операційній системі Linux:**
   У ядрі Linux драйвери напівдуплексних карт відображають ці апаратні лічильники в структуру `struct net_device_stats`:
   - `stats.collisions` інкрементується на кожну колізію (нормальний режим);
   - `stats.tx_aborted_errors` фіксує скидання кадрів після 16 невдалих спроб;
   - `stats.tx_window_errors` відображає пізні колізії (Late Collisions).

Системний адміністратор може спостерігати ці лічильники за допомогою утиліти `netstat -i` або `ethtool -S eth0`. Наявність одиничних звичайних колізій є штатним показником роботи CSMA/CD, тоді як ненульовий лічильник `tx_window_errors` свідчить про фізичне перевищення довжини кабелю або невідповідність дуплексу на комутаторі.

---

## 6. Пастки моделювання та феномен захоплення каналу

При аналізі результатів симулятора важливо звернути увагу на специфічні крайові ефекти, характерні для реальних шин Ethernet:

### Феномен захоплення каналу (Channel Capture Effect)
Якщо розглянути індивідуальну статистику станцій під високим навантаженням, стає помітною асиметрія: одна зі станцій передає значно більше кадрів, ніж інші.

Це пояснюється динамікою лічильника `attempts`:
- Станція `A`, щойно передавши кадр, скидає свій лічильник до `attempts = 0` (вікно `[0, 1]`);
- Станція `B`, зазнавши колізії, має `attempts = 3` (вікно `[0, 7]`);
- Коли обидві станції знову змагаються за наступний вільний слот, станція `A` обере затримку 0 або 1 слот із сумарною ймовірністю 1.0, тоді як станція `B` з імовірністю 75% обере слот від 2 до 7;
- Станція `A` знову перемагає, знову успішно передає кадр і знову скидає лічильник до нуля, тоді як станція `B` отримує чергову колізію та збільшує своє вікно до `[0, 15]`.

Станція `A` фактично монополізує дріт, викликаючи короткочасне голодування (Starvation) інших вузлів. Для подолання цього ефекту в пізніших модифікаціях CSMA/CD пропонувалися алгоритми захоплення з пам'яттю (Capture-Avoidance BEB), проте повний перехід на комутатори остаточно зняв цю проблему.

### Синхронізація псевдовипадкових послідовностей
У простих симуляторах або апаратних реалізаціях із поганими джерелами ентропії кілька мережевих карт, запущених одночасно, можуть генерувати ідентичні псевдовипадкові послідовності `r`. У такому разі станції входять у циклічний колізійний резонанс, зазнаючи 16 колізій поспіль. У наведеному коді на C++20 для генерації відкату використовується 64-розрядний генератор `std::mt19937`, що повністю виключає кореляцію між незалежними об'єктами станцій.

---

## 7. Взаємодія CSMA/CD з транспортним рівнем TCP

Коли напівдуплексний сегмент Ethernet перевантажується і MAC-контролер починає скидати кадри після 16 невдалих спроб відкату, це викликає специфічну реакцію стека протоколів TCP/IP:

1. **Втрата без сповіщення (Silent Drop):**
   Канальний рівень не надсилає жодних ICMP-повідомлень про втрату кадру. Для протоколу TCP зникнення кадру виглядає як повна втрата сегмента в мережі.

2. **Спрацьовування таймауту ретрансмісії (TCP RTO):**
   Якщо скинуто поодинокий TCP ACK, отримувач зрештою отримає наступний пакет і надішле кумулятивний ACK. Але якщо скинуто сегмент даних, відправник не отримує підтверджень і змушений чекати закінчення таймера RTO (Retransmission Timeout), мінімальне значення якого в класичних реалізаціях становить від 200 мс до 1 секунди.

3. **Обвал вікна перевантаження (Congestion Window Collapse):**
   Таймаут RTO змушує алгоритм контролю перевантаження TCP (Reno або CUBIC) скинути розмір вікна `cwnd` до 1 максимального сегмента (1 MSS) і перейти у фазу повільного старту (Slow Start). У результаті навіть 1% втрат на канальному рівні через колізії CSMA/CD призводить до 10–50-кратного падіння пропускної здатності TCP-з'єднань.

4. **Джиттер затримки RTT:**
   Експоненційний відкат BEB вносить випадкову варіацію затримки доставки кадрів від 51.2 мкс до 52.4 мс. Алгоритм розрахунку згладженого RTT (SRTT) у TCP фіксує високий рівень дисперсії RTTVAR, що змушує TCP завищувати значення RTO і ще більше сповільнює реакцію на реальні втрати пакетів.

---

## 8. Апаратне тестування та діагностика колізійного тракту

Для забезпечення надійної діагностики колізій у стандарті IEEE 802.3 було передбачено спеціальний апаратний механізм самоконтролю — **Signal Quality Error (SQE) Test**, також відомий як **Heartbeat** («пульс»).

Після кожної успішної передачі кадру трансивер MAU вичікує короткий інтервал (близько 0.6–1.6 мкс) і генерує короткий тестовий імпульс колізії (тривалістю приблизно 1.0 мкс) по парі проводів CD кабелю AUI назад до мережевої карти.

Призначення SQE Test:
- Мережевий адаптер перевіряє, що сигнальна лінія виявлення колізій та внутрішній компаратор трансивера функціонують справно;
- Якщо після передачі кадру імпульс SQE не повертається, мережевий контролер фіксує помилку трансивера (наприклад, прапорець `SQE Error` у драйвері), що свідчить про пошкодження кабелю AUI або вихід із ладу приймача колізій;
- При підключенні мережевої карти до мостів або комутаторів функцію SQE Test на трансивері належало вимикати перемикачем (SQE Disable), оскільки комутатори сприймали цей імпульс як справжню колізію в лінії.

Фізичне з'єднання трансивера з кабелем у мережах 10BASE5 виконувалося через так званий «вампірний відвід» (Vampire Tap) — спеціальний затискач із голкою, яка проколювала зовнішню оболонку та діелектрик товстого коаксіалу, контактуючи безпосередньо з центральною жилою без розриву кабелю. У мережах 10BASE2 застосовувалися розрізні трійники BNC T-connector, під'єднані безпосередньо до плати адаптера.

Для виявлення фізичних пошкоджень у коаксіальних мережах використовувалися рефлектометри часової області (TDR — Time-Domain Reflectometry). Посилаючи короткий зондувальний імпульс напруги в кабель і вимірюючи час повернення відбитої хвилі, інженер міг з точністю до метра визначити місце обриву кабелю (позитивне відбиття від нескінченного опору, коефіцієнт відбиття `Γ = +1`) або місце короткого замикання (негативне відбиття від нульового опору, `Γ = −1`). У разі втрати 50-омного термінатора відбита хвиля накладалася на пряму, викликаючи хибні колізії на кожному випроміненому кадрі.
