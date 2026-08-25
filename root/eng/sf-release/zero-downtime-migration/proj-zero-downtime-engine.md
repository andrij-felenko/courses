# ⚙️ Промисловий рушій міграції даних без простою

Фоновий процес перенесення великих масивів даних у живій системі повинен функціонувати в умовах жорсткої ізоляції від критичного шляху виконання користувацьких транзакцій. Якщо звичайний скрипт оновлення запускається як монолітний пакетний процес, він швидко захоплює ресурси введення-виведення дискової підсистеми, роздуває реплікаційний журнал транзакцій і створює тривалі блокування рядків, що спричиняє каскадну деградацію всього сервісу. Промисловий рушій міграції проєктується як саморегульована розподілена система, що безперервно балансує між швидкістю перенесення та стабільністю первинної СКБД.

## Механіка курсорної пагінації проти зміщення `OFFSET`

При роботі з таблицями, що містять десятки або сотні мільйонів рядків, вибір методу розбиття на порції (*Pagination Strategy*) є критичним для продуктивності:

1. **Деградація наївного зміщення (`OFFSET`):**
   Запит виду `SELECT * FROM users ORDER BY id LIMIT 1000 OFFSET 50000000` змушує рушій СКБД прочитати з індексу B-дерева рівно 50 мільйонів і одну тисячу записів, відкинути перші 50 мільйонів і повернути лише останню тисячу. Час виконання такого запиту зростає лінійно `O(N)` із кожною наступною сторінкою, витісняючи гарячі сторінки з буферного пулу оперативної пам'яті (*Buffer Pool*) на диск.

2. **Курсорна пагінація за первинним ключем (Keyset / Cursor Pagination):**
   Рушій запам'ятовує останній успішно оброблений ідентифікатор `last_seen_id` і формує наступний запит за прямим діапазоном: `SELECT * FROM users WHERE id > :last_seen_id ORDER BY id ASC LIMIT 1000`. СКБД виконує прямий точковий пошук у B-дереві за `O(log N)` операцій і негайно зчитує рівно 1000 послідовних рядків. Час виконання кожної пачки залишається стабільним (2–5 мс) незалежно від того, чи це перший мільйон рядків, чи сотий.

## Адаптивне регулювання навантаження та контроль реплікаційного лагу

Головний ризик фонового копіювання — перевантаження каналу реплікації бази даних. Коли воркер генерує великий обсяг операцій `INSERT` або `UPDATE`, журнал випереджального запису (*WAL / Binlog*) наповнюється швидше, ніж вторинні репліки встигають застосовувати зміни через мережу. Виникає реплікаційний лаг, який загрожує втратою даних у разі аварійного перемикання майстра (*Failover*).

Для запобігання цій загрозі рушій реалізує цикл зворотного зв'язку:
* Перед кожною новою транзакційною пачкою воркер опитує стан реплікаційного лагу (наприклад, функцію `pg_last_xact_replay_timestamp()` або лаг байти споживачів CDC).
* Якщо лаг перевищує встановлений поріг безпеки (наприклад, 1500 мс), рушій призупиняє роботу, збільшуючи експоненційну паузу (*Exponential Backoff*).
* Щойно лаг повертається в межі норми, потік копіювання плавно відновлює роботу.

## Захист від втрати даних: умовний запис за версією

Коли паралельно працюють живий подвійний запис застосунку (*Dual-Write*) та фоновий бекфіл, виникає стан перегонів. Якщо користувач оновив свій профіль у момент, коли бекфіл уже прочитав старий зріз, але ще не записав його в нову базу, несинхронізоване збереження затре свіжі дані.

Розв'язанням є **умовний запис** (*Conditional Upsert*):
Кожен запис супроводжується монотонною міткою часу або номером версії `updated_at`. При збереженні пачки в цільову базу операція оновлення конфлікту виконується лише тоді, коли збережений стан у цільовій базі є старішим за запис, який намагається внести бекфіл:
`INSERT ... ON CONFLICT (id) DO UPDATE SET data = EXCLUDED.data WHERE target.updated_at <= EXCLUDED.updated_at`.
Якщо цільовий запис уже оновлено живим трафіком до новішої версії, операція ігнорується, і свіжий стан зберігається.

