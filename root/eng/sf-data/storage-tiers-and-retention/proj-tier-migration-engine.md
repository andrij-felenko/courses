# ⚙️ Багатопотоковий рушій витіснення та міграції чанків між ярусами зберігання

Міграція блоків даних між швидкими й повільними накопичувачами в режимі реального часу не повинна блокувати поточні запити на читання та запис або залишати систему в неузгодженому стані у випадку мережевих чи апаратних збоїв. Цей проект реалізує повнофункціональний багатопотоковий рушій тирування (англ. *Storage Tiering Engine*), що відстежує температуру доступу за експоненційним згасанням, реагує на ватермарки заповненості простору та виконує атомарну міграцію блоків за протоколом Copy-Verify-CAS-Discard.

### Архітектура та протокол міграції

Процес витіснення працює як фоновий демон і складається з трьох ключових компонентів:

```
  ┌─────────────────────────────────────────────────────────────┐
  │         Потік моніторингу заповненості (Watermark Monitor)  │
  └──────────────────────────────┬──────────────────────────────┘
                                 │ Hot Tier Capacity > High Watermark (85%)
                                 ▼
  ┌─────────────────────────────────────────────────────────────┐
  │   Планувальник вибору кандидатів (Temperature Decayed LRU)  │
  └──────────────────────────────┬──────────────────────────────┘
                                 │ Сортування блоків за оцінкою S(t)
                                 ▼
  ┌─────────────────────────────────────────────────────────────┐
  │   Пул потоків міграції (Worker Pool): Copy -> Checksum ->   │
  │   Atomic CAS Pointer Swap -> blkdiscard / unmap Hot Storage │
  └─────────────────────────────────────────────────────────────┘
```

Для запобігання гонкам даних під час паралельного читання стан кожного чанка захищається блокуванням читачів-письменників (Read-Write Lock). Під час копіювання корисного навантаження в цільовий ярус чанк залишається доступним для читачів у гарячому ярусі. Блокування на ексклюзивний запис захоплюється лише на кілька наносекунд для підміни дескриптора цільового ярусу.

### Чотирифідний життєвий цикл блоку даних

Кожен блок даних (чанк) розміром від 4 МіБ до 64 МіБ проходить через суворий чотирифазний конвеєр переміщення:

1. **Фаза 1: Оцінка температури та вибір кандидата.** Фоновий потік моніторингу регулярно вимірює рівень утилізації дискового простору гарячого ярусу (NVMe). Якщо відсоток зайнятого місця перевищує верхню ватермарку (`High Watermark = 85%`), планувальник сканує каталог метаданих, обчислює актуальну згаслу температуру `S(t)` для кожного активного чанка та формує пріоритетну чергу кандидатів із найменшою оцінкою.
2. **Фаза 2: Фонове копіювання з прямим вводом-виводом (Direct I/O).** Потік-виконавець (англ. *migration worker*) переводить стан чанка в `CHUNK_STATE_MIGRATING`. На цьому етапі читачі продовжують звертатися до оригінального блоку на NVMe без жодних затримок. Вміст чанка зчитується в буфер пам'яті з використанням системних прапорців прямого вводу-виводу `O_DIRECT`, щоб не витісняти корисні сторінки з оперативного кешу операційної системи (Linux Page Cache), і асинхронно відправляється в цільове сховище (теплий диск або об'єктне сховище S3).
3. **Фаза 3: Верифікація цілісності та атомарна підміна покажчика.** Після завершення запису цільовий накопичувач повертає підтвердження та контрольну суму (CRC32C або BLAKE3). Якщо хеш збігається з еталонним значенням метаданих, потік міграції захоплює ексклюзивне блокування на запис (`pthread_rwlock_wrlock` або `std::unique_lock`) на короткий інтервал підміни поля `current_tier` та повернення статусу `CHUNK_STATE_ONLINE`. Усі наступні запити на читання автоматично перенаправляються за новою адресою.
4. **Фаза 4: Звільнення фізичного простору (TRIM / UNMAP).** Потік видає команду `ioctl(fd, BLKDISCARD)` або системний виклик `fallocate(FALLOC_FL_PUNCH_HOLE)` до файлу-контейнера на накопичувачі NVMe. Це повідомляє контролеру твердотільного накопичувача, що відповідні LBA-адреси більше не містять корисних даних, дозволяючи внутрішньому збирачеві сміття FTL (Flash Translation Layer) включити ці блоки в пул очищення без додаткового коефіцієнта посилення запису (Write Amplification).

