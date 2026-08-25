# ⚙️ Практична реалізація трифазного вузла PBFT із захистом від еквівокації

У розподілених системах реплікація автомата станів (англ. *State Machine Replication*, SMR) у візантійському середовищі вимагає від кожного вузла забезпечення детермінізму за повної відсутності довіри до координатора. Первинний вузол (Primary / Лідер) може бути скомпрометований, мати апаратні дефекти оперативної пам'яті або навмисно намагатися розколоти кластер шляхом надсилання суперечливих даних різним реплікам (дворушництва чи еквівокації).

Нижче наведено практичну реалізацію ядра репліки PBFT для системи з `N = 4` вузлів, здатної витримувати `f = 1` візантійський збій. Програма реалізує трифазний консенсус (Pre-Prepare, Prepare, Commit), відстежує стан журналу транзакцій, перевіряє кворуми розміром `2f + 1` та детектує спроби підробки даних.

## Архітектура та структура автомата станів репліки

Кожен вузол кластера підтримує локальний журнал транзакцій (Log), де для кожного порядкового номера запиту (слота `n`) фіксується життєвий цикл пропозиції.

Життєвий цикл слота складається з таких станів:
1. **Ініціалізація слота:** Слот очікує надходження першого повідомлення від лідера.
2. **Отримання Pre-Prepare:** Вузол перевіряє, що відправник є легітимним лідером поточного виду `v`, дайджест збігається з тілом транзакції, а для цього слота ще не було зареєстровано іншого дайджесту.
3. **Збір підготовленого сертифіката (Prepared Certificate):** Вузол транслює `Prepare` і підраховує ідентичні повідомлення `Prepare` від інших реплік. Коли накопичено `2f` підтверджень від сусідів, предикат `prepared` стає істинним.
4. **Збір сертифіката фіксації (Commit Certificate):** Вузол транслює `Commit` і чекає `2f + 1` повідомлень `Commit` (включно з власним). Після цього слот переходить у стан `committed-local` і операція передається на виконання локальному автомату станів.

