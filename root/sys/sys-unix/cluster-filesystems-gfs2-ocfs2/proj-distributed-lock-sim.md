# ⚙️ Симуляція розподіленого менеджера блокувань та когерентності кешу

Цей практичний проєкт демонструє базовий механізм роботи розподіленого менеджера блокувань (*Distributed Lock Manager*, DLM) та координацію локальних кешів сторінок (*page cache coherency*) між двома віртуальними вузлами, що звертаються до спільного блокового буфера. Програма наочно відтворює послідовність асинхронних пасток `BAST` (запит на пониження режиму) та `CAST` (підтвердження надання блокування), а також примусове скидання брудних даних на диск (`flush`) та інвалідацію локального кешу (`invalidate`).

## 1. Архітектурна задача та математична модель станів

У кластерній файловій системі зі спільним диском головна небезпека полягає в асиметрії локальних кешів: якщо Вузол A модифікує блок даних у власній оперативній пам'яті, Вузол B не має апаратного способу дізнатися про цю зміну через звичайну дискову шину. Щоб запобігти зчитуванню застарілих даних (*stale reads*) або затиранню чужих змін (*lost updates*), використовується програмний автомат розподілених блокувань.

### Математичні інваріанти блокувань

Для довільного блокового ресурсу `R` стан визначається кортежем:

```text
State(R) = (GrantedMode, HoldersSet, DirtyNode)
```

де `GrantedMode ∈ {NL, PR, EX}`:

1. **Інваріант ексклюзивності (EX):** якщо `GrantedMode = EX`, то `|HoldersSet| = 1` та жоден інший вузол не має права читати чи писати ресурс;
2. **Інваріант спільного доступу (PR):** якщо `GrantedMode = PR`, то `|HoldersSet| ≥ 1` та всі учасники множини гарантовано володіють актуальними даними, оскільки перед переходом у `PR` будь-який попередній власник `EX` зобов'язаний скинути свій брудний кеш на спільний накопичувач;
3. **Інваріант інвалідації кешу:** якщо вузол не володіє блокуванням (`HeldMode = NL`), його локальний кеш позначається як невалідний (`cache_valid = false`). Перед виконанням читання вузол зобов'язаний отримати `PR` та перечитати блок безпосередньо з диска.

## 2. Архітектурна ідея симуляції

Симуляція моделює спрощену версію поведінки `glock` у GFS2 або `o2dlm` у OCFS2:

1. **Спільний блоковий пристрій** — спільний масив байтів у пам'яті (`shared_storage_t` у C, `SharedStorage` у C++), що симулює диск SAN / iSCSI LUN, захищений м'ютексом доступу;
2. **Менеджер блокувань (DLM Coordinator)** — координатор станів із підтримкою режимів `NL` (*Null*), `PR` (*Protected Read*) та `EX` (*Exclusive*);
3. **Локальні вузли (Node A та Node B)** — кожен вузол має власний локальний кеш (`local_cache`), статус валідності (`cache_valid`), прапорець брудних даних (`cache_dirty`) та поточний режим утримуваного блокування (`held_mode`);
4. **Протокол BAST/CAST:**
   * Коли Вузол B вимагає режим `PR` для читання, а Вузол A утримує `EX` із незбереженими даними, координатор надсилає `BAST` Вузлу A;
   * Вузол A у відповідь на `BAST` виконує еквівалент ядрового виклику `filemap_write_and_wait()`: записує брудний буфер на спільний диск, скидає прапорець `cache_dirty = false` і погоджується на деградацію до `PR`;
   * Координатор надсилає `CAST` Вузлу B, надаючи йому доступ `PR`;
   * Вузол B виявляє `cache_valid == false`, інвалідує старий буфер і завантажує свіжий блок зі спільного диска.

## 3. Реалізація симулятора

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
#include <pthread.h>
#include <unistd.h>

#define BLOCK_SIZE 64

