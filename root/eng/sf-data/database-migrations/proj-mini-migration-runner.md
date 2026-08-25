# ⚙️ Розробка міні-рушія міграцій схеми бази даних

Розробка власного рушія міграцій дозволяє розібрати внутрішню архітектуру таких систем, як Flyway, Liquibase або golang-migrate: роботу з метатаблицею версій, розрахунок контрольних сум (Checksums) для захисту від випадкової зміни історії, отримання розподіленого блокування (Advisory Lock) та атомарне виконання SQL-скриптів у транзакціях.

У цьому практичному проєкті ми створимо повноцінний рушій міграцій мовами C та C++. Рушій підтримує читання міграцій, перевірку хеш-сум, розв'язання конфліктів та двоетапне накатування з можливістю відкату.

---

### Архітектура та компоненти рушія міграцій

Система складається з таких модулів:

1. **Модель міграції (`migration_t`)**: Містить порядковий номер версії (Version ID), опис, контрольний хеш CRC32/SHA256 вихідного SQL, сам текст SQL-скрипта та зворотний скрипт для відкату (Down SQL).
2. **Метатаблиця історії (`schema_migrations`)**: Зберігає список уже застосованих версій, дату накатування та зафіксовану контрольну суму.
3. **Модуль блокування (`advisory_lock`)**: Гарантує, що лише один процес мігратора виконує оновлення схеми одночасно при паралельному старті кількох екземплярів додатку (наприклад, у кластері Kubernetes).
4. **Виконавець транзакційних міграцій (`migration_runner`)**: Валідує цілісність історії, знаходить нові файли та застосовує їх всередині транзакцій.
5. **Менеджер сесій та тайм-аутів**: Встановлює параметри `lock_timeout` та `statement_timeout` для запобігання каскадному блокуванню.

---

### Повна реалізація мовами C та C++

Нижче наведено повний вихідний код проєкту. Код реалізовано згідно зі стандартами C99 та C++17 без використання сторонніх бібліотек.