### Реалізація планувальника та рушія міграції

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <time.h>
#include <math.h>
#include <pthread.h>
#include <unistd.h>

#define MAX_CHUNKS 1024
#define HOT_TIER_CAPACITY_BYTES (1024 * 1024 * 1024ULL) // 1 GiB
#define HIGH_WATERMARK_RATIO 0.85
#define LOW_WATERMARK_RATIO 0.70
#define TEMPERATURE_HALF_LIFE_SEC 3600.0 // 1 година

typedef enum {
    TIER_HOT = 0,
    TIER_WARM = 1,
    TIER_COLD = 2,
    TIER_ARCHIVE = 3
} storage_tier_t;

typedef enum {
    CHUNK_STATE_ONLINE,
    CHUNK_STATE_MIGRATING,
    CHUNK_STATE_DELETED
} chunk_state_t;

typedef struct {
    uint64_t chunk_id;
    size_t size_bytes;
    storage_tier_t current_tier;
    chunk_state_t state;
    
    // Статистика доступу
    double temperature_score;
    time_t last_access_ts;
    uint64_t access_count;
    
    uint32_t checksum;
    pthread_rwlock_t lock;
} chunk_meta_t;

typedef struct {
    chunk_meta_t chunks[MAX_CHUNKS];
    size_t total_chunks;
    
    uint64_t hot_bytes_used;
    pthread_mutex_t engine_mutex;
    bool is_running;
} tier_engine_t;

// Обчислення згасання температури доступу: S(t) = S(t0) * 2^(-dt / T_half)
static double decay_temperature(double current_score, time_t last_ts, time_t now) {
    double dt = difftime(now, last_ts);
    if (dt <= 0.0) return current_score;
    double decay_factor = pow(2.0, -dt / TEMPERATURE_HALF_LIFE_SEC);
    return current_score * decay_factor;
}

// Фіксація звернення до блоку читачем або транзакцією
void tier_engine_record_access(tier_engine_t *engine, uint64_t chunk_id) {
    if (chunk_id >= engine->total_chunks) return;
    chunk_meta_t *c = &engine->chunks[chunk_id];
    
    pthread_rwlock_wrlock(&c->lock);
    time_t now = time(NULL);
    double decayed = decay_temperature(c->temperature_score, c->last_access_ts, now);
    c->temperature_score = decayed + 1.0;
    c->last_access_ts = now;
    c->access_count++;
    pthread_rwlock_unlock(&c->lock);
}

// Імітація безпечного копіювання даних та обчислення контрольної суми
static bool simulate_tier_transfer(uint64_t chunk_id, storage_tier_t src, storage_tier_t dst, uint32_t *out_chk) {
    usleep(5000); // 5 мс затримки I/O
    *out_chk = (uint32_t)(chunk_id ^ 0xDEADBEEF);
    return true;
}

// Атомарний 4-кроковий конвеєр міграції одного чанка
static bool migrate_single_chunk(tier_engine_t *engine, chunk_meta_t *c, storage_tier_t target_tier) {
    pthread_rwlock_wrlock(&c->lock);
    if (c->state != CHUNK_STATE_ONLINE || c->current_tier == target_tier) {
        pthread_rwlock_unlock(&c->lock);
        return false;
    }
    
    storage_tier_t old_tier = c->current_tier;
    size_t chunk_size = c->size_bytes;
    c->state = CHUNK_STATE_MIGRATING;
    pthread_rwlock_unlock(&c->lock);
    
    // Крок 1 і 2: Копіювання у цільовий ярус і верифікація контрольної суми
    uint32_t target_checksum = 0;
    bool copy_ok = simulate_tier_transfer(c->chunk_id, old_tier, target_tier, &target_checksum);
    
    if (!copy_ok || target_checksum != c->checksum) {
        pthread_rwlock_wrlock(&c->lock);
        c->state = CHUNK_STATE_ONLINE; // Відкат стану при збої
        pthread_rwlock_unlock(&c->lock);
        fprintf(stderr, "[ПОМИЛКА] Збій копіювання або невідповідність CRC чанка %lu\n", c->chunk_id);
        return false;
    }
    
    // Крок 3: Атомарна підміна цільового покажчика в метаданих
    pthread_rwlock_wrlock(&c->lock);
    c->current_tier = target_tier;
    c->state = CHUNK_STATE_ONLINE;
    pthread_rwlock_unlock(&c->lock);
    
    // Крок 4: Звільнення дискового простору старого ярусу (blkdiscard / trim)
    if (old_tier == TIER_HOT) {
        pthread_mutex_lock(&engine->engine_mutex);
        if (engine->hot_bytes_used >= chunk_size) {
            engine->hot_bytes_used -= chunk_size;
        } else {
            engine->hot_bytes_used = 0;
        }
        pthread_mutex_unlock(&engine->engine_mutex);
    }
    
    printf("[ТИРУВАННЯ] Чанк %lu успішно переміщено %d -> %d (%zu байтів)\n",
           c->chunk_id, old_tier, target_tier, chunk_size);
    return true;
}

