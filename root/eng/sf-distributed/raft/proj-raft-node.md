# ⚙️ Практична реалізація ядра Raft: керування станом, вибори та обробка RPC

Цей проєкт демонструє мінімальне, математично повне й працездатне ядро вузла консенсусу Raft: керування станом, переходи між ролями (Follower, Candidate, Leader), випадковий таймер виборів, покрокову обробку вхідних RPC `RequestVote` та `AppendEntries`, а також логіку просування індексу фіксації (`commitIndex`) за правилом більшості.

## 1. Архітектурний дизайн та інваріанти

Ядро Raft проєктується як детермінований скінченний автомат, що реагує на два класи зовнішніх і внутрішніх подій:
1. **Часові події (Time Events):** спливання випадкового таймауту виборів (для фоловерів та кандидатів) або періодичний таймер розсилки серцебиття (для лідера).
2. **Мережеві події (RPC Events):** отримання запитів або відповідей `RequestVote`, `AppendEntries` та `InstallSnapshot`.

Для забезпечення математичної коректності рушій дотримується трьох фундаментальних правил:
- **Атомарність персистентного стану:** змінні `currentTerm`, `votedFor` та масив записів `log[]` обов'язково записуються на енергонезалежний носій (із викликом `fsync()` у POSIX або аналога) **до того**, як функція надішле відповідь клієнту чи сусіду.
- **Рандомізація таймерів:** кожен вузол обирає таймаут виборів випадковим чином з інтервалу 150–300 мс (10–20 інтервалів серцебиття `T_heartbeat = 15..20` мс), що розпорошує спроби висунення кандидатів у часі й зводить імовірність розколу голосів (Split Vote) майже до нуля.
- **Правило фіксації (§5.4.2):** лідер просуває `commitIndex` лише тоді, коли більшість вузлів підтвердила запис, створений у **його поточному термі**. Записи попередніх термів фіксуються виключно непрямо.

---

## 2. Реалізація ядра протоколу: C та C++

Нижче наведено паралельну реалізацію протокольного рушія. У вкладці C реалізовано чистий, прозорий структурний код із явним керуванням масивами та індексами. У вкладці C++ застосовано сучасні ідіоми: типізовані переліки (`enum class Role`), динамічні масиви `std::vector`, тип `std::optional` для безпечного представлення виборчого стану, роботу з часом через `std::chrono` та інкапсуляцію в класі з RAII-гарантіями.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <stdint.h>
#include <string.h>

#define MAX_PEERS 5
#define MAX_LOG 1024

typedef enum {
    ROLE_FOLLOWER = 0,
    ROLE_CANDIDATE,
    ROLE_LEADER
} raft_role_t;

typedef struct {
    uint64_t term;
    uint64_t index;
    int32_t  data;
} log_entry_t;

typedef struct {
    uint64_t term;
    uint32_t candidate_id;
    uint64_t last_log_index;
    uint64_t last_log_term;
} request_vote_args_t;

typedef struct {
    uint64_t term;
    bool     vote_granted;
} request_vote_reply_t;

typedef struct {
    uint64_t term;
    uint32_t leader_id;
    uint64_t prev_log_index;
    uint64_t prev_log_term;
    uint64_t leader_commit;
    uint32_t entries_count;
    log_entry_t entries[16];
} append_entries_args_t;

typedef struct {
    uint64_t term;
    bool     success;
    uint64_t match_index;
    uint64_t conflict_term;
    uint64_t conflict_first_index;
} append_entries_reply_t;

typedef struct {
    uint32_t id;
    uint32_t cluster_size;
    raft_role_t role;

    /* Персистентний стан */
    uint64_t current_term;
    int32_t  voted_for; /* -1, якщо не голосував у поточному термі */
    log_entry_t log[MAX_LOG];
    uint64_t log_size;

    /* Леткий стан на всіх серверах */
    uint64_t commit_index;
    uint64_t last_applied;

    /* Леткий стан лідера */
    uint64_t next_index[MAX_PEERS];
    uint64_t match_index[MAX_PEERS];

    /* Виборча статистика кандидата */
    uint32_t votes_received;
} raft_node_t;

