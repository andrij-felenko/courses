# ⚙️ Реалізація детектора та резолвера конфліктів мультилідерної реплікації

У мультилідерній архітектурі вузол не може приймати вхідні пакети реплікації як сліпі команди на безумовний перезапис пам'яті. Якщо репліка просто виконає чужий `UPDATE` поверх свого поточного рядка, будь-який паралельний локальний запис буде безповоротно знищено. Кожен вузол-лідер мусить містити внутрішній рушій координації, який розв'язує три послідовні задачі:
1. **Визначення причинності (англ. *causality tracking*):** з'ясувати за допомогою версійних векторів, чи нове оновлення логічно спирається на локальний стан (тобто сталося суворо *після* нього), чи було сформовано в іншому датацентрі незалежно й паралельно.
2. **Фільтрація лупів (англ. *loop suppression*):** перевірити метадані транзакції, щоб відкинути оновлення, які вже проходили через цей вузол у кільцевих чи повнозв'язних топологіях.
3. **Детерміноване розв'язання (англ. *conflict resolution*):** застосувати обрану політику збіжності (LWW, збереження розгалужень або злиття полів), гарантуючи, що всі вузли кластера після отримання однакового набору пакетів прийдуть до ідентичного бітового стану.

Нижче наведено повноцінну реалізацію ядра детекції та розв'язання конфліктів.

### Структури даних та математичне відношення передування

Версійний вектор (англ. *Version Vector*) відстежує кількість оновлень, виконаних кожним вузлом кластера для конкретного ключа. Для двох версійних векторів `V_A` та `V_B` однакової розмірності `N` діють такі правила порівняння:
- `V_A = V_B` (ідентичні): `∀i: V_A[i] = V_B[i]`.
- `V_A > V_B` (`V_A` строго домінує над `V_B`, тобто `V_B` причинно передує `V_A`): `∀i: V_A[i] ≥ V_B[i]` та `∃j: V_A[j] > V_B[j]`.
- `V_A < V_B` (`V_A` підпорядкований `V_B`): `∀i: V_A[i] ≤ V_B[i]` та `∃j: V_A[j] < V_B[j]`.
- `V_A ∥ V_B` (вектори **конкурентні**, тобто паралельні): існують індекси `j` та `k` такі, що `V_A[j] > V_B[j]`, але `V_A[k] < V_B[k]`. Це стан конфлікту.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <stdbool.h>

#define MAX_NODES 8
#define MAX_SIBLINGS 4
#define MAX_VAL_LEN 64

/* Результат порівняння причинності */
typedef enum {
    CAUSAL_IDENTICAL,
    CAUSAL_DOMINATES,      /* Локальний стан новіший за вхідний */
    CAUSAL_IS_DOMINATED,   /* Вхідний стан новіший за локальний (пряме оновлення) */
    CAUSAL_CONCURRENT      /* Справжній конфлікт: паралельні незалежні записи */
} CausalRelation;

/* Політика розв'язання конфліктів */
typedef enum {
    STRATEGY_LWW,          /* Last-Write-Wins за фізичною міткою часу */
    STRATEGY_SIBLINGS,     /* Збереження розгалужень для злиття на читанні */
    STRATEGY_FIELD_MERGE   /* Поколонне / полями об'єднання (CRDT-like) */
} ConflictStrategy;

/* Версійний вектор */
typedef struct {
    uint64_t counters[MAX_NODES];
} VersionVector;

/* Окремий варіант значення (ревізія) */
typedef struct {
    char value[MAX_VAL_LEN];
    VersionVector vv;
    uint64_t timestamp_ms;
    uint32_t origin_node;
} RecordRevision;

/* Сховище запису для одного ключа */
typedef struct {
    char key[32];
    RecordRevision siblings[MAX_SIBLINGS];
    size_t sibling_count;
} DatabaseRecord;

/* Ініціалізація вектора */
void vv_init(VersionVector *vv) {
    memset(vv->counters, 0, sizeof(vv->counters));
}

/* Інкремент лічильника свого вузла */
void vv_increment(VersionVector *vv, uint32_t node_id) {
    if (node_id < MAX_NODES) {
        vv->counters[node_id]++;
    }
}

/* Об'єднання векторів (компонентний максимум) */
void vv_merge(VersionVector *dest, const VersionVector *src) {
    for (size_t i = 0; i < MAX_NODES; i++) {
        if (src->counters[i] > dest->counters[i]) {
            dest->counters[i] = src->counters[i];
        }
    }
}

