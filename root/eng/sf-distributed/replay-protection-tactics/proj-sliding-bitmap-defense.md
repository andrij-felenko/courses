# ⚙️ Високопродуктивний ковзний бітмап захисту від перегравання

У високошвидкісних мережевих протоколах (IPsec ESP, WireGuard, QUIC), розподілених брокерах повідомлень та інфраструктурі фінансового трейдингу потоки даних досягають десятків мільйонів пакетів на секунду. Перевірка кожного вхідного повідомлення через виклик розподіленого сховища ключ-значення (Redis) або виконання транзакційного запиту до реляційної бази даних створює неприпустиму затримку в кілька мілісекунд, породжує мережевий оверхед і вичерпує пропускну здатність шини пам'яті.

Ковзний бітмапний фільтр (Sliding Bitmap Filter) вирішує задачу виявлення дублікатів та застарілих пакетів за `O(1)` часу та з фіксованими `O(1)` витратами пам'яті (лічені байти на рівні L1-кешу процесора), коректно витримуючи перевпорядкування пакетів, викликане асиметричною маршрутизацією та джитером каналів.

## Задача та інваріанти структури даних

Необхідно спроєктувати структуру даних, яка для кожного вхідного 64-бітного порядкового номера `seq` повертає одне з двох рішень:
1. `ACCEPT`: пакет отримано вперше, його номер знаходиться у межах допустимого вікна або перевищує поточний максимум. Стан фільтра оновлюється.
2. `REJECT`: пакет є дублікатом (вже був оброблений раніше) або прибув із запізненням, що перевищує розмір вікна `W`.

Фільтр оперує двома основними величинами:
* `max_seq`: найбільший порядковий номер, успішно прийнятий і зафіксований фільтром на даний момент.
* `bitmap`: 64-бітова бітова маска (або масив слів `uint64_t`), де кожен `k`-й біт вказує на факт отримання пакета з порядковим номером `max_seq - k`.

```
[max_seq - 63] ... [max_seq - 2] [max_seq - 1] [max_seq]
      ↑                                           ↑
  старший біт                                 молодший біт (0-й)
```

Математично простір порядкових номерів ділиться на три взаємовиключні зони відносно поточного стану `(max_seq, W)`:
* **Зона застарілих пакетів (`seq ≤ max_seq - W`):** пакет відстає від лідера більше ніж на розмір вікна. Інформація про його статус уже витіснена з пам'яті. Такий пакет безумовно відкидається для запобігання прориву дедуплікації.
* **Зона активного вікна (`max_seq - W < seq ≤ max_seq`):** пакет потрапляє у діапазон пам'яті. Обчислюється бітове зміщення `diff = max_seq - seq`. Якщо `(bitmap & (1 << diff)) != 0`, пакет уже оброблено (дублікат); якщо біт нульовий — пакет приймається вперше, а біт перемикається в одиницю.
* **Зона випередження (`seq > max_seq`):** надійшов новий максимальний номер. Вікно зміщується вліво на `diff = seq - max_seq` бітів, біт нульової позиції ставиться в одиницю, а `max_seq` стає рівним `seq`.

## Реалізація фільтра мовами C та C++

Нижче наведено промислові реалізації ковзного фільтра з розміром вікна 64 біти. Для забезпечення високої швидкодії всі операції зведені до прямих регістрових зсувів без виділення динамічної пам'яті.

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define ANTI_REPLAY_WIN_SIZE 64ULL

typedef struct {
    uint64_t max_seq;
    uint64_t bitmap;
    uint64_t packets_accepted;
    uint64_t packets_rejected_duplicate;
    uint64_t packets_rejected_stale;
} anti_replay_filter_t;

void anti_replay_init(anti_replay_filter_t *filter) {
    if (!filter) return;
    filter->max_seq = 0;
    filter->bitmap = 0;
    filter->packets_accepted = 0;
    filter->packets_rejected_duplicate = 0;
    filter->packets_rejected_stale = 0;
}

/*
 * Перевірка та оновлення стану фільтра за один крок.
 * Повертає true, якщо пакет валідний і прийнятий; false, якщо це повтор або застарілий пакет.
 */
bool anti_replay_process(anti_replay_filter_t *filter, uint64_t seq) {
    if (!filter) return false;

    /* Перший пакет у системі */
    if (filter->packets_accepted == 0 && filter->max_seq == 0 && filter->bitmap == 0) {
        filter->max_seq = seq;
        filter->bitmap = 1ULL;
        filter->packets_accepted++;
        return true;
    }

    /* Випадок 1: Номер більший за поточний максимум (рух вікна вперед) */
    if (seq > filter->max_seq) {
        uint64_t diff = seq - filter->max_seq;
        if (diff < ANTI_REPLAY_WIN_SIZE) {
            filter->bitmap = (filter->bitmap << diff) | 1ULL;
        } else {
            /* Стрибок номера перевищив розмір усього вікна: історія повністю витісняється */
            filter->bitmap = 1ULL;
        }
        filter->max_seq = seq;
        filter->packets_accepted++;
        return true;
    }

    /* Випадок 2: Номер застарілий і випав за межі лівого краю вікна */
    uint64_t diff = filter->max_seq - seq;
    if (diff >= ANTI_REPLAY_WIN_SIZE) {
        filter->packets_rejected_stale++;
        return false;
    }

    /* Випадок 3: Номер потрапляє всередину поточного вікна */
    uint64_t mask = 1ULL << diff;
    if (filter->bitmap & mask) {
        /* Біт уже встановлено — це повторне перегравання */
        filter->packets_rejected_duplicate++;
        return false;
    }

    /* Пакет легітимний, встановлюємо відповідний біт */
    filter->bitmap |= mask;
    filter->packets_accepted++;
    return true;
}
```
```cpp
#include <cstdint>
#include <concepts>
#include <optional>
#include <atomic>
#include <string_view>

