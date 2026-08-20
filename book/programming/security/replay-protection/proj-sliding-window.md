# ⚙️ Реалізація ковзного бітового вікна захисту від повторів (RFC 6479)

У високошвидкісних мережевих протоколах (IPsec ESP, DTLS 1.3, WireGuard) пакети передаються через ненадійні дейтаграми без збереження з'єднання. Пакети можуть втрачатися, надходити не по порядку через наявність паралельних маршрутів або навмисно повторюватися зловмисником.

Реалізація ковзного вікна на основі масиву 64-бітних машинних слів (відповідно до стандарту RFC 6479) забезпечує детермінований константний час перевірки `O(1)`, нульове динамічне виділення пам'яті та захист від атак відмови в обслуговуванні (DoS).

---

### Архітектура та бітова модель ковзного вікна

Фільтр відстежує послідовність пакетів за допомогою двох компонентів:
1. **Базового номера `seq_max`** — найбільшого валідного порядкового номера, який було успішно верифіковано та зафіксовано.
2. **Бітового масиву `bitmap`** — масиву беззнакових 64-бітних цілих чисел `uint64_t`. Ширина вікна `W` кратна 64 бітам (для `WINDOW_WORDS = 2` ширина вікна становить 128 бітів).

Біт на позиції `0` у першому слові масиву завжди відповідає пакету з номером `seq_max`. Кожен наступний біт на позиції `offset` представляє пакет із номером `seq_max - offset`.

```
Слово 0 (bitmap[0]):  [біт 63: seq_max - 63]  ... [біт 1: seq_max - 1] [біт 0: seq_max]
Слово 1 (bitmap[1]):  [біт 63: seq_max - 127] ... [біт 1: seq_max - 65] [біт 0: seq_max - 64]
```

#### Проблема переповнення 32-бітних лічильників у швидкісних мережах

У ранніх версіях протоколу IPsec (RFC 2401) використовувався 32-бітний лічильник послідовності. У сучасних мережах із пропускною здатністю 100 Гбіт/с (100GbE) потік мінімальних 64-байтних пакетів досягає 148 мільйонів пакетів за секунду:

```
T_overflow = 2³² / 148 000 000 пакетів/с ≈ 29 секунд
```

Це означає, що 32-бітний лічильник вичерпується менш ніж за пів хвилини. Якщо не зупинити передачу, значення лічильника переповниться і почнеться з нуля (`wrap-around`). Приймальне вікно сприйме ці нові пакети як старі повтори й заблокує весь канал зв'язку.

Саме тому сучасні стандарти (RFC 4303, RFC 6479) вимагають використання 64-бітних лічильників. При швидкості 148 мільйонів пакетів за секунду 64-бітний простір чисел вичерпається лише через:

```
T_overflow_64 = 2⁶⁴ / 148 000 000 пакетів/с ≈ 1.24 · 10¹¹ секунд ≈ 3940 років
```

#### Локальність даних та ефективність кешу процесора (L1 Cache Line)

Компактність структури `replay_window_t` (8 байтів для `seq_max` + 16 байтів для `bitmap[2]` = 24 байти) має вирішальне значення для продуктивності мережевих стеків (DPDK, FD.io VPP).

Уся структура вікна разом із криптографічними ключами симетричного шифрування та верифікації вміщується в один 64-байтний рядок кешу першого рівня (L1 Data Cache Line). Під час обробки пакета процесор здійснює рівно одне читання з пам'яті:
- Бітова перевірка `check()` виконується за 3 такти CPU без звернення до оперативної пам'яті RAM.
- Якщо пакет виявляється застарілим або підробленим, стек негайно скидає його без виклику важких інструкцій розшифрування AES-NI або AVX-512, захищаючи ядро від перевантаження обчислювальних блоків.

---

### Вихідний код реалізації (C та C++)

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <stdio.h>
#include <assert.h>

#define WINDOW_WORDS 2
#define BITS_PER_WORD 64
#define WINDOW_BITS (WINDOW_WORDS * BITS_PER_WORD)

