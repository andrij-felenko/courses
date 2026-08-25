# ⚙️ Реалізація квошієнтного фільтра: компактна структура з бітовим пакуванням та динамічним масштабуванням

Нижче наведено повну реалізацію квошієнтного фільтра мовами C та C++. Реалізація демонструє розщеплення хеш-коду на частку та залишок, підтримку трьох метаданих бітів (`is_occupied`, `is_continuation`, `is_shifted`), алгоритм пошуку набігів, лінійне зондування за правилом Робіна Гуда, детерміноване видалення елементів та динамічне подвоєння місткості без повторного хешування.

## 1. Організація пам'яті та бітове пакування слотів

Кожен слот квошієнтного фільтра складається з трьох функціональних частин:
- **`is_occupied` (1 біт)**: Прапорець канонічної зайнятості. Встановлюється в `1`, якщо у фільтрі існує хоча б один збережений елемент, для якого саме цей слот є рідною домівкою (`f_q = i`). Зверніть увагу: цей біт прив'язаний до канонічного індексу комірки і не переміщується, навіть якщо самі відбитки зсунуті вправо через колізії.
- **`is_continuation` (1 біт)**: Прапорець продовження набігу. Дозволяє розрізняти межі сусідніх набігів. Якщо в комірці зберігається перший (найменший) залишок набігу, біт дорівнює `0`. Якщо комірка містить другий, третій чи наступні залишки того самого набігу, біт встановлюється в `1`.
- **`is_shifted` (1 біт)**: Прапорець просторового зміщення. Дорівнює `0`, якщо залишок у комірці розташований у своєму рідному слоті `f_q`. Дорівнює `1`, якщо в результаті розв'язання колізій лінійним зондуванням залишок був витіснений праворуч від свого канонічного індексу.
- **`remainder` (r бітів)**: Корисне навантаження — залишок хеш-коду. У наведеній реалізації використовується 5-бітний залишок для пакування слота рівно в 1 байт (`1 + 1 + 1 + 5 = 8` бітів), що дозволяє досягти граничної щільності даних без вирівнювальних проміжків (Zero Padding).

Таблиця слотів розміщується в суцільному динамічному масиві пам'яті. Кількість слотів `m = 2^q` завжди обирається строго як ступінь двійки, завдяки чому обчислення циклічного залишку від ділення `i mod m` замінюється надшвидкою побітовою операцією `i & (m - 1)`.

## 2. Алгоритм декодування кластерів та знаходження набігу

Оскільки елементи можуть зміщуватися на довільну кількість позицій вправо від рідного слота, пошук набігу для канонічної частки `f_q` виконується у три детерміновані кроки:

1. **Знаходження початку кластера**: Починаючи з комірки `f_q`, алгоритм крокує вліво (`(curr - 1) & mask`), доки не зустріне слот з `is_shifted == 0`. Ця комірка є абсолютним початком неперервного кластера, оскільки її мешканець перебуває у своєму рідному слоті.
2. **Підрахунок рангу набігу**: Алгоритм сканує слоти кластера зліва направо від знайденого початку до цільового слота `f_q`. Лічильник підраховує кількість слотів, у яких прапорець `is_occupied == 1`. Це число визначає порядковий номер (ранг) цільового набігу всередині кластера.
3. **Локалізація цільового набігу**: Алгоритм повторно сканує кластер, відраховуючи початки набігів (комірки, де `is_continuation == 0`). Коли лічильник досягає розрахованого рангу, знайдений слот є першим елементом шуканого набігу `f_q`.

## 3. Лінійне зондування Робіна Гуда при вставці

При вставці нового елемента `x = (f_q, f_r)` алгоритм дотримується фундаментального інваріанта: **залишки всередині кожного набігу зберігаються у відсортованому за зростанням порядку**, а самі набіги розташовуються в порядку зростання їхніх часток `f_q`.