## Тіньова верифікація цілісності (Shadow Checksum Verification)

Для гарантії 100% узгодженості рушій розраховує контрольну суму або хеш полів кожного запису. Це дозволяє в реальному часі виявляти розходження форматів, помилки перетворення типів або пошкодження даних ще до перемикання основного трафіку.

## Крайові випадки та обробка аномалій

Промислова експлуатація рушія міграції стикається з низкою нестандартних сценаріїв, які вимагають детермінованої поведінки:

1. **Фізичне та м'яке видалення рядків (Deletions & Tombstones):**
   Якщо користувач видаляє обліковий запис під час міграції, просте копіювання `SELECT` не зафіксує факт зникнення рядка, якщо бекфіл уже пройшов цей діапазон. При використанні м'якого видалення (*Soft Deletes*) колонка `deleted_at` копіюється як звичайна мутація. При фізичному видаленні (*Hard Deletes*) рушій обов'язково синхронізується з потоком CDC або веде журнал могильних маркерів (*Tombstones*), які повторно застосовуються до цільової бази перед фінальним перемиканням.

2. **Отруйні записи та ізоляція помилок (Poison Rows):**
   Якщо окремий рядок містить пошкоджені бінарні дані або не проходить валідацію нової схеми (наприклад, некоректний формат email), аварійне завершення всієї пачки заблокує процес міграції. Рушій перехоплює помилку, ізолює проблемний запис у спеціальну карантинну таблицю розходжень (*Dead Letter Table*) і продовжує обробку решти пачки.

3. **Керування пам'яттю та ресурсами процесу:**
   Для обробки сотень мільйонів записів неприпустимо виділяти динамічну пам'ять на кожен рядок. Буфер пачки виділяється один раз при старті процесу (`malloc` фіксованого масиву або `std::vector::reserve`), що усуває фрагментацію купи та навантаження на збирач сміття.

4. **Коректна зупинка та збереження контрольних точок (Graceful Shutdown):**
   При отриманні сигналів операційної системи `SIGTERM` або `SIGINT` воркер не перериває транзакцію на середині пачки, а завершує поточну ітерацію, скидає значення `last_processed_id` на диск і коректно закриває з'єднання з базою.

## Реалізація рушія

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <time.h>

#define BATCH_SIZE 1000
#define MAX_ALLOWED_LAG_MS 1500
#define DEFAULT_SLEEP_MS 10

typedef struct {
    int64_t id;
    char email[128];
    int64_t updated_at_ms;
    uint32_t checksum;
} Record;

typedef struct {
    int64_t last_processed_id;
    int64_t total_migrated;
    int64_t total_skipped_due_to_race;
    int64_t checksum_mismatches;
} MigrationStats;

/* Швидкий хеш для асинхронної верифікації полів сутності */
static uint32_t compute_record_crc(const Record* r) {
    uint32_t hash = 5381;
    const unsigned char* p = (const unsigned char*)r->email;
    while (*p) {
        hash = ((hash << 5) + hash) + *p++;
    }
    hash = ((hash << 5) + hash) + (uint32_t)(r->updated_at_ms & 0xFFFFFFFF);
    return hash;
}

/* Опитування системних метрик СКБД для контролю реплікаційного відставання */
static int64_t get_current_replication_lag_ms(void) {
    /* Симуляція запиту до pg_stat_replication або binlog_lag */
    return 120;
}

/* Курсорна вибірка порції історичних даних без використання OFFSET */
static size_t fetch_source_batch(int64_t after_id, Record* batch_out, size_t max_count) {
    size_t count = 0;
    for (size_t i = 0; i < max_count && (after_id + (int64_t)i + 1) <= 5000; ++i) {
        batch_out[i].id = after_id + (int64_t)i + 1;
        snprintf(batch_out[i].email, sizeof(batch_out[i].email), "user_%lld@company.ua", (long long)batch_out[i].id);
        batch_out[i].updated_at_ms = 1700000000000LL + batch_out[i].id * 10;
        batch_out[i].checksum = compute_record_crc(&batch_out[i]);
        count++;
    }
    return count;
}

