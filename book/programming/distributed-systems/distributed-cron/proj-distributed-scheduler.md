# ⚙️ Розподілений планувальник із шардованим часовим колесом та огорожею

У розподілених сервісах із високою щільністю періодичних задач (відкладені платежі, очищення тимчасових сесій, моніторинг таймаутів з'єднань) наївне опитування бази даних через запити `SELECT ... WHERE next_run <= NOW()` створює непереборні накладні витрати на процесорні ядра та дисковий ввід-вивід. Коли кількість таймерів досягає сотень тисяч і мільйонів, традиційні структури пам'яті на зразок бінарної купи (англ. *min-heap*) також стають вузьким місцем: кожна операція додавання чи скасування задачі вимагає перебалансування дерева зі складністю `O(log N)`.

Щоб досягти справжнього константного часу виконання `O(1)` для операцій планування, скасування та щосекундного диспатчу задач, сучасні розподілені планувальники поєднують **ієрархічне часове колесо** (англ. *Hierarchical Timing Wheel*) алгоритму Джорджа Варгезе та Тоні Лаука з **координатором ліз володіння шардами** та **токенами огорожі** (англ. *fencing tokens*) для надійного взаємного виключення при відмовах вузлів.

## Архітектурний дизайн та принципи функціонування

Пропонована реалізація розбиває життєвий цикл розподіленого планування на три незалежні та строго ізольовані складові:

1. **Шардування простору задач та оренда ліз (Sharding & Leases)**: простір ідентифікаторів періодичних задач рівномірно розбивається на фіксовану кількість шардингових сегментів за формулою `shard_id = hash(job_id) % NUM_SHARDS`. Кожен екземпляр планувальника у кластері динамічно орендує право на обробку певної групи шардів у розподіленого координатора консенсусу (наприклад, etcd або Raft). Ліза видається на обмежений інтервал `T_lease` (наприклад, 10 секунд). Щоразу, коли вузол отримує або перехоплює шард, координатор інкрементує 64-бітне число — **епоху огорожі** (`fencing_epoch`), яке стає монотонним паспортом усіх операцій цього вузла.
2. **Кільцевий буфер часового колеса (Timing Wheel Slots)**: для кожного активного шарду в пам'яті планувальника ініціалізується кільцевий буфер із фіксованою кількістю слотів `WHEEL_SLOTS` (наприклад, 60 слотів із кроком `WHEEL_TICK_SEC = 1` секунда для покриття хвилинного інтервалу). При додаванні задачі планувальник обчислює цільовий слот за модулем: `target_slot = (current_slot + delay_ticks) % WHEEL_SLOTS`. Якщо інтервал перевищує розмір колеса, задача отримує лічильник повних обертів `remaining_rounds = delay_ticks / WHEEL_SLOTS`. Під час кожного щосекундного такту планувальник зсуває вказівник `current_slot` на одиницю і переглядає однозв'язний список задач поточного слота. Задачі з `remaining_rounds > 0` лише декрементують лічильник, а задачі з `remaining_rounds == 0` вилучаються зі списку та передаються на диспатч за строго константний час `O(1)`.
3. **Диспатч тригерів та захист огорожею (Fenced Dispatching)**: спрацьовуючи, планувальник формує подію запуску, куди упаковує ідентифікатор `job_id`, канонічну часову мітку слота `scheduled_time_utc` та поточний номер `fencing_epoch`. Ця подія передається через брокер черг виконавчим воркерам. Воркер перед початком виконання бізнес-коду перевіряє токен епохи: якщо через мережеву затримку чи GC-паузу старий планувальник прокинувся і надіслав запізнілий тригер із меншим номером епохи, ніж уже зафіксовано у системі (`epoch < highest_seen_epoch`), воркер безумовно відхиляє команду, гарантуючи захист від дублювання операцій.

## Робоча реалізація ядра планувальника

Нижче наведено самодостатній та працездатний приклад реалізації ядра розподіленого планувальника на мовах C та C++. Обидві версії демонструють роботу кільцевого часового колеса, автоматичну деградацію при спливанні строку лізи та механізм фільтрації запізнілих зомбі-тригерів токенами огорожі.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <time.h>

#define WHEEL_SLOTS 60
#define WHEEL_TICK_SEC 1
#define MAX_NAME_LEN 64

/* Структура періодичної задачі */
typedef struct cron_task {
    uint64_t job_id;
    char name[MAX_NAME_LEN];
    uint64_t interval_sec;
    uint64_t next_run_utc;
    uint32_t remaining_rounds;
    struct cron_task* next;
} cron_task_t;

/* Часове колесо для одного шарду */
typedef struct {
    cron_task_t* slots[WHEEL_SLOTS];
    uint32_t current_slot;
    uint64_t current_time_sec;
} timing_wheel_t;

/* Контекст лізи та огорожі шарду */
typedef struct {
    uint32_t shard_id;
    uint64_t fencing_epoch;
    uint64_t lease_deadline_utc;
    bool is_active;
} shard_lease_t;

/* Стан воркера для перевірки огорожі */
typedef struct {
    uint64_t highest_seen_epoch;
} worker_fencing_state_t;

/* Ініціалізація часового колеса */
void wheel_init(timing_wheel_t* w, uint64_t start_time) {
    memset(w->slots, 0, sizeof(w->slots));
    w->current_slot = 0;
    w->current_time_sec = start_time;
}

/* Додавання задачі у часове колесо: O(1) */
void wheel_add_task(timing_wheel_t* w, cron_task_t* task) {
    int64_t delay = (int64_t)(task->next_run_utc - w->current_time_sec);
    if (delay < 0) delay = 0;

    uint64_t ticks = (uint64_t)delay / WHEEL_TICK_SEC;
    task->remaining_rounds = (uint32_t)(ticks / WHEEL_SLOTS);
    uint32_t target_slot = (uint32_t)((w->current_slot + ticks) % WHEEL_SLOTS);

    task->next = w->slots[target_slot];
    w->slots[target_slot] = task;
}

/* Диспатч задачі воркеру з токеном огорожі */
void dispatch_to_worker(const cron_task_t* task, uint64_t epoch, worker_fencing_state_t* worker) {
    printf("[DISPATCH] Запуск задачі ID=%llu ('%s'), Слот=%llu UTC, Епоха=%llu\n",
           (unsigned long long)task->job_id, task->name,
           (unsigned long long)task->next_run_utc, (unsigned long long)epoch);

    /* Перевірка огорожі на боці воркера/сховища */
    if (epoch < worker->highest_seen_epoch) {
        printf("  [ВОРКЕР: ВІДХИЛЕНО] Запізнілий сигнал зомбі-планувальника! (Епоха %llu < %llu)\n",
               (unsigned long long)epoch, (unsigned long long)worker->highest_seen_epoch);
        return;
    }

    worker->highest_seen_epoch = epoch;
    printf("  [ВОРКЕР: ПРИЙНЯТО] Успішне виконання бізнес-логіки для епохи %llu.\n",
           (unsigned long long)epoch);
}

/* Просування часу на один такт (1 секунда): O(1) */
void wheel_tick(timing_wheel_t* w, shard_lease_t* lease, worker_fencing_state_t* worker) {
    w->current_time_sec += WHEEL_TICK_SEC;
    w->current_slot = (w->current_slot + 1) % WHEEL_SLOTS;

    /* Перевірка чинності лізи володіння шардом */
    if (!lease->is_active || w->current_time_sec > lease->lease_deadline_utc) {
        printf("[WARN] Ліза шарду %u спливла! Зупинка генерації тригерів.\n", lease->shard_id);
        return;
    }

    cron_task_t** curr = &w->slots[w->current_slot];
    while (*curr != NULL) {
        cron_task_t* task = *curr;
        if (task->remaining_rounds > 0) {
            task->remaining_rounds--;
            curr = &task->next;
        } else {
            /* Виймаємо задачу зі списку поточного слота */
            *curr = task->next;
            task->next = NULL;

            /* Відправляємо тригер на виконання */
            dispatch_to_worker(task, lease->fencing_epoch, worker);

            /* Перераховуємо наступний запуск для періодичної задачі */
            task->next_run_utc = w->current_time_sec + task->interval_sec;
            wheel_add_task(w, task);
        }
    }
}

int main(void) {
    uint64_t now = 1700000000;
    timing_wheel_t wheel;
    wheel_init(&wheel, now);

    shard_lease_t lease = {
        .shard_id = 1,
        .fencing_epoch = 100,
        .lease_deadline_utc = now + 10,
        .is_active = true
    };

    worker_fencing_state_t worker = { .highest_seen_epoch = 0 };

    /* Реєструємо дві періодичні задачі */
    cron_task_t task1 = {
        .job_id = 101,
        .name = "Database Backup",
        .interval_sec = 2,
        .next_run_utc = now + 2,
        .remaining_rounds = 0,
        .next = NULL
    };
    cron_task_t task2 = {
        .job_id = 102,
        .name = "Billing Settlement",
        .interval_sec = 5,
        .next_run_utc = now + 5,
        .remaining_rounds = 0,
        .next = NULL
    };

    wheel_add_task(&wheel, &task1);
    wheel_add_task(&wheel, &task2);

    printf("=== СТАРТ СИМУЛЯЦІЇ ПЛАНУВАЛЬНИКА (Епоха 100) ===\n");
    for (int sec = 1; sec <= 6; sec++) {
        printf("\n--- Час: T + %d с ---\n", sec);
        wheel_tick(&wheel, &lease, &worker);
    }

    printf("\n=== СИМУЛЯЦІЯ ПАУЗИ ТА ЗМІНИ ЛІДЕРА (Нова Епоха 101) ===\n");
    /* Новий лідер зафіксував свіжішу епоху у воркері */
    worker.highest_seen_epoch = 101;

    /* Старий планувальник виходить із паузи і намагається виконати тригер зі старою епохою 100 */
    printf("Старий вузол із зомбі-епохою 100 надсилає запізнілий тригер:\n");
    dispatch_to_worker(&task1, lease.fencing_epoch, &worker);

    return 0;
}
```
```cpp
#include <iostream>
#include <vector>
#include <memory>
#include <string>
#include <string_view>
#include <chrono>
#include <cstdint>
#include <expected>

namespace cron {

using Seconds = std::chrono::seconds;
using SystemTime = std::chrono::system_clock::time_point;

struct CronTask {
    uint64_t job_id;
    std::string name;
    Seconds interval;
    SystemTime next_run;
    uint32_t remaining_rounds{0};
};

struct TriggerEvent {
    uint64_t job_id;
    std::string name;
    SystemTime scheduled_time;
    uint64_t fencing_epoch;
};

enum class DispatchError {
    LeaseExpired,
    StaleFencingToken
};

/* Стан воркера з підтримкою огорожі */
class WorkerFencingGuard {
public:
    std::expected<void, DispatchError> validate_and_record(uint64_t epoch) noexcept {
        if (epoch < highest_seen_epoch_) {
            return std::unexpected(DispatchError::StaleFencingToken);
        }
        highest_seen_epoch_ = epoch;
        return {};
    }

    [[nodiscard]] uint64_t highest_seen_epoch() const noexcept {
        return highest_seen_epoch_;
    }

private:
    uint64_t highest_seen_epoch_{0};
};

/* Обгортка лізи шарду з перевіркою часу (RAII) */
class ShardLease {
public:
    ShardLease(uint32_t shard_id, uint64_t epoch, SystemTime deadline) noexcept
        : shard_id_(shard_id), epoch_(epoch), deadline_(deadline), active_(true) {}

    [[nodiscard]] bool is_valid(SystemTime current_time) const noexcept {
        return active_ && (current_time <= deadline_);
    }

    [[nodiscard]] uint64_t epoch() const noexcept { return epoch_; }
    [[nodiscard]] uint32_t shard_id() const noexcept { return shard_id_; }

    void invalidate() noexcept { active_ = false; }

private:
    uint32_t shard_id_;
    uint64_t epoch_;
    SystemTime deadline_;
    bool active_;
};

/* Ієрархічне часове колесо */
class TimingWheel {
public:
    static constexpr size_t SlotsCount = 60;
    static constexpr Seconds TickDuration{1};

    explicit TimingWheel(SystemTime start_time)
        : current_time_(start_time), current_slot_(0), slots_(SlotsCount) {}

    void add_task(std::unique_ptr<CronTask> task) {
        auto delay = std::chrono::duration_cast<Seconds>(task->next_run - current_time_).count();
        if (delay < 0) delay = 0;

        auto ticks = static_cast<uint64_t>(delay) / TickDuration.count();
        task->remaining_rounds = static_cast<uint32_t>(ticks / SlotsCount);
        size_t target_slot = (current_slot_ + ticks) % SlotsCount;

        slots_[target_slot].push_back(std::move(task));
    }

    void tick(const ShardLease& lease, WorkerFencingGuard& worker) {
        current_time_ += TickDuration;
        current_slot_ = (current_slot_ + 1) % SlotsCount;

        if (!lease.is_valid(current_time_)) {
            std::cout << "[WARN] Ліза шарду " << lease.shard_id() << " недійсна! Пропуск диспатчу.\n";
            return;
        }

        auto& bucket = slots_[current_slot_];
        std::vector<std::unique_ptr<CronTask>> rearm_list;

        for (auto it = bucket.begin(); it != bucket.end();) {
            if ((*it)->remaining_rounds > 0) {
                (*it)->remaining_rounds--;
                ++it;
            } else {
                auto task = std::move(*it);
                it = bucket.erase(it);

                // Відправляємо тригер
                dispatch(TriggerEvent{
                    .job_id = task->job_id,
                    .name = task->name,
                    .scheduled_time = current_time_,
                    .fencing_epoch = lease.epoch()
                }, worker);

                // Оновлюємо розклад для наступного спрацьовування
                task->next_run = current_time_ + task->interval;
                rearm_list.push_back(std::move(task));
            }
        }

        for (auto& task : rearm_list) {
            add_task(std::move(task));
        }
    }

private:
    void dispatch(const TriggerEvent& ev, WorkerFencingGuard& worker) {
        std::cout << "[DISPATCH C++] Задача ID=" << ev.job_id << " ('" << ev.name
                  << "'), Епоха=" << ev.fencing_epoch << "\n";

        auto res = worker.validate_and_record(ev.fencing_epoch);
        if (!res.has_value()) {
            std::cout << "  [ВОРКЕР: ВІДХИЛЕНО] Токен огорожі застарів! ("
                      << ev.fencing_epoch << " < " << worker.highest_seen_epoch() << ")\n";
        } else {
            std::cout << "  [ВОРКЕР: ПРИЙНЯТО] Успішна обробка задачі.\n";
        }
    }

    SystemTime current_time_;
    size_t current_slot_;
    std::vector<std::vector<std::unique_ptr<CronTask>>> slots_;
};

} // namespace cron

int main() {
    using namespace std::chrono_literals;
    auto now = std::chrono::system_clock::now();

    cron::TimingWheel wheel(now);
    cron::ShardLease lease(1, 200, now + 10s);
    cron::WorkerFencingGuard worker;

    auto t1 = std::make_unique<cron::CronTask>();
    t1->job_id = 501;
    t1->name = "Analytics Aggregation";
    t1->interval = 2s;
    t1->next_run = now + 2s;

    auto t2 = std::make_unique<cron::CronTask>();
    t2->job_id = 502;
    t2->name = "Cache Invalidation";
    t2->interval = 4s;
    t2->next_run = now + 4s;

    wheel.add_task(std::move(t1));
    wheel.add_task(std::move(t2));

    std::cout << "=== СТАРТ СИМУЛЯЦІЇ C++ ПЛАНУВАЛЬНИКА ===\n";
    for (int i = 1; i <= 5; ++i) {
        std::cout << "\n--- Тік " << i << " с ---\n";
        wheel.tick(lease, worker);
    }

    std::cout << "\n=== ТЕСТ ЗОМБІ-СИГНАЛУ ЗІ СТАРОЮ ЕПОХОЮ ===\n";
    // Імітуємо оновлення епохи іншим планувальником
    static_cast<void>(worker.validate_and_record(201));

    // Спроба відправити подію зі старою епохою 200
    cron::TriggerEvent stale_event{
        .job_id = 501,
        .name = "Analytics Aggregation",
        .scheduled_time = now + 6s,
        .fencing_epoch = 200
    };
    auto check = worker.validate_and_record(stale_event.fencing_epoch);
    if (!check.has_value()) {
        std::cout << "Токен 200 відкинуто успішно: безпеку даних збережено.\n";
    }

    return 0;
}
```
:::

## Інженерний аналіз граничних ситуацій та підводних каменів

Під час розгортання та експлуатації шардованих часових коліс у промисловому середовищі виникають специфічні асинхронні ефекти, які необхідно враховувати на рівні системного коду:

1. **Квантування часу та накопичення задач у слоті**: якщо дискретність колеса становить 1 секунду (`dt = 1`), усі задачі, заплановані на інтервал `[t, t + 1)`, потрапляють в один бакет. Якщо в системі зареєстровано 50 000 періодичних завдань, що мають спрацювати опівночі, послідовний обхід зв'язного списку такого слота в одному потоці займе сотні мілісекунд, що затримає настання наступного такту колеса. Для уникнення цієї пастки планувальник ніколи не виконує важкі мережеві запити безпосередньо в циклі обходу слота: вилучені елементи миттєво перекладаються у неблокуючий кільцевий буфер пам'яті (Lock-free Ring Buffer), звідки пул незалежних потоків-диспатчерів транслює події у брокер повідомлень.
2. **Зсув лізи посеред обходу слота через Stop-the-world паузу**: якщо віртуальна машина або процес планувальника зависає у паузі збирача сміття чи свопінгу на 15 секунд під час обробки списку задач, строк лізи на координаторі спливає. Інший вузол кластера перехоплює шард і починає паралельну генерацію тригерів. Коли перший процес прокидається, він намагається завершити обхід списку. Запобіжником тут виступає подвійна перевірка: по-перше, планувальник перевіряє стан лізи перед відправкою кожного окремого елемента; по-друге, навіть якщо пакет було сформовано і надіслано в мережу, виконавчий воркер або база даних заблокує його виконання завдяки застарілому значенню `fencing_epoch`.
3. **Розбіжність між монотонним лічильником та астрономічним часом**: часове колесо функціонує виключно на базі апаратного монотонного таймера операційної системи (`CLOCK_MONOTONIC_RAW` у Linux або `std::chrono::steady_clock` у C++), що гарантує строгу рівномірність тактів без зворотних стрибків. Водночас розрахунок цільових точок запуску задач виконується у глобальній шкалі системного часу UTC. Якщо системний годинник зазнає корекції через протокол NTP, планувальник не пересуває поточний слот колеса стрибком, а плавно коригує відносне зміщення майбутніх слотів, запобігаючи масовому хибному спрацьовуванню таймерів.
4. **Протитиск при переповненні черги воркерів (Backpressure)**: якщо брокер повідомлень або пул виконавців перевантажений і не встигає споживати згенеровані тригери, часове колесо не повинно нескінченно накопичувати події у пам'яті. При досягненні граничного ліміту буфера диспатчу планувальник тимчасово призупиняє обхід майбутніх слотів та переводить задачі у стан `EVALUATING` із фіксацією метрики системного запізнення (Scheduler Lag).