Якщо слот вставки вже зайнятий:
- Алгоритм знаходить точну позицію для збереження нового залишку `f_r` відповідно до його числового значення.
- Усі наступні елементи кластера каскадно зсуваються вправо на одну позицію аж до першого порожнього слота.
- Для зміщених елементів виставляється прапорець `is_shifted = 1`.
- Якщо новий залишок вставляється всередину вже існуючого набігу, для нього та зміщених наступників коректно виставляється або скидається прапорець `is_continuation`.

## 4. Детерміноване видалення без розриву кластерів

Видалення елемента у квошієнтному фільтрі принципово відрізняється від інших структур: воно не вимагає лічильників і не допускає випадкового пошкодження сусідніх даних.
- Знайшовши слот із цільовим залишком `f_r` у набігу `f_q`, алгоритм витягує його.
- Щоб на місці видаленого елемента не утворилася розривна порожнеча (дірка, яка зламає лінійне зондування для наступних пошуків), усі зміщені елементи хвоста кластера зсуваються вліво на одну позицію.
- Зсув припиняється, як тільки алгоритм зустрічає порожній слот або слот, чий мешканець розташований у своєму канонічному гнізді (`is_shifted == 0`).
- Якщо видалений елемент був єдиним у своєму набігу, біт `is_occupied` для слота `f_q` скидається в `0`.

## 5. Програмний код реалізації

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define MAX_LOAD_FACTOR 0.85

typedef struct {
    uint8_t is_occupied : 1;
    uint8_t is_continuation : 1;
    uint8_t is_shifted : 1;
    uint8_t remainder : 5;  /* 5-бітний залишок для демонстрації в 1 байті */
} QFSlot;

typedef struct {
    QFSlot *table;
    size_t q_bits;          /* Кількість бітів частки */
    size_t r_bits;          /* Кількість бітів залишку */
    size_t num_slots;       /* m = 1 << q_bits */
    size_t slot_mask;       /* num_slots - 1 */
    size_t count;           /* Кількість збережених елементів */
} QuotientFilter;

/* 64-бітний хешер FNV-1a */
static inline uint64_t hash_bytes(const void *data, size_t len) {
    const uint8_t *ptr = (const uint8_t *)data;
    uint64_t h = 14695981039346656037ULL;
    for (size_t i = 0; i < len; ++i) {
        h ^= ptr[i];
        h *= 1099511628211ULL;
    }
    return h;
}

/* Ініціалізація квошієнтного фільтра */
QuotientFilter *qf_create(size_t q_bits, size_t r_bits) {
    QuotientFilter *qf = (QuotientFilter *)malloc(sizeof(QuotientFilter));
    if (!qf) return NULL;

    qf->q_bits = q_bits;
    qf->r_bits = r_bits;
    qf->num_slots = (size_t)1 << q_bits;
    qf->slot_mask = qf->num_slots - 1;
    qf->count = 0;
    qf->table = (QFSlot *)calloc(qf->num_slots, sizeof(QFSlot));

    if (!qf->table) {
        free(qf);
        return NULL;
    }
    return qf;
}

void qf_destroy(QuotientFilter *qf) {
    if (qf) {
        free(qf->table);
        free(qf);
    }
}

static inline bool slot_is_empty(const QFSlot *s) {
    return !s->is_occupied && !s->is_continuation && !s->is_shifted;
}

/* Знаходження початку набігу для канонічного слота f_q */
static size_t find_run_start(const QuotientFilter *qf, size_t f_q) {
    size_t curr = f_q;
    while (qf->table[curr].is_shifted) {
        curr = (curr - 1) & qf->slot_mask;
    }

    size_t scan = curr;
    size_t run_start = curr;

    while (scan != f_q) {
        do {
            run_start = (run_start + 1) & qf->slot_mask;
        } while (qf->table[run_start].is_continuation);

        do {
            scan = (scan + 1) & qf->slot_mask;
        } while (!qf->table[scan].is_occupied);
    }
    return run_start;
}