typedef enum {
    REPLAY_OK = 0,
    REPLAY_DUPLICATE = 1,
    REPLAY_TOO_OLD = 2
} replay_status_t;

typedef struct {
    uint64_t seq_max;                       // найбільший підтверджений номер
    uint64_t bitmap[WINDOW_WORDS];          // бітова маска вікна
} replay_window_t;

// Ініціалізація або повне скидання стану вікна
void replay_window_init(replay_window_t *w) {
    w->seq_max = 0;
    memset(w->bitmap, 0, sizeof(w->bitmap));
}

// 1. Попередня перевірка без зміни стану (виконується ДО розшифрування/HMAC)
replay_status_t replay_window_check(const replay_window_t *w, uint64_t seq) {
    if (seq == 0) {
        return REPLAY_TOO_OLD;              // порядковий номер 0 заборонено стандартами
    }

    if (seq > w->seq_max) {
        return REPLAY_OK;                   // новий пакет попереду вікна
    }

    uint64_t diff = w->seq_max - seq;
    if (diff >= WINDOW_BITS) {
        return REPLAY_TOO_OLD;              // пакет занадто старий, лівіше вікна
    }

    size_t word_idx = (size_t)(diff / BITS_PER_WORD);
    size_t bit_idx = (size_t)(diff % BITS_PER_WORD);

    if ((w->bitmap[word_idx] & ((uint64_t)1 << bit_idx)) != 0) {
        return REPLAY_DUPLICATE;            // пакет уже був успішно отриманий
    }

    return REPLAY_OK;
}

// 2. Фіксація номера у вікні (виконується ТІЛЬКИ ПІСЛЯ успішної перевірки криптографії)
void replay_window_commit(replay_window_t *w, uint64_t seq) {
    if (seq > w->seq_max) {
        uint64_t diff = seq - w->seq_max;
        if (diff < WINDOW_BITS) {
            // Зсув бітової маски вліво на diff бітів через межі 64-бітних слів
            size_t word_shift = (size_t)(diff / BITS_PER_WORD);
            size_t bit_shift = (size_t)(diff % BITS_PER_WORD);

            for (int i = WINDOW_WORDS - 1; i >= 0; --i) {
                int src = i - (int)word_shift;
                uint64_t val = (src >= 0) ? (w->bitmap[src] << bit_shift) : 0;
                if (src > 0 && bit_shift > 0) {
                    val |= (w->bitmap[src - 1] >> (BITS_PER_WORD - bit_shift));
                }
                w->bitmap[i] = val;
            }
        } else {
            // Стрибок більше або дорівнює ширині вікна: очищаємо всю стару маску
            memset(w->bitmap, 0, sizeof(w->bitmap));
        }

        w->seq_max = seq;
        w->bitmap[0] |= (uint64_t)1;        // позначаємо біт 0 для нового seq_max
    } else {
        uint64_t diff = w->seq_max - seq;
        if (diff < WINDOW_BITS) {
            size_t word_idx = (size_t)(diff / BITS_PER_WORD);
            size_t bit_idx = (size_t)(diff % BITS_PER_WORD);
            w->bitmap[word_idx] |= ((uint64_t)1 << bit_idx);
        }
    }
}
```
```cpp
#include <cstdint>
#include <cstddef>
#include <array>
#include <iostream>
#include <cassert>

enum class ReplayStatus : uint8_t {
    Ok = 0,
    Duplicate = 1,
    TooOld = 2
};

template <size_t WindowWords = 2>
class ReplayWindow {
public:
    static constexpr size_t BitsPerWord = 64;
    static constexpr size_t TotalBits = WindowWords * BitsPerWord;

    constexpr ReplayWindow() noexcept {
        reset();
    }

    void reset() noexcept {
        seq_max_ = 0;
        bitmap_.fill(0);
    }