typedef enum {
    LOCK_NL = 0,
    LOCK_PR = 1,
    LOCK_EX = 2
} lock_mode_t;

static const char *mode_str(lock_mode_t m) {
    switch (m) {
        case LOCK_NL: return "NL (Unlocked)";
        case LOCK_PR: return "PR (Protected Read / Shared)";
        case LOCK_EX: return "EX (Exclusive)";
        default:      return "UNKNOWN";
    }
}

/* Спільний блоковий накопичувач */
typedef struct {
    char data[BLOCK_SIZE];
    pthread_mutex_t disk_mutex;
} shared_storage_t;

/* Стан блокування ресурсу в DLM */
typedef struct {
    pthread_mutex_t lock_mutex;
    pthread_cond_t  lock_cv;
    lock_mode_t     granted_mode;
    int             owner_node_id; /* -1 якщо вільно або декілька PR */
    int             pr_holders_count;
} dlm_resource_t;

/* Локальний стан вузла */
typedef struct {
    int              node_id;
    char             local_cache[BLOCK_SIZE];
    bool             cache_valid;
    bool             cache_dirty;
    lock_mode_t      held_mode;
    dlm_resource_t  *res;
    shared_storage_t *disk;
} cluster_node_t;

/* Ініціалізація компонентів */
void storage_init(shared_storage_t *s) {
    memset(s->data, 0, BLOCK_SIZE);
    snprintf(s->data, BLOCK_SIZE, "Початкові дані на диску");
    pthread_mutex_init(&s->disk_mutex, NULL);
}

void dlm_init(dlm_resource_t *res) {
    pthread_mutex_init(&res->lock_mutex, NULL);
    pthread_cond_init(&res->lock_cv, NULL);
    res->granted_mode = LOCK_NL;
    res->owner_node_id = -1;
    res->pr_holders_count = 0;
}

void node_init(cluster_node_t *node, int id, dlm_resource_t *res, shared_storage_t *disk) {
    node->node_id = id;
    memset(node->local_cache, 0, BLOCK_SIZE);
    node->cache_valid = false;
    node->cache_dirty = false;
    node->held_mode = LOCK_NL;
    node->res = res;
    node->disk = disk;
}

/* Обробник BAST (Blocking AST): примусове скидання кешу та пониження режиму */
void handle_bast(cluster_node_t *node, lock_mode_t requested_mode) {
    printf("[Вузол %d] << Отримано BAST: інший вузол вимагає %s >>\n",
           node->node_id, mode_str(requested_mode));

    if (node->cache_dirty) {
        printf("[Вузол %d] BAST: Скидання брудного кешу на диск: \"%s\"\n",
               node->node_id, node->local_cache);
        pthread_mutex_lock(&node->disk->disk_mutex);
        memcpy(node->disk->data, node->local_cache, BLOCK_SIZE);
        pthread_mutex_unlock(&node->disk->disk_mutex);
        node->cache_dirty = false;
    }

    if (requested_mode == LOCK_PR && node->held_mode == LOCK_EX) {
        printf("[Вузол %d] BAST: Добровільне пониження блокування EX -> PR\n", node->node_id);
        node->held_mode = LOCK_PR;
    } else if (requested_mode == LOCK_EX) {
        printf("[Вузол %d] BAST: Повна інвалідація кешу та звільнення до NL\n", node->node_id);
        node->held_mode = LOCK_NL;
        node->cache_valid = false;
    }
}