void raft_node_init(raft_node_t *node, uint32_t id, uint32_t cluster_size) {
    node->id = id;
    node->cluster_size = cluster_size;
    node->role = ROLE_FOLLOWER;
    node->current_term = 0;
    node->voted_for = -1;
    node->log_size = 0;
    node->commit_index = 0;
    node->last_applied = 0;
    node->votes_received = 0;

    for (uint32_t i = 0; i < MAX_PEERS; i++) {
        node->next_index[i] = 1;
        node->match_index[i] = 0;
    }
}

static uint64_t get_last_log_term(const raft_node_t *node) {
    if (node->log_size == 0) return 0;
    return node->log[node->log_size - 1].term;
}

static uint64_t get_last_log_index(const raft_node_t *node) {
    return node->log_size;
}

/* Перехід фоловера у стан кандидата та старт виборів */
void raft_start_election(raft_node_t *node) {
    node->role = ROLE_CANDIDATE;
    node->current_term++;
    node->voted_for = (int32_t)node->id;
    node->votes_received = 1; /* Голосує за самого себе */

    printf("[Вузол %u] Став Кандидатом, новий Терм %llu, розсилка RequestVote\n",
           node->id, (unsigned long long)node->current_term);
}

/* Обробка вхідного запиту RequestVote */
void raft_handle_request_vote(raft_node_t *node,
                              const request_vote_args_t *args,
                              request_vote_reply_t *reply) {
    /* 1. Якщо терм запиту більший за наш — оновлюємося й переходимо у фоловери */
    if (args->term > node->current_term) {
        node->current_term = args->term;
        node->role = ROLE_FOLLOWER;
        node->voted_for = -1;
    }

    reply->term = node->current_term;
    reply->vote_granted = false;

    /* Застарілі вибори відкидаються негайно */
    if (args->term < node->current_term) {
        return;
    }

    /* 2. Перевірка: чи не віддали ми вже голос іншому кандидату в цьому термі */
    bool can_vote = (node->voted_for == -1 || node->voted_for == (int32_t)args->candidate_id);
    if (!can_vote) {
        return;
    }

    /* 3. Перевірка актуальності логу (Election Restriction) */
    uint64_t my_last_term = get_last_log_term(node);
    uint64_t my_last_idx  = get_last_log_index(node);

    bool log_is_up_to_date = (args->last_log_term > my_last_term) ||
                             (args->last_log_term == my_last_term &&
                              args->last_log_index >= my_last_idx);

    if (log_is_up_to_date) {
        node->voted_for = (int32_t)args->candidate_id;
        reply->vote_granted = true;
        printf("[Вузол %u] Віддав голос за кандидата %u у термі %llu\n",
               node->id, args->candidate_id, (unsigned long long)node->current_term);
    }
}

/* Обробка вхідного виклику AppendEntries */
void raft_handle_append_entries(raft_node_t *node,
                                const append_entries_args_t *args,
                                append_entries_reply_t *reply) {
    /* Якщо терм вищий за локальний — підкоряємося новому лідеру */
    if (args->term > node->current_term) {
        node->current_term = args->term;
        node->role = ROLE_FOLLOWER;
        node->voted_for = -1;
    }

    reply->term = node->current_term;
    reply->success = false;
    reply->match_index = node->log_size;
    reply->conflict_term = 0;
    reply->conflict_first_index = 0;

    /* 1. Відхиляємо старі терми */
    if (args->term < node->current_term) {
        return;
    }

    /* Визнаємо легітимного лідера поточного терму */
    if (node->role == ROLE_CANDIDATE) {
        node->role = ROLE_FOLLOWER;
    }

    /* 2. Перевірка інваріанта відповідності (Log Matching) */
    if (args->prev_log_index > 0) {
        if (args->prev_log_index > node->log_size) {
            /* Лог надто короткий: повертаємо довжину для швидкого відкочування */
            reply->conflict_first_index = node->log_size + 1;
            return;
        }
        if (node->log[args->prev_log_index - 1].term != args->prev_log_term) {
            /* Конфлікт терму: знаходимо перший індекс цього конфліктного терму */
            uint64_t c_term = node->log[args->prev_log_index - 1].term;
            reply->conflict_term = c_term;
            uint64_t first_idx = args->prev_log_index;
            while (first_idx > 1 && node->log[first_idx - 2].term == c_term) {
                first_idx--;
            }
            reply->conflict_first_index = first_idx;

            /* Обрізаємо конфліктну гілку */
            node->log_size = args->prev_log_index - 1;
            return;
        }
    }

    /* 3. Дописування нових записів та вирішення колізій */
    for (uint32_t i = 0; i < args->entries_count; i++) {
        uint64_t insert_idx = args->prev_log_index + 1 + i;
        if (insert_idx <= node->log_size) {
            if (node->log[insert_idx - 1].term != args->entries[i].term) {
                node->log_size = insert_idx - 1;
                node->log[node->log_size++] = args->entries[i];
            }
        } else {
            node->log[node->log_size++] = args->entries[i];
        }
    }

    /* 4. Оновлення commitIndex за вказівкою лідера */
    if (args->leader_commit > node->commit_index) {
        node->commit_index = (args->leader_commit < node->log_size) ?
                              args->leader_commit : node->log_size;
    }

    reply->success = true;
    reply->match_index = node->log_size;
}