    // Фаза 1: Перевірка без зміни стану (перед перевіркою AEAD/HMAC)
    [[nodiscard]] ReplayStatus check(uint64_t seq) const noexcept {
        if (seq == 0) {
            return ReplayStatus::TooOld;
        }

        if (seq > seq_max_) {
            return ReplayStatus::Ok;
        }

        const uint64_t diff = seq_max_ - seq;
        if (diff >= TotalBits) {
            return ReplayStatus::TooOld;
        }

        const size_t word_idx = diff / BitsPerWord;
        const size_t bit_idx = diff % BitsPerWord;

        if ((bitmap_[word_idx] & (uint64_t{1} << bit_idx)) != 0) {
            return ReplayStatus::Duplicate;
        }

        return ReplayStatus::Ok;
    }

    // Фаза 2: Фіксація пакета після успішної криптографічної перевірки
    void commit(uint64_t seq) noexcept {
        if (seq > seq_max_) {
            const uint64_t diff = seq - seq_max_;
            if (diff < TotalBits) {
                const size_t word_shift = diff / BitsPerWord;
                const size_t bit_shift = diff % BitsPerWord;

                for (int i = static_cast<int>(WindowWords) - 1; i >= 0; --i) {
                    const int src = i - static_cast<int>(word_shift);
                    uint64_t val = (src >= 0) ? (bitmap_[src] << bit_shift) : 0;
                    if (src > 0 && bit_shift > 0) {
                        val |= (bitmap_[src - 1] >> (BitsPerWord - bit_shift));
                    }
                    bitmap_[i] = val;
                }
            } else {
                bitmap_.fill(0);
            }

            seq_max_ = seq;
            bitmap_[0] |= uint64_t{1};
        } else {
            const uint64_t diff = seq_max_ - seq;
            if (diff < TotalBits) {
                const size_t word_idx = diff / BitsPerWord;
                const size_t bit_idx = diff % BitsPerWord;
                bitmap_[word_idx] |= (uint64_t{1} << bit_idx);
            }
        }
    }