/* Умовне застосування пачки із запобіганням затиранню живих мутацій */
static bool apply_conditional_upsert_batch(const Record* batch, size_t count, MigrationStats* stats) {
    for (size_t i = 0; i < count; ++i) {
        /* Імітація наявності свіжішого стану від живого Dual-Write */
        int64_t existing_target_updated_at = (batch[i].id % 250 == 0) ? (batch[i].updated_at_ms + 5000) : 0;

        if (existing_target_updated_at > batch[i].updated_at_ms) {
            /* Стан у цільовій базі свіжіший — захищаємо від перезапису */
            stats->total_skipped_due_to_race++;
        } else {
            stats->total_migrated++;
        }

        /* Тіньова перевірка контрольних сум */
        uint32_t target_crc = compute_record_crc(&batch[i]);
        if (target_crc != batch[i].checksum) {
            stats->checksum_mismatches++;
        }
    }
    return true;
}

int main(void) {
    MigrationStats stats = {0, 0, 0, 0};
    Record* batch_buffer = (Record*)malloc(sizeof(Record) * BATCH_SIZE);
    if (!batch_buffer) {
        fprintf(stderr, "Помилка виділення пам'яті під буфер пачки\n");
        return 1;
    }

    printf("=== СТАРТ ФОНОВОГО РУШІЯ МІГРАЦІЇ ===\n");

    while (true) {
        int64_t lag = get_current_replication_lag_ms();
        if (lag > MAX_ALLOWED_LAG_MS) {
            printf("[ДРОСЕЛЮВАННЯ] Лаг %lld мс перевищує ліміт %d мс. Очікування...\n",
                   (long long)lag, MAX_ALLOWED_LAG_MS);
            struct timespec ts = {0, 50 * 1000000L};
            nanosleep(&ts, NULL);
            continue;
        }

        size_t fetched = fetch_source_batch(stats.last_processed_id, batch_buffer, BATCH_SIZE);
        if (fetched == 0) {
            printf("Усі історичні дані успішно оброблено.\n");
            break;
        }

        if (!apply_conditional_upsert_batch(batch_buffer, fetched, &stats)) {
            fprintf(stderr, "Критична помилка запису пачки\n");
            break;
        }

        stats.last_processed_id = batch_buffer[fetched - 1].id;
        printf("[ПРОГРЕС] Оброблено до ID: %lld | Успішно: %lld | Пропущено через гонку: %lld\n",
               (long long)stats.last_processed_id,
               (long long)stats.total_migrated,
               (long long)stats.total_skipped_due_to_race);

        struct timespec sleep_ts = {0, DEFAULT_SLEEP_MS * 1000000L};
        nanosleep(&sleep_ts, NULL);
    }

    printf("=== ПІДСУМОК МІГРАЦІЇ ===\n");
    printf("Всього перенесено рядків: %lld\n", (long long)stats.total_migrated);
    printf("Захищено свіжих мутацій від затирання: %lld\n", (long long)stats.total_skipped_due_to_race);
    printf("Помилок контрольних сум: %lld\n", (long long)stats.checksum_mismatches);

    free(batch_buffer);
    return 0;
}
```
```cpp
#include <iostream>
#include <vector>
#include <string>
#include <string_view>
#include <chrono>
#include <thread>
#include <cstdint>
#include <memory>
#include <expected>
#include <span>

namespace migration {

struct Record {
    int64_t id{0};
    std::string email;
    std::chrono::milliseconds updated_at{0};
    uint32_t checksum{0};
};

struct MigrationStats {
    int64_t last_processed_id{0};
    int64_t total_migrated{0};
    int64_t total_skipped_due_to_race{0};
    int64_t checksum_mismatches{0};
};

class MigrationEngine {
public:
    static constexpr size_t kBatchSize = 1000;
    static constexpr auto kMaxAllowedLag = std::chrono::milliseconds(1500);
    static constexpr auto kDefaultSleep = std::chrono::milliseconds(10);