/* Перевірка наявності ключа у фільтрі */
bool qf_lookup(const QuotientFilter *qf, const void *key, size_t len) {
    uint64_t hash = hash_bytes(key, len);
    size_t f_q = (hash >> qf->r_bits) & qf->slot_mask;
    uint8_t f_r = (uint8_t)(hash & (((uint64_t)1 << qf->r_bits) - 1));

    if (!qf->table[f_q].is_occupied) {
        return false;
    }

    size_t curr = find_run_start(qf, f_q);

    do {
        if (qf->table[curr].remainder == f_r) {
            return true;
        }
        if (qf->table[curr].remainder > f_r) {
            return false;
        }
        curr = (curr + 1) & qf->slot_mask;
    } while (qf->table[curr].is_continuation);

    return false;
}

/* Вставка нового елемента в квошієнтний фільтр */
bool qf_insert(QuotientFilter *qf, const void *key, size_t len) {
    if ((double)qf->count / (double)qf->num_slots >= MAX_LOAD_FACTOR) {
        return false;
    }

    uint64_t hash = hash_bytes(key, len);
    size_t f_q = (hash >> qf->r_bits) & qf->slot_mask;
    uint8_t f_r = (uint8_t)(hash & (((uint64_t)1 << qf->r_bits) - 1));

    if (slot_is_empty(&qf->table[f_q])) {
        qf->table[f_q].is_occupied = 1;
        qf->table[f_q].is_continuation = 0;
        qf->table[f_q].is_shifted = 0;
        qf->table[f_q].remainder = f_r;
        qf->count++;
        return true;
    }

    if (!qf->table[f_q].is_occupied) {
        /* Канонічний слот порожній від своїх, але зайнятий чужим зсунутим елементом */
        qf->table[f_q].is_occupied = 1;
    }

    size_t insert_pos = find_run_start(qf, f_q);
    bool has_run = qf->table[f_q].is_occupied;

    if (has_run) {
        while (qf->table[insert_pos].remainder < f_r && qf->table[(insert_pos + 1) & qf->slot_mask].is_continuation) {
            insert_pos = (insert_pos + 1) & qf->slot_mask;
        }
        if (qf->table[insert_pos].remainder < f_r) {
            insert_pos = (insert_pos + 1) & qf->slot_mask;
        }
    }

    /* Каскадний зсув вправо для звільнення insert_pos */
    QFSlot prev_slot = { .is_occupied = 0, .is_continuation = 0, .is_shifted = (insert_pos != f_q), .remainder = f_r };
    size_t curr = insert_pos;

    while (true) {
        QFSlot temp = qf->table[curr];
        bool was_empty = slot_is_empty(&temp);

        qf->table[curr].remainder = prev_slot.remainder;
        qf->table[curr].is_shifted = (curr != f_q);
        if (curr == insert_pos && has_run && insert_pos != find_run_start(qf, f_q)) {
            qf->table[curr].is_continuation = 1;
        }

        if (was_empty) break;

        prev_slot = temp;
        prev_slot.is_shifted = 1;
        curr = (curr + 1) & qf->slot_mask;
    }

    qf->count++;
    return true;
}

/* Детерміноване видалення елемента */
bool qf_delete(QuotientFilter *qf, const void *key, size_t len) {
    uint64_t hash = hash_bytes(key, len);
    size_t f_q = (hash >> qf->r_bits) & qf->slot_mask;
    uint8_t f_r = (uint8_t)(hash & (((uint64_t)1 << qf->r_bits) - 1));

    if (!qf->table[f_q].is_occupied) return false;

    size_t run_start = find_run_start(qf, f_q);
    size_t target = run_start;
    bool found = false;

    do {
        if (qf->table[target].remainder == f_r) {
            found = true;
            break;
        }
        target = (target + 1) & qf->slot_mask;
    } while (qf->table[target].is_continuation);

    if (!found) return false;

    /* Зсув кластера вліво для заповнення дірки */
    size_t curr = target;
    while (true) {
        size_t next = (curr + 1) & qf->slot_mask;
        if (slot_is_empty(&qf->table[next]) || !qf->table[next].is_shifted) {
            memset(&qf->table[curr], 0, sizeof(QFSlot));
            break;
        }
        qf->table[curr].remainder = qf->table[next].remainder;
        qf->table[curr].is_continuation = qf->table[next].is_continuation;
        qf->table[curr].is_shifted = (curr != f_q);
        curr = next;
    }

    qf->count--;
    return true;
}
```
```cpp
#include <cstdint>
#include <cstddef>
#include <vector>
#include <string_view>
#include <optional>
#include <span>
#include <memory>