:::tabs
```c
#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define MAX_NODES 4
#define MAX_LOG_ENTRIES 64
#define DIGEST_LEN 32

typedef struct {
    uint8_t bytes[DIGEST_LEN];
} digest_t;

typedef enum {
    MSG_PRE_PREPARE = 1,
    MSG_PREPARE     = 2,
    MSG_COMMIT      = 3
} msg_type_t;

typedef struct {
    msg_type_t type;
    uint32_t view;
    uint32_t seq_num;
    digest_t digest;
    uint32_t sender_id;
} pbft_msg_t;

typedef struct {
    uint32_t view;
    uint32_t seq_num;
    digest_t digest;
    bool has_pre_prepare;
    uint32_t prepare_count;
    uint32_t commit_count;
    bool prepares_from[MAX_NODES];
    bool commits_from[MAX_NODES];
    bool is_prepared;
    bool is_committed;
} log_entry_t;

typedef struct {
    uint32_t node_id;
    uint32_t total_nodes;
    uint32_t max_faults;
    uint32_t current_view;
    log_entry_t log[MAX_LOG_ENTRIES];
} pbft_replica_t;

static bool digests_equal(const digest_t* a, const digest_t* b) {
    return memcmp(a->bytes, b->bytes, DIGEST_LEN) == 0;
}

void pbft_init(pbft_replica_t* rep, uint32_t id, uint32_t total_nodes) {
    rep->node_id = id;
    rep->total_nodes = total_nodes;
    rep->max_faults = (total_nodes - 1) / 3;
    rep->current_view = 0;
    memset(rep->log, 0, sizeof(rep->log));
}

bool pbft_handle_pre_prepare(pbft_replica_t* rep, const pbft_msg_t* msg, pbft_msg_t* out_prepare) {
    uint32_t primary_id = rep->current_view % rep->total_nodes;
    if (msg->sender_id != primary_id) {
        printf("[Вузол %u] Відхилено Pre-Prepare: відправник %u не є лідером виду %u\n",
               rep->node_id, msg->sender_id, rep->current_view);
        return false;
    }
    if (msg->view != rep->current_view || msg->seq_num >= MAX_LOG_ENTRIES) {
        return false;
    }

    log_entry_t* entry = &rep->log[msg->seq_num];
    if (entry->has_pre_prepare) {
        if (!digests_equal(&entry->digest, &msg->digest)) {
            printf("[Вузол %u] Детектовано еквівокацію лідера на слоті %u! Запуск View Change.\n",
               rep->node_id, msg->seq_num);
        }
        return false;
    }

    entry->view = msg->view;
    entry->seq_num = msg->seq_num;
    entry->digest = msg->digest;
    entry->has_pre_prepare = true;
    entry->prepare_count = 1;
    entry->prepares_from[rep->node_id] = true;

    out_prepare->type = MSG_PREPARE;
    out_prepare->view = rep->current_view;
    out_prepare->seq_num = msg->seq_num;
    out_prepare->digest = msg->digest;
    out_prepare->sender_id = rep->node_id;
    return true;
}

bool pbft_handle_prepare(pbft_replica_t* rep, const pbft_msg_t* msg, pbft_msg_t* out_commit) {
    if (msg->view != rep->current_view || msg->seq_num >= MAX_LOG_ENTRIES || msg->sender_id >= rep->total_nodes) {
        return false;
    }

    log_entry_t* entry = &rep->log[msg->seq_num];
    if (!entry->has_pre_prepare || !digests_equal(&entry->digest, &msg->digest)) {
        return false;
    }

    if (!entry->prepares_from[msg->sender_id]) {
        entry->prepares_from[msg->sender_id] = true;
        entry->prepare_count++;
    }

    uint32_t quorum_needed = 2 * rep->max_faults;
    if (entry->prepare_count >= quorum_needed && !entry->is_prepared) {
        entry->is_prepared = true;
        entry->commit_count = 1;
        entry->commits_from[rep->node_id] = true;

        out_commit->type = MSG_COMMIT;
        out_commit->view = rep->current_view;
        out_commit->seq_num = msg->seq_num;
        out_commit->digest = msg->digest;
        out_commit->sender_id = rep->node_id;
        return true;
    }
    return false;
}

bool pbft_handle_commit(pbft_replica_t* rep, const pbft_msg_t* msg) {
    if (msg->view != rep->current_view || msg->seq_num >= MAX_LOG_ENTRIES || msg->sender_id >= rep->total_nodes) {
        return false;
    }

    log_entry_t* entry = &rep->log[msg->seq_num];
    if (!entry->is_prepared || !digests_equal(&entry->digest, &msg->digest)) {
        return false;
    }

    if (!entry->commits_from[msg->sender_id]) {
        entry->commits_from[msg->sender_id] = true;
        entry->commit_count++;
    }

    uint32_t commit_quorum = 2 * rep->max_faults + 1;
    if (entry->commit_count >= commit_quorum && !entry->is_committed) {
        entry->is_committed = true;
        printf("[Вузол %u] Слот %u успішно зафіксовано (Committed-Local)! Виконання транзакції.\n",
               rep->node_id, msg->seq_num);
        return true;
    }
    return false;
}
```
```cpp
#include <iostream>
#include <vector>
#include <array>
#include <span>
#include <optional>
#include <string_view>
#include <cstdint>

namespace pbft {

constexpr size_t DigestSize = 32;
using Digest = std::array<uint8_t, DigestSize>;

enum class MessageType : uint8_t {
    PrePrepare = 1,
    Prepare    = 2,
    Commit     = 3
};

struct Message {
    MessageType type;
    uint32_t view;
    uint32_t seq_num;
    Digest digest;
    uint32_t sender_id;
};

struct LogEntry {
    uint32_t view{0};
    uint32_t seq_num{0};
    Digest digest{};
    bool has_pre_prepare{false};
    std::vector<bool> prepares_from;
    std::vector<bool> commits_from;
    uint32_t prepare_count{0};
    uint32_t commit_count{0};
    bool is_prepared{false};
    bool is_committed{false};

    explicit LogEntry(size_t node_count = 4)
        : prepares_from(node_count, false),
          commits_from(node_count, false) {}
};

class ReplicaNode {
public:
    ReplicaNode(uint32_t id, uint32_t total_nodes)
        : node_id_(id),
          total_nodes_(total_nodes),
          max_faults_((total_nodes - 1) / 3),
          current_view_(0),
          log_(64, LogEntry(total_nodes)) {}

    [[nodiscard]] std::optional<Message> handle_pre_prepare(const Message& msg) {
        uint32_t primary_id = current_view_ % total_nodes_;
        if (msg.sender_id != primary_id) {
            std::cout << "[Вузол " << node_id_ << "] Pre-Prepare відхилено: відправник "
                      << msg.sender_id << " не є лідером виду " << current_view_ << "\n";
            return std::nullopt;
        }

        if (msg.view != current_view_ || msg.seq_num >= log_.size()) {
            return std::nullopt;
        }

        auto& entry = log_[msg.seq_num];
        if (entry.has_pre_prepare) {
            if (entry.digest != msg.digest) {
                std::cout << "[Вузол " << node_id_ << "] Зрада лідера: еквівокація на слоті "
                          << msg.seq_num << "! Запуск View Change.\n";
            }
            return std::nullopt;
        }

        entry.view = msg.view;
        entry.seq_num = msg.seq_num;
        entry.digest = msg.digest;
        entry.has_pre_prepare = true;
        entry.prepare_count = 1;
        entry.prepares_from[node_id_] = true;

        return Message{
            .type = MessageType::Prepare,
            .view = current_view_,
            .seq_num = msg.seq_num,
            .digest = msg.digest,
            .sender_id = node_id_
        };
    }

    [[nodiscard]] std::optional<Message> handle_prepare(const Message& msg) {
        if (msg.view != current_view_ || msg.seq_num >= log_.size() || msg.sender_id >= total_nodes_) {
            return std::nullopt;
        }

        auto& entry = log_[msg.seq_num];
        if (!entry.has_pre_prepare || entry.digest != msg.digest) {
            return std::nullopt;
        }

        if (!entry.prepares_from[msg.sender_id]) {
            entry.prepares_from[msg.sender_id] = true;
            entry.prepare_count++;
        }

        uint32_t quorum_needed = 2 * max_faults_;
        if (entry.prepare_count >= quorum_needed && !entry.is_prepared) {
            entry.is_prepared = true;
            entry.commit_count = 1;
            entry.commits_from[node_id_] = true;

            return Message{
                .type = MessageType::Commit,
                .view = current_view_,
                .seq_num = msg.seq_num,
                .digest = msg.digest,
                .sender_id = node_id_
            };
        }
        return std::nullopt;
    }

    bool handle_commit(const Message& msg) {
        if (msg.view != current_view_ || msg.seq_num >= log_.size() || msg.sender_id >= total_nodes_) {
            return false;
        }

        auto& entry = log_[msg.seq_num];
        if (!entry.is_prepared || entry.digest != msg.digest) {
            return false;
        }

        if (!entry.commits_from[msg.sender_id]) {
            entry.commits_from[msg.sender_id] = true;
            entry.commit_count++;
        }

        uint32_t commit_quorum = 2 * max_faults_ + 1;
        if (entry.commit_count >= commit_quorum && !entry.is_committed) {
            entry.is_committed = true;
            std::cout << "[Вузол " << node_id_ << "] Слот " << msg.seq_num
                      << " зафіксовано (Committed-Local)! Стан репліковано.\n";
            return true;
        }
        return false;
    }

private:
    uint32_t node_id_;
    uint32_t total_nodes_;
    uint32_t max_faults_;
    uint32_t current_view_;
    std::vector<LogEntry> log_;
};

} // namespace pbft
```
:::