/* Порівняння двох версійних векторів */
CausalRelation vv_compare(const VersionVector *a, const VersionVector *b) {
    bool a_greater = false;
    bool b_greater = false;

    for (size_t i = 0; i < MAX_NODES; i++) {
        if (a->counters[i] > b->counters[i]) {
            a_greater = true;
        } else if (a->counters[i] < b->counters[i]) {
            b_greater = true;
        }
    }

    if (!a_greater && !b_greater) return CAUSAL_IDENTICAL;
    if (a_greater && !b_greater)  return CAUSAL_DOMINATES;
    if (!a_greater && b_greater)  return CAUSAL_IS_DOMINATED;
    return CAUSAL_CONCURRENT;
}

/* Локальний запис на вузлі */
void record_local_write(DatabaseRecord *rec, const char *new_val, 
                        uint32_t local_node_id, uint64_t now_ms) {
    VersionVector next_vv;
    vv_init(&next_vv);

    /* Акумулюємо знання з усіх поточних siblings */
    for (size_t i = 0; i < rec->sibling_count; i++) {
        vv_merge(&next_vv, &rec->siblings[i].vv);
    }
    vv_increment(&next_vv, local_node_id);

    /* Запис схлопує всі старі версії в одну нову */
    rec->sibling_count = 1;
    strncpy(rec->siblings[0].value, new_val, MAX_VAL_LEN - 1);
    rec->siblings[0].value[MAX_VAL_LEN - 1] = '\0';
    rec->siblings[0].vv = next_vv;
    rec->siblings[0].timestamp_ms = now_ms;
    rec->siblings[0].origin_node = local_node_id;
}

/* Застосування вхідного пакета реплікації */
bool record_apply_remote(DatabaseRecord *rec, const RecordRevision *incoming,
                         ConflictStrategy strategy) {
    if (rec->sibling_count == 0) {
        rec->siblings[0] = *incoming;
        rec->sibling_count = 1;
        return true;
    }

    /* 1. Перевіряємо вхідний запис проти кожного локального sibling */
    bool incoming_is_obsolete = true;
    bool any_concurrent = false;
    size_t survived_count = 0;
    RecordRevision survived[MAX_SIBLINGS];

    for (size_t i = 0; i < rec->sibling_count; i++) {
        CausalRelation rel = vv_compare(&rec->siblings[i].vv, &incoming->vv);

        switch (rel) {
            case CAUSAL_IDENTICAL:
            case CAUSAL_DOMINATES:
                /* Локальний стан уже знає або перевищує вхідний */
                survived[survived_count++] = rec->siblings[i];
                break;

            case CAUSAL_IS_DOMINATED:
                /* Вхідний запис витісняє локальний застарілий */
                incoming_is_obsolete = false;
                break;

            case CAUSAL_CONCURRENT:
                /* Паралельний незалежний запис */
                incoming_is_obsolete = false;
                any_concurrent = true;
                survived[survived_count++] = rec->siblings[i];
                break;
        }
    }

    if (incoming_is_obsolete && !any_concurrent) {
        /* Вхідний запис відкинуто як застарілий дублікат */
        return false;
    }

    if (!any_concurrent && !incoming_is_obsolete) {
        /* Пряме оновлення без конфлікту: вхідний замінює все застаріле */
        rec->siblings[0] = *incoming;
        rec->sibling_count = 1;
        return true;
    }

    /* 2. Обробка конкурентного конфлікту за обраною стратегією */
    if (strategy == STRATEGY_LWW) {
        /* Знаходимо переможця за часом (з tie-breaker за ID вузла) */
        RecordRevision winner = *incoming;
        for (size_t i = 0; i < survived_count; i++) {
            if (survived[i].timestamp_ms > winner.timestamp_ms ||
               (survived[i].timestamp_ms == winner.timestamp_ms && 
                survived[i].origin_node > winner.origin_node)) {
                winner = survived[i];
            }
        }
        /* Зливаємо вектори, щоб зафіксувати знання обох гілок */
        for (size_t i = 0; i < survived_count; i++) {
            vv_merge(&winner.vv, &survived[i].vv);
        }
        vv_merge(&winner.vv, &incoming->vv);

        rec->siblings[0] = winner;
        rec->sibling_count = 1;
        return true;
    } 
    else if (strategy == STRATEGY_SIBLINGS) {
        /* Додаємо вхідний варіант до списку збережених гілок */
        if (survived_count < MAX_SIBLINGS) {
            survived[survived_count++] = *incoming;
        }
        rec->sibling_count = survived_count;
        for (size_t i = 0; i < survived_count; i++) {
            rec->siblings[i] = survived[i];
        }
        return true;
    }
    else if (strategy == STRATEGY_FIELD_MERGE) {
        /* CRDT-злиття: конкатенація неперетинних частин */
        RecordRevision merged;
        snprintf(merged.value, MAX_VAL_LEN, "%s+%s", survived[0].value, incoming->value);
        vv_init(&merged.vv);
        vv_merge(&merged.vv, &survived[0].vv);
        vv_merge(&merged.vv, &incoming->vv);
        merged.timestamp_ms = (incoming->timestamp_ms > survived[0].timestamp_ms) 
                              ? incoming->timestamp_ms : survived[0].timestamp_ms;
        merged.origin_node = incoming->origin_node;

        rec->siblings[0] = merged;
        rec->sibling_count = 1;
        return true;
    }

    return false;
}
```
```cpp
#include <iostream>
#include <vector>
#include <string>
#include <string_view>
#include <algorithm>
#include <cstdint>
#include <optional>
#include <array>
#include <span>