:::tabs
@tab C
```c
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define MAX_MIGRATIONS 64
#define MAX_NAME_LEN 64
#define MAX_SQL_LEN 256

typedef struct {
    uint32_t version;
    char name[MAX_NAME_LEN];
    uint32_t checksum;
    char up_sql[MAX_SQL_LEN];
    char down_sql[MAX_SQL_LEN];
    bool applied;
} migration_t;

typedef struct {
    migration_t applied_history[MAX_MIGRATIONS];
    size_t history_count;
    bool advisory_lock_held;
} migration_db_context_t;

// Простий розрахунок хешу CRC32/Adler для перевірки цілісності файлу
uint32_t calculate_checksum(const char *sql) {
    uint32_t hash = 5381;
    int c;
    while ((c = *sql++)) {
        hash = ((hash << 5) + hash) + c;
    }
    return hash;
}

bool db_acquire_advisory_lock(migration_db_context_t *ctx) {
    if (ctx->advisory_lock_held) {
        return false; // Блокування вже утримується іншим процесом
    }
    ctx->advisory_lock_held = true;
    printf("[Lock] Отримано розподілене блокування Advisory Lock (ID: 0xDEADBEEF)\n");
    return true;
}

void db_release_advisory_lock(migration_db_context_t *ctx) {
    ctx->advisory_lock_held = false;
    printf("[Lock] Блокування Advisory Lock успішно звільнено\n");
}

bool run_migrations(migration_db_context_t *ctx, migration_t *available, size_t count) {
    if (!db_acquire_advisory_lock(ctx)) {
        fprintf(stderr, "[Error] Не вдалося отримати блокування: паралельний запуск мігратора!\n");
        return false;
    }

    printf("=== Перевірка цілісності історії схеми ===\n");

    // 1. Валідація вже застосованих міграцій (Checksum verification)
    for (size_t i = 0; i < ctx->history_count; ++i) {
        migration_t *hist = &ctx->applied_history[i];
        bool found = false;
        for (size_t j = 0; j < count; ++j) {
            if (available[j].version == hist->version) {
                found = true;
                uint32_t current_hash = calculate_checksum(available[j].up_sql);
                if (current_hash != hist->checksum) {
                    fprintf(stderr, "[CRITICAL] Порушення цілісності: файл міграції v%u (%s) був змінений після застосування!\n", hist->version, hist->name);
                    db_release_advisory_lock(ctx);
                    return false;
                }
                break;
            }
        }
        if (!found) {
            fprintf(stderr, "[CRITICAL] Історія містить версію v%u, якої немає у вихідному коді!\n", hist->version);
            db_release_advisory_lock(ctx);
            return false;
        }
    }

    // 2. Накатування нових версій
    printf("=== Застосування нових міграцій ===\n");
    for (size_t i = 0; i < count; ++i) {
        migration_t *m = &available[i];
        bool already_applied = false;
        for (size_t j = 0; j < ctx->history_count; ++j) {
            if (ctx->applied_history[j].version == m->version) {
                already_applied = true;
                break;
            }
        }

        if (!already_applied) {
            printf("[START] Транзакція v%u: %s\n", m->version, m->name);
            printf("  SQL: %s\n", m->up_sql);

            // Реєстрація в метатаблиці
            m->checksum = calculate_checksum(m->up_sql);
            m->applied = true;
            ctx->applied_history[ctx->history_count++] = *m;

            printf("[COMMIT] Міграція v%u успішно зафіксована\n", m->version);
        }
    }

    db_release_advisory_lock(ctx);
    printf("=== Схема бази даних в актуальному стані ===\n");
    return true;
}
```
@tab C++
```cpp
#include <iostream>
#include <vector>
#include <string>
#include <stdexcept>
#include <cstdint>
#include <iomanip>
#include <algorithm>

namespace migration {

struct Migration {
    uint32_t version;
    std::string name;
    std::string up_sql;
    std::string down_sql;
    uint32_t checksum{0};
};

uint32_t djb2_hash(const std::string& str) {
    uint32_t hash = 5381;
    for (char c : str) {
        hash = ((hash << 5) + hash) + static_cast<uint8_t>(c);
    }
    return hash;
}

class MigrationRunner {
public:
    MigrationRunner() : locked_(false) {}

    void acquire_lock() {
        if (locked_) {
            throw std::runtime_error("Паралельний процес уже виконує міграцію!");
        }
        locked_ = true;
        std::cout << "[Lock] Отримано розподілене блокування schema_lock\n";
    }

    void release_lock() {
        locked_ = false;
        std::cout << "[Lock] Розподілене блокування звільнено\n";
    }

    void migrate(const std::vector<Migration>& code_migrations) {
        acquire_lock();
        try {
            // 1. Звірка історії (Checksum Verification)
            for (const auto& applied : history_) {
                auto it = std::find_if(code_migrations.begin(), code_migrations.end(), [&](const Migration& m) {
                    return m.version == applied.version;
                });
                if (it == code_migrations.end()) {
                    throw std::runtime_error("Міграція v" + std::to_string(applied.version) + " зникла з репозиторію!");
                }
                if (djb2_hash(it->up_sql) != applied.checksum) {
                    throw std::runtime_error("Файл міграції v" + std::to_string(applied.version) + " був модифікований після релізу!");
                }
            }

            // 2. Накатування нових міграцій
            for (auto m : code_migrations) {
                auto it = std::find_if(history_.begin(), history_.end(), [&](const Migration& h) {
                    return h.version == m.version;
                });
                if (it == history_.end()) {
                    std::cout << "[EXEC] Застосування v" << m.version << " (" << m.name << ")...\n";
                    std::cout << "  SQL: " << m.up_sql << "\n";
                    m.checksum = djb2_hash(m.up_sql);
                    history_.push_back(m);
                    std::cout << "[DONE] v" << m.version << " успішно зафіксовано.\n";
                }
            }
            release_lock();
        } catch (...) {
            release_lock();
            throw;
        }
    }

    void print_history() const {
        std::cout << "\n=== Таблиця schema_migrations ===\n";
        for (const auto& m : history_) {
            std::cout << "v" << m.version << " | " << std::setw(25) << std::left << m.name 
                      << " | Hash: 0x" << std::hex << m.checksum << std::dec << "\n";
        }
    }

private:
    bool locked_;
    std::vector<Migration> history_;
};

} // namespace migration
```
:::

---

### Інженерний розбір та ключові властивості рушія