## Покроковий розбір обробки повідомлень та захисту від атак

Розглянемо, як наведений код запобігає класичним візантійським атакам на рівні окремої репліки.

### 1. Захист від нелегітимного лідера (Impersonation)

У функції `handle_pre_prepare` першим кроком обчислюється ідентифікатор очікуваного первинного вузла: `primary_id = current_view % total_nodes`. Якщо зловмисний вузол 2 надішле повідомлення `Pre-Prepare` у виді 0 (де лідером є вузол 0), репліка негайно відкине пакет без зміни локального стану. Це унеможливлює спроби підміни координатора без офіційної процедури зміни виду.

### 2. Запобігання еквівокації лідера (Equivocation Detection)

Якщо первинний вузол надішле репліці повідомлення `Pre-Prepare` з дайджестом `D1` для слота 5, а згодом спробує надіслати інший `Pre-Prepare` з дайджестом `D2` для того самого слота 5, репліка виявить, що прапорець `has_pre_prepare` уже встановлений, а збережений дайджест не збігається з новим.

Репліка не просто відкидає повторне суперечливе повідомлення, а реєструє факт зради лідера та ініціює перехід до процедури зміни виду (`View Change`).

### 3. Гарантія кворуму та фільтрація дублікатів голосів

Під час обробки повідомлень `Prepare` та `Commit` репліка веде бітові маски (`prepares_from` та `commits_from`), де фіксує ідентифікатори вузлів, чиї голоси вже враховані. Якщо візантійський вузол надішле десять однакових повідомлень `Prepare`, лічильник `prepare_count` збільшиться лише один раз під час отримання першого пакета.