// Робочий цикл фонового планувальника
void* tiering_scheduler_thread(void *arg) {
    tier_engine_t *engine = (tier_engine_t*)arg;
    
    while (engine->is_running) {
        pthread_mutex_lock(&engine->engine_mutex);
        uint64_t used = engine->hot_bytes_used;
        pthread_mutex_unlock(&engine->engine_mutex);
        
        double current_ratio = (double)used / (double)HOT_TIER_CAPACITY_BYTES;
        
        if (current_ratio > HIGH_WATERMARK_RATIO) {
            printf("[УВАГА] Заповненість Hot ярусу %.1f%% > High Watermark (85%%). Початок витіснення.\n",
                   current_ratio * 100.0);
            
            time_t now = time(NULL);
            
            // Пошук найхолоднішого чанка серед активних у гарячому ярусі
            while (current_ratio > LOW_WATERMARK_RATIO && engine->is_running) {
                int64_t coldest_id = -1;
                double min_temp = 1e18;
                
                for (size_t i = 0; i < engine->total_chunks; i++) {
                    chunk_meta_t *c = &engine->chunks[i];
                    pthread_rwlock_rdlock(&c->lock);
                    if (c->state == CHUNK_STATE_ONLINE && c->current_tier == TIER_HOT) {
                        double t = decay_temperature(c->temperature_score, c->last_access_ts, now);
                        if (t < min_temp) {
                            min_temp = t;
                            coldest_id = (int64_t)i;
                        }
                    }
                    pthread_rwlock_unlock(&c->lock);
                }
                
                if (coldest_id == -1) break; // Немає доступних кандидатів
                
                migrate_single_chunk(engine, &engine->chunks[coldest_id], TIER_WARM);
                
                pthread_mutex_lock(&engine->engine_mutex);
                used = engine->hot_bytes_used;
                pthread_mutex_unlock(&engine->engine_mutex);
                current_ratio = (double)used / (double)HOT_TIER_CAPACITY_BYTES;
            }
            
            printf("[ІНФО] Витіснення завершено. Поточна заповненість Hot ярусу: %.1f%%\n",
                   current_ratio * 100.0);
        }
        
        sleep(1); // Період опитування датчика
    }
    return NULL;
}
```
```cpp
#include <iostream>
#include <vector>
#include <memory>
#include <shared_mutex>
#include <mutex>
#include <atomic>
#include <chrono>
#include <cmath>
#include <thread>
#include <optional>
#include <algorithm>

enum class StorageTier : uint8_t {
    Hot = 0,
    Warm = 1,
    Cold = 2,
    Archive = 3
};

enum class ChunkState : uint8_t {
    Online,
    Migrating,
    Deleted
};

struct ChunkMetadata {
    const uint64_t id;
    const size_t size_bytes;
    StorageTier current_tier{StorageTier::Hot};
    ChunkState state{ChunkState::Online};
    
    double temperature_score{1.0};
    std::chrono::system_clock::time_point last_access;
    uint64_t access_count{0};
    uint32_t checksum{0};
    
    mutable std::shared_mutex rw_lock;

    ChunkMetadata(uint64_t chunk_id, size_t size)
        : id(chunk_id), size_bytes(size), last_access(std::chrono::system_clock::now()),
          checksum(static_cast<uint32_t>(chunk_id ^ 0xDEADBEEF)) {}
          