/* Запит на отримання блокування через DLM */
void dlm_acquire(cluster_node_t *node, lock_mode_t target_mode, cluster_node_t *other_node) {
    pthread_mutex_lock(&node->res->lock_mutex);

    printf("[Вузол %d] Запит блокування %s (поточний утримуваний: %s)\n",
           node->node_id, mode_str(target_mode), mode_str(node->held_mode));

    while (1) {
        if (target_mode == LOCK_PR) {
            if (node->res->granted_mode == LOCK_NL || node->res->granted_mode == LOCK_PR) {
                node->res->granted_mode = LOCK_PR;
                node->res->pr_holders_count++;
                node->held_mode = LOCK_PR;
                printf("[Вузол %d] >> CAST: Надано режим PR (читачів: %d) <<\n",
                       node->node_id, node->res->pr_holders_count);
                break;
            } else if (node->res->granted_mode == LOCK_EX) {
                /* Конфлікт: викликаємо BAST на власнику EX */
                printf("[DLM] Конфлікт! Виклик BAST на Вузлі %d\n", other_node->node_id);
                handle_bast(other_node, LOCK_PR);
                node->res->granted_mode = LOCK_PR;
                node->res->owner_node_id = -1;
                node->res->pr_holders_count = 1; /* Вузол A понизився до PR */
                node->res->pr_holders_count++;   /* Вузол B отримує PR */
                node->held_mode = LOCK_PR;
                printf("[Вузол %d] >> CAST: Надано режим PR після деградації EX <<\n", node->node_id);
                break;
            }
        } else if (target_mode == LOCK_EX) {
            if (node->res->granted_mode == LOCK_NL) {
                node->res->granted_mode = LOCK_EX;
                node->res->owner_node_id = node->node_id;
                node->held_mode = LOCK_EX;
                printf("[Вузол %d] >> CAST: Надано режим EX <<\n", node->node_id);
                break;
            } else {
                /* Конфлікт із PR або чужим EX */
                printf("[DLM] Конфлікт для EX! Виклик BAST на Вузлі %d\n", other_node->node_id);
                handle_bast(other_node, LOCK_EX);
                node->res->granted_mode = LOCK_EX;
                node->res->owner_node_id = node->node_id;
                node->res->pr_holders_count = 0;
                node->held_mode = LOCK_EX;
                printf("[Вузол %d] >> CAST: Надано режим EX після витіснення <<\n", node->node_id);
                break;
            }
        }
        pthread_cond_wait(&node->res->lock_cv, &node->res->lock_mutex);
    }

    pthread_mutex_unlock(&node->res->lock_mutex);
}

/* Операції запису та читання */
void node_write(cluster_node_t *node, const char *new_text, cluster_node_t *other_node) {
    printf("\n--- [Вузол %d] Початок операції WRITE(\"%s\") ---\n", node->node_id, new_text);
    if (node->held_mode != LOCK_EX) {
        dlm_acquire(node, LOCK_EX, other_node);
    }
    snprintf(node->local_cache, BLOCK_SIZE, "%s", new_text);
    node->cache_valid = true;
    node->cache_dirty = true;
    printf("[Вузол %d] Запис у локальний Page Cache виконано (cache_dirty = true)\n", node->node_id);
}

void node_read(cluster_node_t *node, cluster_node_t *other_node) {
    printf("\n--- [Вузол %d] Початок операції READ() ---\n", node->node_id);
    if (node->held_mode == LOCK_NL) {
        dlm_acquire(node, LOCK_PR, other_node);
    }
    if (!node->cache_valid) {
        printf("[Вузол %d] Кеш невалідний! Читання блоку з фізичного LUN...\n", node->node_id);
        pthread_mutex_lock(&node->disk->disk_mutex);
        memcpy(node->local_cache, node->disk->data, BLOCK_SIZE);
        pthread_mutex_unlock(&node->disk->disk_mutex);
        node->cache_valid = true;
    } else {
        printf("[Вузол %d] Використання валідного локального кешу сторінок (RAM Hit)\n", node->node_id);
    }
    printf("[Вузол %d] Прочитані дані: \"%s\"\n", node->node_id, node->local_cache);
}