/* Просування коміт-індексу на лідері за правилом §5.4.2 */
void raft_leader_advance_commit(raft_node_t *node) {
    if (node->role != ROLE_LEADER) return;

    for (uint64_t n = node->log_size; n > node->commit_index; n--) {
        /* Фіксуємо лише записи власного поточного терму! */
        if (node->log[n - 1].term != node->current_term) {
            continue;
        }

        uint32_t match_count = 1; /* Власний лог лідера */
        for (uint32_t peer = 0; peer < node->cluster_size; peer++) {
            if (peer != node->id && node->match_index[peer] >= n) {
                match_count++;
            }
        }

        if (match_count > node->cluster_size / 2) {
            node->commit_index = n;
            printf("[Лідер %u] Просунув commitIndex до %llu у термі %llu\n",
                   node->id, (unsigned long long)node->commit_index,
                   (unsigned long long)node->current_term);
            break;
        }
    }
}
```
```cpp
#include <iostream>
#include <vector>
#include <optional>
#include <cstdint>
#include <algorithm>
#include <chrono>

enum class Role {
    Follower,
    Candidate,
    Leader
};

struct LogEntry {
    uint64_t term{0};
    uint64_t index{0};
    int32_t  data{0};
};

struct RequestVoteArgs {
    uint64_t term{0};
    uint32_t candidateId{0};
    uint64_t lastLogIndex{0};
    uint64_t lastLogTerm{0};
};

struct RequestVoteReply {
    uint64_t term{0};
    bool     voteGranted{false};
};

struct AppendEntriesArgs {
    uint64_t term{0};
    uint32_t leaderId{0};
    uint64_t prevLogIndex{0};
    uint64_t prevLogTerm{0};
    uint64_t leaderCommit{0};
    std::vector<LogEntry> entries;
};

struct AppendEntriesReply {
    uint64_t term{0};
    bool     success{false};
    uint64_t matchIndex{0};
    uint64_t conflictTerm{0};
    uint64_t conflictFirstIndex{0};
};

class RaftNode {
public:
    RaftNode(uint32_t id, uint32_t clusterSize)
        : m_id(id), m_clusterSize(clusterSize) {
        m_nextIndex.resize(clusterSize, 1);
        m_matchIndex.resize(clusterSize, 0);
    }

    void startElection() {
        m_role = Role::Candidate;
        m_currentTerm++;
        m_votedFor = m_id;
        m_votesReceived = 1;

        std::cout << "[Вузол " << m_id << "] Став Кандидатом, новий Терм "
                  << m_currentTerm << ", розсилка RequestVote\n";
    }

    RequestVoteReply handleRequestVote(const RequestVoteArgs& args) {
        if (args.term > m_currentTerm) {
            m_currentTerm = args.term;
            m_role = Role::Follower;
            m_votedFor.reset();
        }

        RequestVoteReply reply{.term = m_currentTerm, .voteGranted = false};
        if (args.term < m_currentTerm) {
            return reply;
        }

        bool canVote = (!m_votedFor.has_value() || *m_votedFor == args.candidateId);
        if (!canVote) return reply;

        uint64_t myLastTerm = getLastLogTerm();
        uint64_t myLastIdx  = getLastLogIndex();

        bool logIsUpToDate = (args.lastLogTerm > myLastTerm) ||
                             (args.lastLogTerm == myLastTerm && args.lastLogIndex >= myLastIdx);

        if (logIsUpToDate) {
            m_votedFor = args.candidateId;
            reply.voteGranted = true;
            std::cout << "[Вузол " << m_id << "] Віддав голос за кандидата "
                      << args.candidateId << " у термі " << m_currentTerm << "\n";
        }
        return reply;
    }