    double calculate_decayed_temperature(std::chrono::system_clock::time_point now, double half_life_sec) const {
        auto duration = std::chrono::duration_cast<std::chrono::seconds>(now - last_access).count();
        if (duration <= 0) return temperature_score;
        double decay = std::pow(2.0, -static_cast<double>(duration) / half_life_sec);
        return temperature_score * decay;
    }
};

class TieringMigrationEngine {
public:
    TieringMigrationEngine(size_t hot_capacity_bytes, double high_wm = 0.85, double low_wm = 0.70)
        : hot_tier_capacity_(hot_capacity_bytes),
          high_watermark_(high_wm),
          low_watermark_(low_wm),
          is_running_(true) {}

    ~TieringMigrationEngine() {
        stop();
    }

    void register_chunk(uint64_t id, size_t size_bytes) {
        auto chunk = std::make_unique<ChunkMetadata>(id, size_bytes);
        std::unique_lock lock(catalog_mutex_);
        hot_bytes_used_ += size_bytes;
        chunks_.push_back(std::move(chunk));
    }

    void record_access(uint64_t chunk_id) {
        std::shared_lock lock(catalog_mutex_);
        if (chunk_id >= chunks_.size()) return;
        
        auto& c = *chunks_[chunk_id];
        std::unique_lock chunk_lock(c.rw_lock);
        auto now = std::chrono::system_clock::now();
        double decayed = c.calculate_decayed_temperature(now, 3600.0);
        c.temperature_score = decayed + 1.0;
        c.last_access = now;
        ++c.access_count;
    }

    void start_scheduler() {
        worker_thread_ = std::jthread([this](std::stop_token st) {
            while (!st.stop_requested() && is_running_) {
                evaluate_and_migrate();
                std::this_thread::sleep_for(std::chrono::milliseconds(500));
            }
        });
    }

    void stop() {
        is_running_ = false;
        if (worker_thread_.joinable()) {
            worker_thread_.request_stop();
        }
    }

private:
    const size_t hot_tier_capacity_;
    const double high_watermark_;
    const double low_watermark_;
    
    std::atomic<bool> is_running_{false};
    std::atomic<size_t> hot_bytes_used_{0};
    
    std::vector<std::unique_ptr<ChunkMetadata>> chunks_;
    std::shared_mutex catalog_mutex_;
    std::jthread worker_thread_;

    bool execute_chunk_migration(ChunkMetadata& chunk, StorageTier target_tier) {
        StorageTier old_tier;
        size_t size = chunk.size_bytes;

        {
            std::unique_lock lock(chunk.rw_lock);
            if (chunk.state != ChunkState::Online || chunk.current_tier == target_tier) {
                return false;
            }
            old_tier = chunk.current_tier;
            chunk.state = ChunkState::Migrating;
        }

        // Імітація фонового передавання даних у новий ярус
        std::this_thread::sleep_for(std::chrono::milliseconds(5));
        uint32_t calculated_crc = static_cast<uint32_t>(chunk.id ^ 0xDEADBEEF);

        if (calculated_crc != chunk.checksum) {
            std::unique_lock lock(chunk.rw_lock);
            chunk.state = ChunkState::Online; // Відкат стану
            std::cerr << "[ПОМИЛКА] Невідповідність CRC під час міграції чанка " << chunk.id << "\n";
            return false;
        }

        // Атомарна фіксація нового ярусу
        {
            std::unique_lock lock(chunk.rw_lock);
            chunk.current_tier = target_tier;
            chunk.state = ChunkState::Online;
        }

        // Звільнення ємності гарячого ярусу
        if (old_tier == StorageTier::Hot) {
            hot_bytes_used_.fetch_sub(size);
        }

        std::cout << "[ТИРУВАННЯ] Чанк " << chunk.id << " переведено на ярус " 
                  << static_cast<int>(target_tier) << " (" << size << " байтів)\n";
        return true;
    }