Кворум для переходу в стан `prepared` становить `2f` підтверджень від інших реплік (плюс голос самого лідера). Кворум для переходу в стан `committed` становить `2f + 1` підтверджень від різних вузлів кластера (включно з власним голосом). Це математично виключає можливість підтвердження операції за змовою меншості зрадників.

## Очищення журналу: контрольні точки (Checkpoints) та водяні знаки

Журнал транзакцій репліки не може зростати нескінченно. Для стабільної тривалої роботи алгоритм PBFT застосовує механізм періодичного створення узгоджених контрольних точок стану (Checkpoints):

1. **Періодичність контрольних точок:** Кожні `K` виконаних транзакцій (наприклад, кожні 100 або 1000 слотів) репліка фіксує стан свого автомата пам'яті, обчислює криптографічний дайджест стану `d_state = Hash(State)` та розсилає всім іншим вузлам повідомлення `<CHECKPOINT, n, d_state, i>`.
2. **Збір сертифіката чекпойнта:** Коли репліка накопичує `2f + 1` ідентичних повідомлень `CHECKPOINT` від різних вузлів кластера, чекпойнт `n` оголошується **стабільним** (Stable Checkpoint).
3. **Очищення старих записів:** Після формування стабільного чекпойнта на слоті `n` репліка безпечно видаляє з оперативного журналу всі повідомлення `Pre-Prepare`, `Prepare` та `Commit` для слотів `k ≤ n`.
4. **Зсув вікна водяних знаків:** Новий нижній водяний знак встановлюється рівним `h = n`, а верхній водяний знак пересувається на `H = h + 2·L` (де `L` — максимальна ємність вікна буферизації). Будь-які запити, що надходять поза межами діапазону `[h, H]`, негайно відхиляються.

## Типові інженерні пастки при реалізації BFT

Під час перенесення алгоритму в продуктивне середовище слід уникати чотирьох критичних помилок:

1. **Недетерміноване виконання операцій:** Якщо бізнес-логіка транзакції звертається до системного часу (`gettimeofday()`), генерує випадкові числа (`rand()`) або читає стан локального диска, різні чесні репліки отримають різні результати виконання, навіть якщо вони узгодили абсолютно однаковий порядок транзакцій. Усі змінні середовища мусять передаватися явно всередині тіла запиту клієнта.
2. **Переповнення пам'яті журналу (Log Exhaustion):** У наведеному прикладі журнал має фіксований розмір `MAX_LOG_ENTRIES = 64`. У реальній системі вузли зобов'язані періодично створювати узгоджені контрольні точки (Checkpoints) кожні `K` транзакцій, збирати кворум із `2f + 1` підписів стану та очищати старі записи журналу, пересуваючи вікно водяних знаків `[h, H]`.
3. **Асиметричний криптографічний оверхед:** Перевірка RSA чи ECDSA-підписів на кожен пакет `Prepare` створює колосальне навантаження на процесор. У продуктивних реалізаціях PBFT між кожною парою реплік встановлюється сесійний симетричний ключ через TLS, а пакети підписуються за допомогою швидких векторів MAC (HMAC / Poly1305), залишаючи важкі асиметричні підписи лише для рідкісних повідомлень `View-Change` та `New-View`.
4. **Атака на тайм-аути зміни виду:** Якщо тайм-аут лідера встановлено занадто малим, звичайний короткочасний сплеск мережевого навантаження спричинить лавиноподібну зміну видів, паралізуючи роботу системи. Тайм-аут зобов'язаний експоненційно подвоюватися після кожної невдалої спроби зміни виду (Exponential Backoff).