enum class ReplayStatus {
    Accepted,
    Duplicate,
    Stale
};

template <std::size_t WindowSize = 64>
requires (WindowSize == 64) // Для розширених розмірів використовується блоковий масив слів
class AntiReplayWindow {
public:
    constexpr AntiReplayWindow() noexcept = default;

    [[nodiscard]] ReplayStatus process(uint64_t seq) noexcept {
        // Обробка найпершого пакета після запуску сесії
        if (accepted_count_ == 0 && max_seq_ == 0 && bitmap_ == 0) {
            max_seq_ = seq;
            bitmap_ = 1ULL;
            ++accepted_count_;
            return ReplayStatus::Accepted;
        }

        // Сценарій 1: Новий максимальний порядковий номер (просування вікна)
        if (seq > max_seq_) {
            const uint64_t diff = seq - max_seq_;
            if (diff < WindowSize) {
                bitmap_ = (bitmap_ << diff) | 1ULL;
            } else {
                bitmap_ = 1ULL; // Повне витіснення попереднього діапазону
            }
            max_seq_ = seq;
            ++accepted_count_;
            return ReplayStatus::Accepted;
        }

        // Сценарій 2: Застарілий номер за межами лівої межі активного вікна
        const uint64_t diff = max_seq_ - seq;
        if (diff >= WindowSize) {
            ++stale_count_;
            return ReplayStatus::Stale;
        }

        // Сценарій 3: Номер усередині активного ковзного вікна
        const uint64_t bit_mask = 1ULL << diff;
        if ((bitmap_ & bit_mask) != 0) {
            ++duplicate_count_;
            return ReplayStatus::Duplicate;
        }

        bitmap_ |= bit_mask;
        ++accepted_count_;
        return ReplayStatus::Accepted;
    }

    [[nodiscard]] uint64_t max_sequence() const noexcept { return max_seq_; }
    [[nodiscard]] uint64_t accepted_count() const noexcept { return accepted_count_; }
    [[nodiscard]] uint64_t duplicate_count() const noexcept { return duplicate_count_; }
    [[nodiscard]] uint64_t stale_count() const noexcept { return stale_count_; }

private:
    uint64_t max_seq_{0};
    uint64_t bitmap_{0};
    uint64_t accepted_count_{0};
    uint64_t duplicate_count_{0};
    uint64_t stale_count_{0};
};
```
:::

## Масштабування вікна: блокова багаторівнева структура (RFC 6479)

Коли пропускна здатність мережі досягає 40–100 Гбіт/с, а мережевий джитер (розкид часу доставки) становить 50–100 мілісекунд, 64 бітів стає недостатньо: швидкі пакети випереджають повільні на тисячі позицій, викликаючи помилкове відхилення легітимних пакетів.

Стандарт RFC 6479 масштабує бітмап на масив із `M` 64-бітних слів (наприклад, `M = 16`, що дає вікно в 1024 біти). Замість повільного бітового зсуву всього масиву пам'яті використовується кільцевий буфер слів із блоковою індексацією:

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define WORDS_COUNT 16
#define TOTAL_WINDOW_BITS (WORDS_COUNT * 64)

typedef struct {
    uint64_t max_seq;
    uint64_t window[WORDS_COUNT];
} multiword_anti_replay_t;

void multiword_init(multiword_anti_replay_t *filter) {
    if (!filter) return;
    filter->max_seq = 0;
    memset(filter->window, 0, sizeof(filter->window));
}

bool multiword_check_and_update(multiword_anti_replay_t *filter, uint64_t seq) {
    if (seq > filter->max_seq) {
        uint64_t diff = seq - filter->max_seq;
        if (diff < TOTAL_WINDOW_BITS) {
            uint64_t words_shift = diff / 64;
            uint64_t bits_shift = diff % 64;
            
            // Зсув слів у буфері при необхідності
            for (int i = WORDS_COUNT - 1; i >= 0; --i) {
                uint64_t src = (i >= (int)words_shift) ? filter->window[i - words_shift] : 0ULL;
                uint64_t prev = (i > (int)words_shift && bits_shift > 0) ? filter->window[i - words_shift - 1] : 0ULL;
                filter->window[i] = (src << bits_shift) | (bits_shift > 0 ? (prev >> (64 - bits_shift)) : 0ULL);
            }
            filter->window[0] |= 1ULL;
        } else {
            memset(filter->window, 0, sizeof(filter->window));
            filter->window[0] = 1ULL;
        }
        filter->max_seq = seq;
        return true;
    }

    uint64_t diff = filter->max_seq - seq;
    if (diff >= TOTAL_WINDOW_BITS) {
        return false; // Застарілий пакет
    }

    uint64_t word_idx = diff / 64;
    uint64_t bit_idx = diff % 64;
    uint64_t mask = 1ULL << bit_idx;

    if (filter->window[word_idx] & mask) {
        return false; // Дублікат
    }

    filter->window[word_idx] |= mask;
    return true;
}
```
```cpp
#include <array>
#include <cstdint>
#include <algorithm>

template <std::size_t NumWords = 16>
class LargeAntiReplayFilter {
public:
    static constexpr std::size_t TotalBits = NumWords * 64;

    LargeAntiReplayFilter() noexcept {
        window_.fill(0);
    }

    [[nodiscard]] bool process(uint64_t seq) noexcept {
        if (seq > max_seq_) {
            const uint64_t diff = seq - max_seq_;
            if (diff < TotalBits) {
                const std::size_t words_shift = diff / 64;
                const std::size_t bits_shift = diff % 64;

                for (std::size_t i = NumWords; i-- > 0;) {
                    uint64_t src = (i >= words_shift) ? window_[i - words_shift] : 0ULL;
                    uint64_t prev = (i > words_shift && bits_shift > 0) ? window_[i - words_shift - 1] : 0ULL;
                    window_[i] = (src << bits_shift) | (bits_shift > 0 ? (prev >> (64 - bits_shift)) : 0ULL);
                }
                window_[0] |= 1ULL;
            } else {
                window_.fill(0);
                window_[0] = 1ULL;
            }
            max_seq_ = seq;
            return true;
        }

        const uint64_t diff = max_seq_ - seq;
        if (diff >= TotalBits) {
            return false;
        }

        const std::size_t word_idx = diff / 64;
        const std::size_t bit_idx = diff % 64;
        const uint64_t mask = 1ULL << bit_idx;

        if ((window_[word_idx] & mask) != 0) {
            return false;
        }

        window_[word_idx] |= mask;
        return true;
    }

private:
    uint64_t max_seq_{0};
    std::array<uint64_t, NumWords> window_{};
};
```
:::