int main(void) {
    shared_storage_t disk;
    dlm_resource_t   res;
    cluster_node_t   node_a, node_b;

    storage_init(&disk);
    dlm_init(&res);
    node_init(&node_a, 1, &res, &disk);
    node_init(&node_b, 2, &res, &disk);

    printf("=== СТАРТ СИМУЛЯЦІЇ SHARED-DISK ТА DLM ===\n");

    /* Сценарій:
       1. Вузол A пише нові дані (захоплює EX, кешує в RAM без негайного скидання).
       2. Вузол B намагається прочитати дані (запитує PR).
       3. DLM ініціює BAST на Вузлі A -> Вузол A скидає кеш на диск -> DLM надає PR Вузлу B.
       4. Вузол B інвалідує свій кеш і читає свіжі дані з диска. */

    node_write(&node_a, "Оновлення блоку 42 від Вузла 1", &node_b);
    node_read(&node_b, &node_a);

    printf("\n=== ЗАВЕРШЕННЯ СИМУЛЯЦІЇ ===\n");
    return 0;
}
```
```cpp
#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <memory>
#include <mutex>
#include <condition_variable>
#include <array>
#include <format>

constexpr size_t BLOCK_SIZE = 64;

enum class LockMode {
    Null = 0,
    ProtectedRead = 1,
    Exclusive = 2
};

std::string_view to_string(LockMode mode) {
    switch (mode) {
        case LockMode::Null:          return "NL (Unlocked)";
        case LockMode::ProtectedRead: return "PR (Protected Read / Shared)";
        case LockMode::Exclusive:     return "EX (Exclusive)";
    }
    return "Unknown";
}

/* Спільне блокове сховище */
class SharedStorage {
public:
    SharedStorage() {
        std::string initial = "Початкові дані на диску";
        std::copy(initial.begin(), initial.end(), data_.begin());
    }

    void write_block(std::string_view src) {
        std::lock_guard<std::mutex> lock(mutex_);
        data_.fill(0);
        auto len = std::min(src.size(), BLOCK_SIZE - 1);
        std::copy_n(src.data(), len, data_.begin());
    }

    std::string read_block() const {
        std::lock_guard<std::mutex> lock(mutex_);
        return std::string(data_.data());
    }

private:
    mutable std::mutex mutex_;
    std::array<char, BLOCK_SIZE> data_{};
};

class ClusterNode;

/* Розподілений координатор блокувань */
class DlmCoordinator {
public:
    void acquire(ClusterNode& requester, LockMode target, ClusterNode& other);

private:
    std::mutex dlm_mutex_;
    std::condition_variable cv_;
    LockMode granted_mode_{LockMode::Null};
    int owner_node_id_{-1};
    int pr_holders_{0};
};

/* Вузол кластера */
class ClusterNode {
public:
    ClusterNode(int id, std::shared_ptr<SharedStorage> disk, std::shared_ptr<DlmCoordinator> dlm)
        : node_id_(id), disk_(std::move(disk)), dlm_(std::move(dlm)) {}

    int id() const noexcept { return node_id_; }
    LockMode held_mode() const noexcept { return held_mode_; }

    void handle_bast(LockMode requested) {
        std::cout << std::format("[Вузол {}] << Отримано BAST: потрібен режим {} >>\n",
                                 node_id_, to_string(requested));

        if (cache_dirty_) {
            std::cout << std::format("[Вузол {}] BAST: Скидання брудного кешу на диск: \"{}\"\n",
                                     node_id_, local_cache_);
            disk_->write_block(local_cache_);
            cache_dirty_ = false;
        }

        if (requested == LockMode::ProtectedRead && held_mode_ == LockMode::Exclusive) {
            std::cout << std::format("[Вузол {}] BAST: Добровільне пониження блокування EX -> PR\n", node_id_);
            held_mode_ = LockMode::ProtectedRead;
        } else if (requested == LockMode::Exclusive) {
            std::cout << std::format("[Вузол {}] BAST: Інвалідація кешу та звільнення до NL\n", node_id_);
            held_mode_ = LockMode::Null;
            cache_valid_ = false;
        }
    }