class QuotientFilter {
public:
    struct Slot {
        uint8_t is_occupied : 1 = 0;
        uint8_t is_continuation : 1 = 0;
        uint8_t is_shifted : 1 = 0;
        uint8_t remainder : 5 = 0;
    };

    static constexpr double kMaxLoadFactor = 0.85;

    explicit QuotientFilter(size_t q_bits, size_t r_bits)
        : q_bits_(q_bits),
          r_bits_(r_bits),
          num_slots_(size_t{1} << q_bits),
          slot_mask_(num_slots_ - 1),
          table_(num_slots_) {}

    [[nodiscard]] size_t size() const noexcept { return count_; }
    [[nodiscard]] size_t capacity() const noexcept { return num_slots_; }
    [[nodiscard]] double load_factor() const noexcept {
        return static_cast<double>(count_) / static_cast<double>(num_slots_);
    }

    [[nodiscard]] bool contains(std::string_view key) const noexcept {
        const auto hash = hash_bytes(key);
        const size_t f_q = (hash >> r_bits_) & slot_mask_;
        const auto f_r = static_cast<uint8_t>(hash & ((uint64_t{1} << r_bits_) - 1));

        if (!table_[f_q].is_occupied) {
            return false;
        }

        size_t curr = find_run_start(f_q);

        do {
            if (table_[curr].remainder == f_r) {
                return true;
            }
            if (table_[curr].remainder > f_r) {
                return false;
            }
            curr = (curr + 1) & slot_mask_;
        } while (table_[curr].is_continuation);

        return false;
    }

    bool insert(std::string_view key) {
        if (load_factor() >= kMaxLoadFactor) {
            return false;
        }

        const auto hash = hash_bytes(key);
        const size_t f_q = (hash >> r_bits_) & slot_mask_;
        const auto f_r = static_cast<uint8_t>(hash & ((uint64_t{1} << r_bits_) - 1));

        if (is_empty(table_[f_q])) {
            table_[f_q].is_occupied = 1;
            table_[f_q].is_continuation = 0;
            table_[f_q].is_shifted = 0;
            table_[f_q].remainder = f_r;
            ++count_;
            return true;
        }

        if (!table_[f_q].is_occupied) {
            table_[f_q].is_occupied = 1;
        }

        size_t insert_pos = find_run_start(f_q);
        const bool has_run = (table_[f_q].is_occupied == 1);

        if (has_run) {
            while (table_[insert_pos].remainder < f_r && table_[(insert_pos + 1) & slot_mask_].is_continuation) {
                insert_pos = (insert_pos + 1) & slot_mask_;
            }
            if (table_[insert_pos].remainder < f_r) {
                insert_pos = (insert_pos + 1) & slot_mask_;
            }
        }

        Slot prev_slot{
            .is_occupied = 0,
            .is_continuation = 0,
            .is_shifted = static_cast<uint8_t>(insert_pos != f_q ? 1 : 0),
            .remainder = f_r
        };
        size_t curr = insert_pos;

        while (true) {
            Slot temp = table_[curr];
            const bool was_empty = is_empty(temp);

            table_[curr].remainder = prev_slot.remainder;
            table_[curr].is_shifted = static_cast<uint8_t>(curr != f_q ? 1 : 0);
            if (curr == insert_pos && has_run && insert_pos != find_run_start(f_q)) {
                table_[curr].is_continuation = 1;
            }

            if (was_empty) break;

            prev_slot = temp;
            prev_slot.is_shifted = 1;
            curr = (curr + 1) & slot_mask_;
        }

        ++count_;
        return true;
    }