## Інтеграція в криптографічний конвеєр та захист від DoS-атак

Критичною архітектурною помилкою є зміна стану фільтра до завершення перевірки криптографічного підпису або цілісності повідомлення.

Якщо зловмисник відправляє підроблений неавтентифікований пакет із порядковим номером `seq = max_seq + 1 000 000`, і фільтр негайно зміщує вікно вперед, це спричиняє повний відрив історії: всі подальші легітимні зашифровані пакети будуть безумовно відкинуті як застарілі.

Правильний промисловий конвеєр обробки складається з трьох обов'язкових кроків:

1. **Попередня перевірка (Pre-check):**
   Фільтр читає `seq` і перевіряє, чи не є номер застарілим (`seq <= max_seq - W`) або вже відміченим у бітмапі, але **не змінює стан**. Якщо номер некоректний, пакет відкидається негайно. Це відсікає лавину мережевих повторів без навантаження на підсистему шифрування.

2. **Криптографічна автентифікація (AEAD / HMAC):**
   Виконується перевірка автентичності та розшифрування тіла повідомлення. Якщо підпис недійсний або пакет пошкоджено, він скидається, а стан бітмапа лишається абсолютно незайманим.

3. **Фіксація (Commit / Update):**
   Лише після успішної верифікації криптографії викликається функція оновлення, яка зсуває `max_seq` або виставляє біт у масці.

## Багатопотокова синхронізація та робота без блокувань

У багатоядерних мережевих стеках (eBPF XDP, DPDK, VPP) пакети з одного каналу можуть опрацьовуватися паралельно на різних ядрах процесора через механізм масштабування черг (RSS, від англ. *Receive Side Scaling*).

Використання класичних м'ютексів для синхронізації бітмапа призводить до високої деградації пропускної здатності через між'ядерні блокування шини кеш-пам'яті (Cache Line Bouncing). Для досягнення максимальної продуктивності застосовують дві стратегії:

* **Шардування за сесіями (Per-Session Pinning):** Кожне з'єднання (Security Association у IPsec або Connection ID у QUIC) жорстко прив'язується до конкретного процесорного ядра черги RX. У цьому випадку фільтр функціонує в однопотоковому режимі без жодних атомарних інструкцій.
* **Атомарний оптимістичний CAS (Compare-And-Swap):** Для 64-бітного вікна пара `(max_seq, bitmap)` упаковується в 128-бітну структуру, яка оновлюється за допомогою інструкції `__atomic_compare_exchange_16` (CMPXCHG16B на архітектурі x86_64). Якщо кілька ядер одночасно намагаються зафіксувати різні пакети, одне ядро успішно фіксує зміну, а решта повторюють обчислення бітової маски поверх нового стану.