    MigrationEngine() = default;

    std::expected<MigrationStats, std::string> run() {
        std::vector<Record> batch_buffer;
        batch_buffer.reserve(kBatchSize);

        std::cout << "=== СТАРТ ФОНОВОГО РУШІЯ МІГРАЦІЇ (C++) ===\n";

        while (true) {
            const auto current_lag = measure_replication_lag();
            if (current_lag > kMaxAllowedLag) {
                std::cout << "[ДРОСЕЛЮВАННЯ] Лаг " << current_lag.count() 
                          << " мс перевищує ліміт. Пауза...\n";
                std::this_thread::sleep_for(std::chrono::milliseconds(50));
                continue;
            }

            batch_buffer.clear();
            fetch_source_batch(stats_.last_processed_id, batch_buffer, kBatchSize);

            if (batch_buffer.empty()) {
                std::cout << "Усі історичні дані успішно оброблено.\n";
                break;
            }

            if (!apply_conditional_upsert(batch_buffer)) {
                return std::unexpected("Критична помилка застосування пачки до цільової БД");
            }

            stats_.last_processed_id = batch_buffer.back().id;
            std::cout << "[ПРОГРЕС] Оброблено до ID: " << stats_.last_processed_id
                      << " | Успішно: " << stats_.total_migrated
                      << " | Пропущено через гонку: " << stats_.total_skipped_due_to_race << "\n";

            std::this_thread::sleep_for(kDefaultSleep);
        }

        return stats_;
    }

private:
    MigrationStats stats_;

    static uint32_t compute_crc(const Record& r) noexcept {
        uint32_t hash = 5381;
        for (const char ch : r.email) {
            hash = ((hash << 5) + hash) + static_cast<uint8_t>(ch);
        }
        hash = ((hash << 5) + hash) + static_cast<uint32_t>(r.updated_at.count() & 0xFFFFFFFF);
        return hash;
    }

    std::chrono::milliseconds measure_replication_lag() const noexcept {
        return std::chrono::milliseconds(120);
    }

    void fetch_source_batch(int64_t after_id, std::vector<Record>& out, size_t limit) const {
        for (size_t i = 0; i < limit && (after_id + static_cast<int64_t>(i) + 1) <= 5000; ++i) {
            Record r;
            r.id = after_id + static_cast<int64_t>(i) + 1;
            r.email = "user_" + std::to_string(r.id) + "@company.ua";
            r.updated_at = std::chrono::milliseconds(1700000000000LL + r.id * 10);
            r.checksum = compute_crc(r);
            out.push_back(std::move(r));
        }
    }

    bool apply_conditional_upsert(std::span<const Record> batch) noexcept {
        for (const auto& record : batch) {
            const auto target_updated_at = (record.id % 250 == 0)
                ? (record.updated_at + std::chrono::milliseconds(5000))
                : std::chrono::milliseconds(0);

            if (target_updated_at > record.updated_at) {
                stats_.total_skipped_due_to_race++;
            } else {
                stats_.total_migrated++;
            }

            if (compute_crc(record) != record.checksum) {
                stats_.checksum_mismatches++;
            }
        }
        return true;
    }
};

} // namespace migration

int main() {
    migration::MigrationEngine engine;
    auto result = engine.run();

    if (!result) {
        std::cerr << "Помилка міграції: " << result.error() << "\n";
        return 1;
    }

    const auto& stats = *result;
    std::cout << "=== ПІДСУМОК МІГРАЦІЇ ===\n"
              << "Всього перенесено рядків: " << stats.total_migrated << "\n"
              << "Захищено свіжих мутацій: " << stats.total_skipped_due_to_race << "\n"
              << "Розходжень хешів: " << stats.checksum_mismatches << "\n";

    return 0;
}
```
:::