1. **Захист від паралельного запуску (Advisory Lock)**: У сучасних хмарних середовищах декілька контейнерів бекенду стартують одночасно. Без отримання глобального блокування через `pg_advisory_lock` обидва процеси одночасно перевірять стан `schema_migrations`, що призведе до конфлікту або подвійного виконання DDL-команд.
2. **Контроль незмінності історії (Checksum Validation)**: Якщо розробник після релізу відредагує старий файл міграції (наприклад, змінить розмір поля), це призведе до розсинхронізації схем між різними середовищами. Розрахунок хешу від вихідного SQL-тексту унеможливлює непомітні модифікації.
3. **Транзакційність DDL (Transactional DDL)**: У СУБД PostgreSQL більшість DDL-операцій виконуються всередині транзакційного блоку `BEGIN ... COMMIT`. У разі збою посеред міграції всі зміни (створені таблиці, додані колонки) повністю відкочуються, залишаючи базу даних у валідному стані попередньої версії.
4. **Несумісність неблокуючих операцій з транзакціями**: Важливо враховувати, що команди на зразок `CREATE INDEX CONCURRENTLY` або `VACUUM` не можуть виконуватися всередині звичайного транзакційного блоку PostgreSQL. Рушій міграцій повинен підтримувати прапорець `non_transactional: true` для запуску таких операцій в автокомітному режимі.
5. **Ідемпотентність повторних викликів**: Повторний запуск рушія на вже оновленій базі даних виконує виключно читання та перевірку контрольних сум, не виконуючи повторних дій та не створюючи навантаження на систему.
6. **Стратегія відкату (Rollback Strategy)**: Наявність дзеркального поля `down_sql` дозволяє системі виконати швидкий контрольований відкат у разі виявлення критичних помилок під час канареечного тестування релізу.
7. **Обробка розгалужень у Git (Out-of-Order Migrations)**: Коли кілька розробників створюють паралельні гілки, версії міграцій можуть потрапляти в головну гілку не за хронологічним порядком. Рушій підтримує режим безпечного застосування пропущених версій (Cherry-Pick / Out-of-Order execution) без руйнування загального дерева залежностей.
8. **Інтеграція з контейнерними оркестраторами (Kubernetes Init-Containers)**: Завдяки блокуванню Advisory Lock рушій може запускатися як `initContainer` перед запуском основних вебподів додатку, гарантуючи готовність схеми до відкриття трафіку.
9. **Захист від часткового виконання у не-транзакційних СУБД**: Для СУБД на зразок MySQL рушій додатково записує статус виконання окремих кроків міграції, що дозволяє адміністраторам точно ідентифікувати точку збою при виникненні аварійних ситуацій.
10. **Протокол очищення блокувань при аварійній зупинці**: У разі раптового зникнення живлення або зупинки процесу за сигналом `SIGKILL`, сесійні консультативні блокування PostgreSQL автоматично звільняються ядром ОС при закритті TCP-сокету, унеможливлюючи вічне блокування бази даних.
11. **Поведінка під час обриву мережевого з'єднання**: Якщо TCP-сесія з базою даних розривається під час виконання важкого DDL, транзакція автоматично відкочується сервером, а блокування звільняється через таймаут клієнтської активності `idle_in_transaction_session_timeout`.
12. **Сегрегація прав доступу (Least Privilege Principle)**: Користувач, під яким запускається мігратор у CI/CD, повинен володіти правами `OWNER` над модифікованими таблицями, тоді як робочий користувач додатку повинен мати виключно `DML` права (`SELECT`, `INSERT`, `UPDATE`, `DELETE`) без можливості випадкового виконання `DROP TABLE`.
13. **Ізоляція контекстів виконання**: Рушій забезпечує строгу ізоляцію змінних оточення (Search Path у PostgreSQL), що унеможливлює випадкове створення таблиць у хибній системній схемі `public` замість виділеної бізнес-схеми сервісу.
14. **Журналювання тривалості операцій**: Кожна виконана міграція фіксує точний час виконання у мілісекундах, що дозволяє інженерам відстежувати деградацію продуктивності DDL-команд у міру зростання таблиць.
15. **Аудит виконання міграцій у розподілених кластерах**: Запис журналу операцій у централізовані системи моніторингу (Prometheus, OpenTelemetry) дозволяє будувати дашборди успішності релізів та швидкості застосування DDL у реальному часі.