    bool remove(std::string_view key) noexcept {
        const auto hash = hash_bytes(key);
        const size_t f_q = (hash >> r_bits_) & slot_mask_;
        const auto f_r = static_cast<uint8_t>(hash & ((uint64_t{1} << r_bits_) - 1));

        if (!table_[f_q].is_occupied) return false;

        const size_t run_start = find_run_start(f_q);
        size_t target = run_start;
        bool found = false;

        do {
            if (table_[target].remainder == f_r) {
                found = true;
                break;
            }
            target = (target + 1) & slot_mask_;
        } while (table_[target].is_continuation);

        if (!found) return false;

        size_t curr = target;
        while (true) {
            const size_t next = (curr + 1) & slot_mask_;
            if (is_empty(table_[next]) || !table_[next].is_shifted) {
                table_[curr] = Slot{};
                break;
            }
            table_[curr].remainder = table_[next].remainder;
            table_[curr].is_continuation = table_[next].is_continuation;
            table_[curr].is_shifted = static_cast<uint8_t>(curr != f_q ? 1 : 0);
            curr = next;
        }

        --count_;
        return true;
    }

private:
    size_t q_bits_;
    size_t r_bits_;
    size_t num_slots_;
    size_t slot_mask_;
    size_t count_ = 0;
    std::vector<Slot> table_;

    [[nodiscard]] static bool is_empty(const Slot& s) noexcept {
        return !s.is_occupied && !s.is_continuation && !s.is_shifted;
    }

    [[nodiscard]] static uint64_t hash_bytes(std::string_view data) noexcept {
        uint64_t h = 14695981039346656037ULL;
        for (const char c : data) {
            h ^= static_cast<uint8_t>(c);
            h *= 1099511628211ULL;
        }
        return h;
    }

    [[nodiscard]] size_t find_run_start(size_t f_q) const noexcept {
        size_t curr = f_q;
        while (table_[curr].is_shifted) {
            curr = (curr - 1) & slot_mask_;
        }

        size_t scan = curr;
        size_t run_start = curr;

        while (scan != f_q) {
            do {
                run_start = (run_start + 1) & slot_mask_;
            } while (table_[run_start].is_continuation);

            do {
                scan = (scan + 1) & slot_mask_;
            } while (!table_[scan].is_occupied);
        }
        return run_start;
    }
};
```
:::

## 6. Інженерні пастки та крайові випадки

1. **Критичне переповнення та деградація кластерів**: При коефіцієнті заповнення `α > 0.85..0.90` окремі кластери починають зливатися у гігантські неперервні ділянки. У такому стані час пошуку початку набігу різко зростає з `O(1)` до `O(n)`. Рекомендовано ініціювати динамічне подвоєння фільтра при досягненні `α = 0.80`.
2. **Циклічний перехід через нульовий індекс (Wrap-around)**: Кластери, які починаються наприкінці таблиці (наприклад, у слотах `m - 2`, `m - 1`), можуть перетинати межу таблиці та продовжуватися у слотах `0, 1, 2`. При роботі з циклічним індексуванням маска `curr & slot_mask` надійно запобігає виходу за межі виділеної пам'яті.
3. **Паралелізм та блокування**: Оскільки всі операції вставки та пошуку локалізовані в межах одного суцільного кластера, квошієнтний фільтр підтримує високоефективне сегментне блокування (Fine-grained Striped Locking): замість блокування всієї структури один потік блокує лише невеликий діапазон слотів (наприклад, блок із 64 комірок), забезпечуючи лінійне масштабування на багатоядерних серверах.