    void evaluate_and_migrate() {
        size_t used = hot_bytes_used_.load();
        double current_ratio = static_cast<double>(used) / static_cast<double>(hot_tier_capacity_);

        if (current_ratio <= high_watermark_) return;

        std::cout << "[УВАГА] Рівень заповнення Hot ярусу: " << (current_ratio * 100.0) 
                  << "% > High Watermark. Запуск витіснення.\n";

        auto now = std::chrono::system_clock::now();

        while (current_ratio > low_watermark_ && is_running_) {
            ChunkMetadata* best_candidate = nullptr;
            double min_score = std::numeric_limits<double>::max();

            {
                std::shared_lock lock(catalog_mutex_);
                for (const auto& chunk : chunks_) {
                    std::shared_lock chunk_lock(chunk->rw_lock);
                    if (chunk->state == ChunkState::Online && chunk->current_tier == StorageTier::Hot) {
                        double score = chunk->calculate_decayed_temperature(now, 3600.0);
                        if (score < min_score) {
                            min_score = score;
                            best_candidate = chunk.get();
                        }
                    }
                }
            }

            if (!best_candidate) break;

            execute_chunk_migration(*best_candidate, StorageTier::Warm);
            
            used = hot_bytes_used_.load();
            current_ratio = static_cast<double>(used) / static_cast<double>(hot_tier_capacity_);
        }
    }
};
```
:::

### Математика згасання температури проти звичайного LRU

Класичний алгоритм LRU (Least Recently Used) має серйозну ваду в сховищах даних: він чутливий до одноразових масових сканувань (англ. *scan pollution*). Якщо аналітичний запит або утиліта резервного копіювання виконує повне послідовне читання таблиці, чистий LRU оновить часові мітки всіх старих блоків, витіснивши з гарячого ярусу справді популярні транзакційні дані.

У реалізованому рушії застосовано модель експоненційного згасання температури з періодом напіврозпаду `T_half`:

```
S(t) = S(t_0) · 2^(-(t - t_0) / T_half) + 1.0
```

Кожне нове звернення збільшує оцінку блоку на фіксовану одиницю (`+1.0`), але попередня накопичена вага експоненційно тане з часом. Якщо до блоку звернулися один раз під час сканування, його вага підніметься з 0 до 1.0, і вже через один період `T_half` (наприклад, 1 годину) впаде до 0.5, а через 3 години — до 0.125. 

Натомість блок, до якого регулярно надходить 100 запитів на хвилину, матиме високу рівноважну температуру близько `100 · T_half / ln(2)`, що надійно захищає його від випадкового витіснення будь-якими пакетними аналітичними операціями.

### Споживання оперативної пам'яті каталогом метаданих

Важливою інженерною вимогою до рушія тирування є низький оверхед на збереження стану блоків в оперативній пам'яті. Структура `chunk_meta_t` у мові C займає 64 байти (з урахуванням вирівнювання пам'яті та м'ютекса):

- Якщо розмір чанка становить 4 КіБ (розмір сторінки ОС), для сховища місткістю 1 Петабайт знадобилося б `2.74 · 10^11` структур метаданих, що потребувало б понад 17 Терабайтів оперативної пам'яті лише під індекси каталогу.
- При оптимізованому розмірі чанка в 64 МіБ 1 Петабайт даних містить рівно `16 777 216` чанків. Сумарний обсяг каталогу метаданих становить лише:

```
16 777 216 · 64 байти = 1 073 741 824 байти = 1.0 ГіБ RAM
```

Це дозволяє утримувати повну таблицю розміщення блоків у надшвидкій оперативній пам'яті контролера сховища, гарантуючи виконання перевірки температури та маршрутизації за лічені наносекунди.

### Інваріанти стійкості та обробка збоїв

1. **Гарантія незмінності адреси під час читання:** Перемикання дескриптора `current_tier` відбувається лише після підтвердження I/O-операції запису в цільове сховище та валідації контрольної суми `checksum`. Будь-який запит на читання, що надходить у момент копіювання, обслуговується старим ярусом без блокування виконання.
2. **Захист від осциляцій (Throttling Hysteresis):** Використання двох роздільних порогів — верхнього (85%) для запуску витіснення та нижнього (70%) для його зупинки — запобігає «тремтінню» системи (англ. *thrashing*), коли дрібні порції нових даних постійно викликали б поодинокі міграції блоків туди й назад.
3. **Ідемпотентний відкат при збоях мережі:** Якщо цільове сховище (наприклад, S3 API або мережевий диск) повертає помилку тайм-ауту або контрольна сума не збігається, стан чанка скидається з `CHUNK_STATE_MIGRATING` назад у `CHUNK_STATE_ONLINE`, а виділений блок на NVMe залишається недоторканим.