namespace replication {

constexpr size_t MAX_NODES = 8;

enum class CausalRelation {
    Identical,
    Dominates,      // Локальний вектор строго новіший
    IsDominated,    // Вхідний вектор строго новіший (пряма заміна)
    Concurrent      // Паралельні зміни (конфлікт)
};

enum class ConflictStrategy {
    LastWriteWins,
    PreserveSiblings,
    FieldMerge
};

struct VersionVector {
    std::array<uint64_t, MAX_NODES> counters{};

    void increment(size_t node_id) noexcept {
        if (node_id < MAX_NODES) {
            ++counters[node_id];
        }
    }

    void merge_with(const VersionVector& other) noexcept {
        for (size_t i = 0; i < MAX_NODES; ++i) {
            counters[i] = std::max(counters[i], other.counters[i]);
        }
    }

    [[nodiscard]] CausalRelation compare_to(const VersionVector& other) const noexcept {
        bool this_greater = false;
        bool other_greater = false;

        for (size_t i = 0; i < MAX_NODES; ++i) {
            if (counters[i] > other.counters[i]) {
                this_greater = true;
            } else if (counters[i] < other.counters[i]) {
                other_greater = true;
            }
        }

        if (!this_greater && !other_greater) return CausalRelation::Identical;
        if (this_greater && !other_greater)  return CausalRelation::Dominates;
        if (!this_greater && other_greater)  return CausalRelation::IsDominated;
        return CausalRelation::Concurrent;
    }
};

struct RecordRevision {
    std::string value;
    VersionVector vv;
    uint64_t timestamp_ms{0};
    uint32_t origin_node{0};
};

class DatabaseRecord {
public:
    explicit DatabaseRecord(std::string key) : key_(std::move(key)) {}

    void local_write(std::string_view new_value, uint32_t node_id, uint64_t now_ms) {
        VersionVector next_vv;
        for (const auto& sibling : siblings_) {
            next_vv.merge_with(sibling.vv);
        }
        next_vv.increment(node_id);

        siblings_.clear();
        siblings_.push_back(RecordRevision{
            .value = std::string(new_value),
            .vv = next_vv,
            .timestamp_ms = now_ms,
            .origin_node = node_id
        });
    }