    [[nodiscard]] uint64_t max_sequence() const noexcept {
        return seq_max_;
    }

private:
    uint64_t seq_max_{0};
    std::array<uint64_t, WindowWords> bitmap_{};
};
```
:::

---

### Покроковий розбір механіки багатослівного зсуву

Найбільш складною частиною алгоритму є операція зсуву бітової маски, коли величина випередження `diff` не кратна 64 бітам. Розгляньмо конкретний покроковий приклад виконання:

1. Нехай поточний максимум `seq_max = 100`, а ширина вікна `W = 128` (два слова `bitmap[0]` та `bitmap[1]`).
2. Надходить новий валідний пакет із номером `seq = 105`. Величина випередження становить `diff = 5` бітів.
3. Слово `bitmap[1]` повинно отримати старші 59 бітів від старого слова `bitmap[1]`, а його молодші 5 бітів мають бути заповнені старшими 5 бітами зі слова `bitmap[0]`.
4. Для цього обчислюється складений перенос розрядів:
   `val = (bitmap[0] << 5) | (bitmap[1] >> (64 - 5))`
5. Слово `bitmap[0]` зсувається вліво на 5 бітів, а його нульовий біт встановлюється в `1`, позначаючи прибуття пакета `105`.

Завдяки такій структурі всі бітові індекси зберігають точне математичне значення `offset = seq_max - seq` без використання складних динамічних списків.

---

### Тестування крайових випадків та перевірка інваріантів

Коректність роботи фільтра перевіряється набором обов'язкових сценаріїв:

1. **Послідовне надходження пакетів:** Пакети `1, 2, 3, ..., 1000` проходять перевірку, `seq_max` монотонно зростає.
2. **Пакет-дублікат (Replay):** Пакет `50` надходить повторно, коли `seq_max = 50` або `seq_max = 60`. Функція `check()` негайно повертає `REPLAY_DUPLICATE`.
3. **Перевпорядкування всередині вікна:** Пакети надходять у порядку `1, 5, 2, 4, 3`. Усі пакети приймаються без помилок, пропущені біти заповнюються.
4. **Застарілий пакет:** При `seq_max = 200` пакет `S = 50` (відставання `diff = 150 > 128`) повертає `REPLAY_TOO_OLD`.
5. **Гігантський стрибок уперед:** При `seq_max = 10` надходить валідний пакет `S = 10000`. Вікно повністю скидається, `seq_max` стає рівним `10000`, а всі пакети з номерами менше `9873` стають застарілими.

:::tabs
```c
void run_replay_tests(void) {
    replay_window_t w;
    replay_window_init(&w);

    // 1. Нульовий номер відхиляється
    assert(replay_window_check(&w, 0) == REPLAY_TOO_OLD);

    // 2. Перший пакет
    assert(replay_window_check(&w, 1) == REPLAY_OK);
    replay_window_commit(&w, 1);
    assert(w.seq_max == 1);

    // 3. Дублікат першого пакета
    assert(replay_window_check(&w, 1) == REPLAY_DUPLICATE);

    // 4. Стрибок уперед на 100
    assert(replay_window_check(&w, 100) == REPLAY_OK);
    replay_window_commit(&w, 100);
    assert(w.seq_max == 100);

    // 5. Запізнілий пакет у межах вікна (100 - 95 = 5 < 128)
    assert(replay_window_check(&w, 95) == REPLAY_OK);
    replay_window_commit(&w, 95);
    assert(replay_window_check(&w, 95) == REPLAY_DUPLICATE);

    // 6. Занадто старий пакет (100 - 1 = 99 < 128, але якщо seq_max зросте до 300)
    replay_window_commit(&w, 300);
    assert(replay_window_check(&w, 95) == REPLAY_TOO_OLD);
}
```
```cpp
void run_replay_tests_cpp() {
    ReplayWindow<2> w;

    // 1. Нульовий номер відхиляється
    assert(w.check(0) == ReplayStatus::TooOld);

    // 2. Перший пакет
    assert(w.check(1) == ReplayStatus::Ok);
    w.commit(1);
    assert(w.max_sequence() == 1);

    // 3. Дублікат першого пакета
    assert(w.check(1) == ReplayStatus::Duplicate);

    // 4. Стрибок уперед на 100
    assert(w.check(100) == ReplayStatus::Ok);
    w.commit(100);
    assert(w.max_sequence() == 100);

    // 5. Запізнілий пакет у межах вікна (100 - 95 = 5 < 128)
    assert(w.check(95) == ReplayStatus::Ok);
    w.commit(95);
    assert(w.check(95) == ReplayStatus::Duplicate);

    // 6. Застарілий пакет після зсуву вікна
    w.commit(300);
    assert(w.check(95) == ReplayStatus::TooOld);
}
```
:::

---

### Багатопоточність та оптимізація в ядрі Linux (XFRM)

У ядрі Linux (підсистема IPsec XFRM) стан кожного тунелю представлений структурою `struct xfrm_state`. Перевірка номера послідовності здійснюється у функції `xfrm_replay_check()`, а фіксація — у `xfrm_replay_advance()`.

Для уникнення блокувань на багатоядерних серверах застосовують два рівні оптимізації:
1. **Lock-Free Pre-Check:** Попередня перевірка `check()` виконується без захоплення м'ютекса (читання атомарного значення `seq_max`). Якщо пакет явно дубльований або застарілий, ядро відкидає його до входу в криптографічний стек.
2. **Спінлок фіксації (Commit Spinlock):** Тільки після успішного розшифрування та перевірки ICV ядро бере швидкий спінлок `x->lock`, виконує повторну швидку перевірку (щоб уникнути стану гонки з іншим ядром) та оновлює бітову маску.
3. **Апаратне прискорення (NIC Offload):** Сучасні мережеві адаптери (Mellanox ConnectX, Intel E810) реалізують ковзне вікно безпосередньо в кремнії ASIC, скидаючи переграні пакети на рівні фізичного трансивера без залучення процесора хоста.