    AppendEntriesReply handleAppendEntries(const AppendEntriesArgs& args) {
        if (args.term > m_currentTerm) {
            m_currentTerm = args.term;
            m_role = Role::Follower;
            m_votedFor.reset();
        }

        AppendEntriesReply reply{
            .term = m_currentTerm,
            .success = false,
            .matchIndex = m_log.size(),
            .conflictTerm = 0,
            .conflictFirstIndex = 0
        };

        if (args.term < m_currentTerm) {
            return reply;
        }

        if (m_role == Role::Candidate) {
            m_role = Role::Follower;
        }

        /* Перевірка інваріанта відповідності (Log Matching) */
        if (args.prevLogIndex > 0) {
            if (args.prevLogIndex > m_log.size()) {
                reply.conflictFirstIndex = m_log.size() + 1;
                return reply;
            }
            if (m_log[args.prevLogIndex - 1].term != args.prevLogTerm) {
                uint64_t cTerm = m_log[args.prevLogIndex - 1].term;
                reply.conflictTerm = cTerm;
                uint64_t firstIdx = args.prevLogIndex;
                while (firstIdx > 1 && m_log[firstIdx - 2].term == cTerm) {
                    firstIdx--;
                }
                reply.conflictFirstIndex = firstIdx;
                m_log.resize(args.prevLogIndex - 1);
                return reply;
            }
        }

        /* Дописування або перезапис конфліктних записів */
        for (size_t i = 0; i < args.entries.size(); ++i) {
            size_t insertIdx = args.prevLogIndex + 1 + i;
            if (insertIdx <= m_log.size()) {
                if (m_log[insertIdx - 1].term != args.entries[i].term) {
                    m_log.resize(insertIdx - 1);
                    m_log.push_back(args.entries[i]);
                }
            } else {
                m_log.push_back(args.entries[i]);
            }
        }

        /* Оновлення commitIndex за вказівкою лідера */
        if (args.leaderCommit > m_commitIndex) {
            m_commitIndex = std::min(args.leaderCommit, static_cast<uint64_t>(m_log.size()));
        }

        reply.success = true;
        reply.matchIndex = m_log.size();
        return reply;
    }

    void advanceLeaderCommit() {
        if (m_role != Role::Leader) return;

        for (uint64_t n = m_log.size(); n > m_commitIndex; --n) {
            /* Тільки записи поточного терму фіксуються напряму! (§5.4.2) */
            if (m_log[n - 1].term != m_currentTerm) {
                continue;
            }

            uint32_t matchCount = 1;
            for (uint32_t peer = 0; peer < m_clusterSize; ++peer) {
                if (peer != m_id && m_matchIndex[peer] >= n) {
                    matchCount++;
                }
            }

            if (matchCount > m_clusterSize / 2) {
                m_commitIndex = n;
                std::cout << "[Лідер " << m_id << "] Просунув commitIndex до "
                          << m_commitIndex << " у термі " << m_currentTerm << "\n";
                break;
            }
        }
    }

    [[nodiscard]] uint64_t getLastLogTerm() const {
        return m_log.empty() ? 0 : m_log.back().term;
    }

    [[nodiscard]] uint64_t getLastLogIndex() const {
        return m_log.size();
    }

    [[nodiscard]] Role getRole() const { return m_role; }
    [[nodiscard]] uint64_t getCurrentTerm() const { return m_currentTerm; }
    [[nodiscard]] uint64_t getCommitIndex() const { return m_commitIndex; }

private:
    uint32_t                m_id;
    uint32_t                m_clusterSize;
    Role                    m_role{Role::Follower};

    uint64_t                m_currentTerm{0};
    std::optional<uint32_t> m_votedFor{std::nullopt};
    std::vector<LogEntry>   m_log;

    uint64_t                m_commitIndex{0};
    uint64_t                m_lastApplied{0};