    bool apply_remote_update(const RecordRevision& incoming, ConflictStrategy strategy) {
        if (siblings_.empty()) {
            siblings_.push_back(incoming);
            return true;
        }

        bool incoming_is_obsolete = true;
        bool any_concurrent = false;
        std::vector<RecordRevision> survived;
        survived.reserve(siblings_.size());

        for (const auto& local : siblings_) {
            const auto relation = local.vv.compare_to(incoming.vv);

            switch (relation) {
                case CausalRelation::Identical:
                case CausalRelation::Dominates:
                    survived.push_back(local);
                    break;

                case CausalRelation::IsDominated:
                    incoming_is_obsolete = false;
                    break;

                case CausalRelation::Concurrent:
                    incoming_is_obsolete = false;
                    any_concurrent = true;
                    survived.push_back(local);
                    break;
            }
        }

        if (incoming_is_obsolete && !any_concurrent) {
            return false; // Відкинуто як застаріле
        }

        if (!any_concurrent && !incoming_is_obsolete) {
            siblings_.clear();
            siblings_.push_back(incoming);
            return true;
        }

        // Розв'язання конфлікту паралельних гілок
        switch (strategy) {
            case ConflictStrategy::LastWriteWins: {
                RecordRevision winner = incoming;
                for (const auto& s : survived) {
                    if (s.timestamp_ms > winner.timestamp_ms ||
                       (s.timestamp_ms == winner.timestamp_ms && s.origin_node > winner.origin_node)) {
                        winner = s;
                    }
                }
                for (const auto& s : survived) {
                    winner.vv.merge_with(s.vv);
                }
                winner.vv.merge_with(incoming.vv);

                siblings_.clear();
                siblings_.push_back(std::move(winner));
                return true;
            }

            case ConflictStrategy::PreserveSiblings: {
                survived.push_back(incoming);
                siblings_ = std::move(survived);
                return true;
            }

            case ConflictStrategy::FieldMerge: {
                RecordRevision merged;
                merged.value = survived.front().value + "+" + incoming.value;
                merged.vv = survived.front().vv;
                merged.vv.merge_with(incoming.vv);
                merged.timestamp_ms = std::max(incoming.timestamp_ms, survived.front().timestamp_ms);
                merged.origin_node = incoming.origin_node;

                siblings_.clear();
                siblings_.push_back(std::move(merged));
                return true;
            }
        }

        return false;
    }

    [[nodiscard]] std::span<const RecordRevision> siblings() const noexcept {
        return siblings_;
    }