    void set_granted(LockMode mode) {
        held_mode_ = mode;
    }

    void write(std::string_view new_data, ClusterNode& other) {
        std::cout << std::format("\n--- [Вузол {}] Початок операції WRITE(\"{}\") ---\n", node_id_, new_data);
        if (held_mode_ != LockMode::Exclusive) {
            dlm_->acquire(*this, LockMode::Exclusive, other);
        }
        local_cache_ = std::string(new_data);
        cache_valid_ = true;
        cache_dirty_ = true;
        std::cout << std::format("[Вузол {}] Запис у локальний Page Cache (cache_dirty = true)\n", node_id_);
    }

    void read(ClusterNode& other) {
        std::cout << std::format("\n--- [Вузол {}] Початок операції READ() ---\n", node_id_);
        if (held_mode_ == LockMode::Null) {
            dlm_->acquire(*this, LockMode::ProtectedRead, other);
        }
        if (!cache_valid_) {
            std::cout << std::format("[Вузол {}] Кеш невалідний! Читання блоку з LUN...\n", node_id_);
            local_cache_ = disk_->read_block();
            cache_valid_ = true;
        } else {
            std::cout << std::format("[Вузол {}] Використання локального кешу сторінок (RAM Hit)\n", node_id_);
        }
        std::cout << std::format("[Вузол {}] Прочитані дані: \"{}\"\n", node_id_, local_cache_);
    }

private:
    int node_id_;
    std::shared_ptr<SharedStorage> disk_;
    std::shared_ptr<DlmCoordinator> dlm_;
    std::string local_cache_;
    bool cache_valid_{false};
    bool cache_dirty_{false};
    LockMode held_mode_{LockMode::Null};
};

void DlmCoordinator::acquire(ClusterNode& requester, LockMode target, ClusterNode& other) {
    std::unique_lock<std::mutex> lock(dlm_mutex_);

    std::cout << std::format("[Вузол {}] Запит блокування {} (поточний: {})\n",
                             requester.id(), to_string(target), to_string(requester.held_mode()));

    if (target == LockMode::ProtectedRead) {
        if (granted_mode_ == LockMode::Exclusive) {
            std::cout << std::format("[DLM] Конфлікт! Виклик BAST на Вузлі {}\n", other.id());
            other.handle_bast(LockMode::ProtectedRead);
            granted_mode_ = LockMode::ProtectedRead;
            owner_node_id_ = -1;
            pr_holders_ = 2; // Обидва вузли мають PR
        } else {
            granted_mode_ = LockMode::ProtectedRead;
            ++pr_holders_;
        }
        requester.set_granted(LockMode::ProtectedRead);
        std::cout << std::format("[Вузол {}] >> CAST: Надано режим PR (читачів: {}) <<\n",
                                 requester.id(), pr_holders_);
    } else if (target == LockMode::Exclusive) {
        if (granted_mode_ != LockMode::Null) {
            std::cout << std::format("[DLM] Конфлікт для EX! Виклик BAST на Вузлі {}\n", other.id());
            other.handle_bast(LockMode::Exclusive);
        }
        granted_mode_ = LockMode::Exclusive;
        owner_node_id_ = requester.id();
        pr_holders_ = 0;
        requester.set_granted(LockMode::Exclusive);
        std::cout << std::format("[Вузол {}] >> CAST: Надано режим EX <<\n", requester.id());
    }
}