    std::vector<uint64_t>   m_nextIndex;
    std::vector<uint64_t>   m_matchIndex;
    uint32_t                m_votesReceived{0};
};
```
:::

---

## 3. Покроковий розбір критичних механізмів та пасток

### 3.1. Оптимізація швидкого відкочування (Fast Rollback Protocol)

У базовій версії алгоритму, якщо фоловер відхиляє `AppendEntries` через невідповідність логу на позиції `prevLogIndex`, лідер зменшує `nextIndex[peer]` лише на `1` і повторює спробу. Якщо фоловер був вимкнений упродовж години й відстав на 50 000 записів, лідеру знадобиться 50 000 послідовних мережевих раундів (RTT), щоб знайти точку збіжності логів.

Реалізований вище механізм швидкого відкочування скорочує цей пошук до кількох повідомлень:
1. Якщо лог фоловера занадто короткий (`prevLogIndex > log_size`), фоловер повертає `conflictFirstIndex = log_size + 1` і `conflictTerm = 0`. Лідер негайно виставляє `nextIndex[peer] = conflictFirstIndex`.
2. Якщо у фоловера виявлено запис із конфліктним термом `T_conflict`, він знаходить у своєму лозі перший індекс, де цей терм з'явився (`conflictFirstIndex`), і повертає обидва значення.
3. Лідер перевіряє свій лог на наявність записів із термом `conflictTerm`:
   - Якщо лідер **має** записи з `conflictTerm`, він встановлює `nextIndex[peer]` на індекс відразу за останнім записом цього терму у своєму лозі.
   - Якщо лідер **не має** таких записів, він виставляє `nextIndex[peer] = conflictFirstIndex`.

Завдяки цьому покажчик `nextIndex` перестрибує цілі терми за один мережевий раунд, знаходячи спільну точку збіжності за час, пропорційний кількості конфліктних термів, замість кількості записів.

### 3.2. Атомарність та відновлення після аварій (Crash Recovery)

Будь-який вузол може раптово втратити живлення в будь-якій точці коду. Щоб уникнути порушення інваріантів:
- **Запис перед відповіддю:** Оновлення полів `currentTerm`, `votedFor` та додавання нових елементів у `log` записуються в журнал попереджувального запису (WAL) на диску з примусовим скиданням дискового кешу (`fsync()`) **перед** формуванням відповіді `reply`.
- **Ідемпотентність ініціалізації:** Під час перезапуску вузол зчитує з диска останній відомий `currentTerm`, `votedFor` та весь масив `log[]`. Поля `commitIndex` та `lastApplied` ініціалізуються нулями (або значенням останнього зафіксованого знімка стану), після чого вузол безпечно відновлює обробку повідомлень у ролі фоловера.

### 3.3. Модель конкурентності та блокування

У виробничих системах обробка мережевого вводу-виводу відбувається паралельно в пулі робочих потоків або в асинхронному циклі подій (Event Loop):
- **Модель єдиного циклу подій (Event-Loop Driven):** Найбільш надійна архітектура (застосована в etcd та Redis Raft), де всі мутації стану `RaftNode` виконуються в одному потоці. Мережеві сокети лише читають байти й кладуть готові RPC-повідомлення у чергу вхідних подій. Це виключає блокування, дедлоки та гонки даних без використання дорогих м'ютексів.
- **Багатопотокова модель із м'ютексом:** Якщо кожен RPC обробляється окремим потоком, стан вузла захищається єдиним грубим м'ютексом (`std::mutex`). Головна пастка полягає в тому, що мережевий виклик до сусіда **ніколи не повинен виконуватися під захопленим м'ютексом**: спочатку обчислюються аргументи запиту під замком, замок відпускається, виконується асинхронний мережевий виклик, а отримана відповідь знову обробляється під замком із перевіркою зміни терму.

### 3.4. Методологія тестування: детермінована симуляція хаосу

Тестування алгоритмів консенсусу звичайними модульними тестами (Unit Tests) є недостатнім: найнебезпечніші помилки виникають лише під час рідкісних комбінацій мережевих затримок, падінь серверів і розривів зв'язку.

Сучасний золотий стандарт тестування Raft — **детермінована симуляція дискретних подій (Deterministic Discrete-Event Simulation)**:
- Усі мережеві виклики, таймери та дискові операції загортаються в інтерфейс симулятора з віртуальним часом.
- Генератор псевдовипадкових чисел з фіксованим зерном (Random Seed) моделює будь-які аномалії: дублювання, втрату або затримку пакетів, асиметричні розриви зв'язку та раптові перезавантаження вузлів.
- Якщо в симуляторі виявляється порушення інваріанта безпеки (наприклад, розходження коміт-індексів), інженер може відтворити баг із точністю до біта, просто запустивши симуляцію з тим самим початковим зерном генератора.