    [[nodiscard]] std::string_view key() const noexcept {
        return key_;
    }

private:
    std::string key_;
    std::vector<RecordRevision> siblings_;
};

} // namespace replication
```
:::

### Ключові інженерні нюанси та підводні камені реалізації

Розробка надійного рушія мультилідерної реплікації вимагає врахування низки неочевидних крайових випадків, які виникають на перетині мережевої невизначеності, керування пам'яттю та паралельного виконання.

#### 1. Злиття векторів після вибору переможця в LWW

Зверніть увагу на критичну деталь у реалізації гілки `STRATEGY_LWW`: коли алгоритм обирає єдиного переможця на основі фізичної мітки часу `timestamp_ms`, він категорично **не повинен просто копіювати версійний вектор запису-переможця**. Необхідно обов'язково викликати покомпонентне об'єднання (`vv_merge`) з усіма альтернативними версійними векторами, які брали участь у конфлікті.

Якщо знехтувати цим злиттям, результуючий стан вузла міститиме прогалину в причинній історії. Уявімо ситуацію: вузол A мав вектор `[1, 0]` зі значенням `X`, а вузол B надіслав вектор `[0, 1]` зі значенням `Y` та новішим штампом часу. Якщо вузол A запише значення `Y`, але залишить вектор `[0, 1]`, він «забуде», що колись знав про власну версію `[1, 0]`. Коли вузол A пізніше прийме черговий локальний запис і збільшить свій лічильник до `[2, 1]`, а потім відправить його на вузол C, цей третій вузол не зможе коректно відрізнити, які саме старі стани були враховані, а які загублені. Акумуляція причинного знання через максимум векторів гарантує, що результуючий вектор домінуватиме над усіма учасниками конфлікту, запобігаючи хибним розгалуженням у майбутньому.

#### 2. Захист від вибухового розростання siblings та обмеження глибини

Збереження паралельних гілок (стратегія `STRATEGY_SIBLINGS`) є найбільш математично чесною моделлю, оскільки база даних не бере на себе сміливість вирішувати за бізнес-логіку, чиє оновлення важливіше. Проте ця чесність має пряму ціну в пам'яті та складності клієнтських запитів.

Якщо клієнтський застосунок рідко зчитує певний ключ, а фонові сервіси або інші лідери продовжують генерувати конкурентні записи, список `siblings` починає неконтрольовано зростати (так званий ефект «вибуху гілок», англ. *sibling explosion*). Кожен наступний паралельний запис порівнюється з дедалі більшою кількістю збережених ревізій, що перетворює перевірку причинності з константної операції на квадратичний цикл `O(K · M)`, де `K` — кількість наявних гілок, а `M` — розмір вектора.

Промислові розподілені системи (зокрема Riak KV та Apache CouchDB) застосовують такі захисні механізми:
- **Жорсткий ліміт глибини (max_siblings):** встановлюється поріг (зазвичай від 8 до 64 гілок). Якщо черговий конкурентний запис перевищує цей ліміт, база даних примусово схлопує найстаріші гілки за евристикою LWW, записує попередження в журнал аудиту та інформує метрику моніторингу про деградацію якості даних.
- **Вимога повного контексту при читанні (vclock pruning):** клієнт, зчитуючи список siblings, зобов'язаний передати назад системі так званий непрозорий маркер контексту (англ. *causal context*), який містить об'єднаний версійний вектор усіх прочитаних ревізій. Будь-який наступний запис від цього клієнта з новим значенням автоматично домінуватиме над усіма старими гілками, безпечно стираючи їх зі сховища за один крок.

#### 3. Немонотонність фізичного годинника та необхідність tie-breaker

Покладання на мітку настінного часу (`timestamp_ms`) у стратегії Last-Write-Wins створює ризик розбіжності даних між репліками через дві фізичні причини:
1. **Немонотонність системного часу:** протокол NTP (Network Time Protocol) під час синхронізації з еталонними серверами може коригувати час стрибком назад (англ. *step adjustment*), якщо виявлено суттєве відставання або випередження кварцового резонатора. У результаті запис, здійснений о 12:00:05, може отримати штамп 12:00:02, поступившись старішому запису, зробленому секундою раніше.
2. **Точні колізії міток часу:** у високонавантажених системах з десятками тисяч операцій на секунду два незалежні лідери в різних датацентрах можуть зафіксувати транзакції в одну й ту саму мілісекунду (або навіть мікросекунду).

Якщо два конкурентні записи мають однаковий штамп `t1 == t2`, а алгоритм не має чітко визначеного детермінованого правила вибору, виникає катастрофічна аномалія: лідер у Європі залишить своє значення (бо вважає свій запис первинним), а лідер в Азії залишить своє. Репліки розійдуться назавжди, попри те, що формально обидві використовують LWW.

Щоб запобігти цьому, алгоритм зобов'язаний застосовувати вторинний критерій розриву нічиєї (англ. *tie-breaker*). У наведеному вище коді цим критерієм слугує порівняння унікальних числових ідентифікаторів вузлів `origin_node` (`origin_node_A > origin_node_B`). У промислових сховищах додатково порівнюють криптографічні хеші значень (SHA-256 від корисного навантаження), що гарантує абсолютно однаковий вибір переможця на кожному сервері планети без потреби в додатковому мережевому раунді.

### Проблема видалення даних: могильні плити (tombstones) та їхня утилізація

Найпідступнішою операцією в мультилідерній реплікації є не оновлення, а **видалення запису** (`DELETE`).

Якщо вузол A після видалення рядка клієнта просто витре відповідний блок пам'яті або видалить запис із таблиці на диску, виникне ефект «воскресіння мертвих даних» (англ. *data resurrection* або *ghost records*). Коли вузол B згодом надішле на вузол A черговий пакет реплікації, який містить старе оновлення цього ж клієнта (яке затрималося в мережі або було згенероване до видалення), вузол A сприйме це як вставку абсолютно нового запису і повторно створить видалений об'єкт.

Щоб видалення поширювалося коректно, воно повинно оформлюватися як спеціальний запис-маркер — **могильна плита** (англ. *tombstone*):
1. Операція видалення генерує нормальну нову ревізію запису, але в полі значення встановлюється спеціальний прапорець `is_deleted = true`, а версійний вектор інкрементується за загальними правилами.
2. Могильна плита реплікується на всі інші лідери як звичайне оновлення, придушуючи старіші версії запису за правилом домінування версійного вектора.
3. При звичайних вибірках (`SELECT`) рушій бази даних фільтрує записи з активними надгробками, приховуючи їх від користувача.

#### Горизонт причинної стабільності (GC Horizon)

Могильні плити не можуть зберігатися вічно, інакше база даних поступово переповниться маркерами видалених об'єктів. Проте видалити сам надгробок із диска можна лише тоді, коли система має строгу математичну гарантію: **кожен лідер у кластері вже гарантовано отримав цей надгробок і застосував його у своєму сховищі**.

Для цього лідери періодично обмінюються векторами стабільності (англ. *stability vectors* або *watermarks*). Кожен вузол повідомляє партнерам мінімальний лічильник журналу, до якого він повністю вичитав і зафіксував усі зміни. Коли вектор підтверджень показує, що надгробок подолав горизонт стабільності на всіх активних вузлах кластера, фоновий процес збирача сміття (англ. *garbage collector* або *vacuum*) фізично вичищає могильну плиту з пам'яті та дискових структур.

Якщо ж один із вузлів кластера вимикається на тривалий час (наприклад, аварія датацентру на кілька діб), горизонт стабільності зупиняється, і всі інші лідери змушені накопичувати надгробки на диску. Якщо час простою перевищує максимально допустимий ліміт зберігання (англ. *tombstone TTL*), відключений вузол оголошується безнадійно застарілим: йому забороняється повертатися в кластер через звичайну дельта-реплікацію, і він зобов'язаний пройти повне переініціалізування через новий знімок даних (англ. *full state transfer* / *snapshot restore*).

### Покроковий трасувальний аналіз сценаріїв виконання

Щоб наочно простежити логіку роботи детектора конфліктів, розглянемо три характерні послідовності подій у кластері з двох лідерів (Вузол 0 та Вузол 1).

#### Сценарій 1: Послідовне оновлення без конфлікту (Causal Succession)

1. Початковий стан: ключ порожній на обох вузлах.
2. Вузол 0 виконує локальний запис:
   `value = "Apple"`, вектор `V_0 = [1, 0]`.
3. Пакет реплікації летить від Вузла 0 до Вузла 1.
4. Вузол 1 отримує пакет: оскільки локальний стан був порожнім, запис фіксується. Стан Вузла 1 стає: `value = "Apple"`, `V_1 = [1, 0]`.
5. Клієнт на Вузлі 1 виконує наступне оновлення:
   Локальний запис інкрементує лічильник Вузла 1: `value = "Banana"`, вектор `V_1 = [1, 1]`.
6. Пакет реплікації летить від Вузла 1 до Вузла 0.
7. Вузол 0 порівнює свій вектор `V_0 = [1, 0]` із вхідним вектором `V_in = [1, 1]`.
   - `V_0[0] == V_in[0]` (1 == 1);
   - `V_0[1] < V_in[1]` (0 < 1).
   - Результат порівняння: `CAUSAL_IS_DOMINATED` (вхідний запис строго новіший).
8. Вузол 0 без жодного конфлікту перезаписує значення на `"Banana"` та оновлює свій вектор до `[1, 1]`. Кластер залишається узгодженим.

#### Сценарій 2: Паралельний конфлікт записів (Concurrent Divergence)

1. Обидва вузли стартують зі спільного стану: `value = "Initial"`, вектор `[1, 1]`.
2. Клієнт A на Вузлі 0 пише: `value = "Red"`, новий вектор `V_0 = [2, 1]`, штамп часу `t = 1000`, вузол-джерело `0`.
3. Одночасно клієнт B на Вузлі 1 пише: `value = "Blue"`, новий вектор `V_1 = [1, 2]`, штамп часу `t = 1005`, вузол-джерело `1`.
4. Вузол 0 відправляє свій запис Вузлу 1, а Вузол 1 відправляє свій запис Вузлу 0. Пакети перетинаються в дорозі через трансокеанський канал.
5. Обробка на Вузлі 0:
   - Вузол 0 порівнює `V_0 = [2, 1]` із вхідним `V_in = [1, 2]`.
   - По нульовому індексу: `2 > 1` (Вузол 0 має власну правку).
   - По першому індексу: `1 < 2` (Вхідний запис містить чужу правку).
   - Результат: `CAUSAL_CONCURRENT` (справжній конфлікт).
   - За стратегії `STRATEGY_LWW`: штамп `t = 1005` (Вузол 1) більший за `t = 1000` (Вузол 0). Перемагає `"Blue"`. Вектор схлопується до `[2, 2]`.
6. Обробка на Вузлі 1:
   - Вузол 1 порівнює `V_1 = [1, 2]` із вхідним `V_in = [2, 1]`.
   - Результат: `CAUSAL_CONCURRENT`.
   - За стратегії `STRATEGY_LWW`: порівнюються ті самі мітки часу (`1005 > 1000`). Перемагає той самий запис `"Blue"`. Вектор схлопується до `[2, 2]`.
7. Підсумок: обидва вузли незалежно й детерміновано зафіксували стан `value = "Blue"`, `V = [2, 2]`. Кластер досяг збіжності.

#### Сценарій 3: Конкурентне розгалуження та ручне злиття застосунком (Siblings Merge)

1. Початковий стан: ключ містить ревізію `value = "Original"`, вектор `[1, 1]`.
2. Вузол 0 приймає локальну правку: `value = "Title A"`, новий вектор `[2, 1]`.
3. Вузол 1 паралельно приймає правку: `value = "Title B"`, новий вектор `[1, 2]`.
4. Кластер налаштовано на стратегію `STRATEGY_SIBLINGS`.
5. Після перехресного обміну пакетами реплікації обидва вузли фіксують відношення `CAUSAL_CONCURRENT`.
6. Обидва лідери зберігають **обидві гілки** у внутрішньому масиві:
   `siblings = [ {"Title A", [2, 1]}, {"Title B", [1, 2]} ]`.
7. Користувацький застосунок надсилає запит на читання (`GET /article/101`). База даних повертає обидва значення разом із комбінованим контекстом версій `context = [2, 2]`.
8. Користувач у вебінтерфейсі бачить екран вирішення колізії, обирає синтезований варіант `"Title A & Title B"` і надсилає запис (`POST /article/101`, `context = [2, 2]`).
9. Вузол 0 приймає цей запис, порівнює переданий контекст `[2, 2]` з усіма локальними siblings (`[2, 1]` та `[1, 2]`). Оскільки новий контекст строго домінує над обома гілками, старі siblings стираються, а єдиним чинним станом стає:
   `value = "Title A & Title B"`, новий вектор `V = [3, 2]`.
10. Під час наступної реплікації цей єдиний вектор `[3, 2]` витісняє всі розгалуження на Вузлі 1. Система повернулася до монолітного стану без втрати інформації.

### Оптимізація пам'яті: точкові версійні вектори (Dotted Version Vectors)

У класичних версійних векторах розмір структури масштабується як `O(N)`, де `N` — кількість усіх вузлів, які коли-небудь записували дані. Якщо у кластері динамічно з'являються та зникають репліки (наприклад, контейнери Kubernetes або клієнтські мобільні пристрої), вектори стають громіздкими, споживаючи більше пам'яті, ніж самі корисні дані.

Для вирішення цієї проблеми сучасні сховища (як-от Riak Core) використовують **точкові версійні вектори** (англ. *Dotted Version Vectors*, DVV):
- Базовий версійний вектор (англ. *causal context*) зберігає лише узагальнену інформацію про стабільні старі записи.
- Кожна конкурентна ревізія (sibling) позначається дискретною парою — **точкою** (англ. *dot*): `(node_id, local_counter)`.
- Точка точно ідентифікує конкретну подію запису без потреби тягнути повну копію всього вектора всередині кожного окремого sibling.

Це дозволяє зменшити витрати пам'яті на збереження розгалужень у `K` разів (де `K` — кількість паралельних версій), зберігаючи повну математичну строгість детекції конфліктів.

### Структура мережевого кадру та запобігання зацикленню пакетів

У складних топологіях (кільце або сітка) вхідний пакет реплікації після локального застосування повинен бути пересланий іншим сусіднім лідерам. Щоб пакет не кружляв мережею нескінченно, генеруючи «реплікаційний шторм» (англ. *replication storm*), мережевий протокол додає до кожного кадру спеціальний заголовок трасування.

Типовий двійковий заголовок пакету реплікації включає:
- `magic_bytes` (4 байти): ідентифікатор протоколу реплікації.
- `origin_node_id` (4 байти): первинний лідер, де виникла транзакція.
- `tx_sequence_lsn` (8 байтів): монотонний номер журналу предзапису (Log Sequence Number, LSN) на вузлі-джерелі.
- `hop_count` (1 байт): лічильник пройдених проміжних реплік (зменшується до 0, аналог IP TTL).
- `visited_mask` (8 байтів бітової маски або масив ID): список усіх вузлів, через які вже пройшов цей пакет.
- `payload_crc32` (4 байти): контрольна сума корисного навантаження для захисту від апаратних збоїв мережевих інтерфейсів.

Коли репліка отримує кадр, вона перевіряє свій біт у `visited_mask`. Якщо біт уже встановлено, пакет негайно відкидається (loop suppression). Якщо біт чистий, вузол встановлює свій біт, застосовує зміни до локального сховища через детектор конфліктів і транслює оновлений кадр усім іншим відомим лідерам. Це гарантує скінченність і стабільність поширення даних у довільних мережевих графах.