int main() {
    auto storage = std::make_shared<SharedStorage>();
    auto dlm = std::make_shared<DlmCoordinator>();

    ClusterNode node_a(1, storage, dlm);
    ClusterNode node_b(2, storage, dlm);

    std::cout << "=== СТАРТ СИМУЛЯЦІЇ SHARED-DISK ТА DLM (C++20) ===\n";

    node_a.write("Оновлення блоку 42 від Вузла 1", node_b);
    node_b.read(node_a);

    std::cout << "\n=== ЗАВЕРШЕННЯ СИМУЛЯЦІЇ ===\n";
    return 0;
}
```
:::

## 4. Покроковий розбір трасування виконання

Аналіз консольного виводу симуляції показує точну послідовність зміни станів компонентів:

1. **Фаза 1: Запис на Вузлі 1.** Вузол 1 ініціює `write("Оновлення блоку 42 від Вузла 1")`. Оскільки поточний режим `held_mode == LOCK_NL`, вузол надсилає запит на `LOCK_EX` до DLM. Оскільки ресурс вільний, DLM повертає `CAST` негайно. Вузол 1 записує текст у `local_cache`, встановлює `cache_valid = true` та `cache_dirty = true`. Звернення до `shared_disk` **не відбувається**: дані живуть виключно в RAM Вузла 1;
2. **Фаза 2: Конкурентне читання на Вузлі 2.** Вузол 2 викликає `read()`. Маючи `held_mode == LOCK_NL`, він надсилає до DLM запит на `LOCK_PR`. DLM виявляє, що ресурс утримується Вузлом 1 у режимі `LOCK_EX`. Напряму задовольнити запит неможливо, тому DLM активує пастку `BAST` на Вузлі 1;
3. **Фаза 3: Обробка BAST та скидання кешу.** Вузол 1 у функції `handle_bast()` бачить `cache_dirty == true`. Він блокує `disk_mutex` і копіює свій `local_cache` у фізичний `shared_disk`. Після цього прапорець `cache_dirty` скидається, а режим блокування добровільно деградує до `LOCK_PR`;
4. **Фаза 4: Завершення блокування та інвалідація.** DLM фіксує перехід ресурсу в стан `LOCK_PR` з двома читачами й надсилає `CAST` Вузлу 2. Вузол 2 перевіряє `cache_valid`: оскільки кеш невалідний, він зчитує щойно записаний блок безпосередньо зі `shared_disk`, оновлює свій `local_cache`, позначає його валідним і повертає коректні дані читачеві.

## 5. Розбір крайових ситуацій та підводних каменів

Під час експлуатації реальних кластерних файлових систем виникають складні граничні ситуації, які вимагають додаткових архітектурних рішень:

1. **Затримка відповіді на BAST (Deadlock / Starvation):** якщо потік на Вузлі A зависне під час виконання скидання сторінок на диск (наприклад, через перевантаження черги дискового HBA чи затримку пам'яті), Вузол B не зможе отримати блокування й заблокує відповідний системний виклик у ядрі. У реальних DLM для запобігання вічному блокуванню застосовують сторожові таймери (*watchdogs*), які примусово вилучають вузол з кластера через процедуру fencing;
2. **Пінг-понг блокувань (Lock Bouncing):** якщо обидва вузли виконуватимуть цикл `write()` у той самий блок почергово, кожен запис провокуватиме BAST, повне скидання кешу та відкликання прав. Продуктивність впаде з сотень тисяч операцій на секунду до кількох десятків (затримка визначатиметься сумою часу передачі пакетів мережею та синхронного запису на диск);
3. **Падіння вузла під час обробки BAST:** якщо Вузол A отримує сповіщення BAST, розпочинає скидання сторінок на диск і зазнає паніки ядра до завершення запису, DLM виявляє втрату зв'язку через інтерконнект. У цей момент ресурс блокується у спеціальному стані відновлення (*recovery state*), доки живий Вузол B не виконає фехтування мертвого вузла та не програє його журнал транзакцій;
4. **Конкуренція конверсій у черзі (Conversion Deadlock):** якщо два вузли одночасно утримують режим `PR` і обидва намагаються підвищити свій рівень до `EX` (`PR -> EX`), жоден із них не може отримати монополію, оскільки сусід утримує `PR`. Для розв'язання цієї колізії DLM реалізує пріоритет черги конверсій (*Convert Queue*) та алгоритм відкату транзакцій із поверненням помилки `-EDEADLK`.
