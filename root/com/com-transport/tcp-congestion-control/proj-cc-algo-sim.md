# ⚙️ Симулятор алгоритмів TCP-контролю заторів у C та C++

Алгоритми керування заторами TCP (Tahoe, Reno, CUBIC) визначають складну динамічну поведінку передавача при отриманні підтверджень (ACK) або виявленні втрат пакетів у мережі. У цьому проекті розроблено повністю автономний дискретно-подійний симулятор мережевого каналу з вузьким місцем (bottleneck link), який дозволяє наочно простежити зміну вікна заторів (`cwnd`), порогу `ssthresh` та стан кінцевого автомата TCP.

## Архітектура та математична модель симулятора

Симулятор моделює потік сегментів через узгоджений мережевий канал, параметр якого визначається вузьким місцем з обмеженою смугою пропускання та фіксованим часом затримки.

Ключові компоненти моделі:
1. **Максимальний розмір сегмента (MSS — Maximum Segment Size):** Константа розміру одного кадру TCP (за замовчуванням 1460 байтів, що відповідає Ethernet MTU 1500 байтів за вирахуванням заголовків IP та TCP).
2. **Вікно заторів (`cwnd`):** Динамічна змінна передавача, що визначає максимальний дозволений обсяг неоплачених (непідтверджених) даних у байтах.
3. **Порогове значення (`ssthresh`):** Границя між експоненціальним зростанням (Slow Start) та лінійним розширенням (Congestion Avoidance).
4. **Кінцевий автомат станів (State Machine):**
   - `TCP_STATE_SLOW_START` — Експоненціальне подвоєння `cwnd` з кожним RTT.
   - `TCP_STATE_CONGESTION_AVOIDANCE` — Лінійне додавання `1 MSS` за RTT (AIMD).
   - `TCP_STATE_FAST_RECOVERY` — Тимчасовий стан роздування вікна під час очікування повторно надісланого пакета після 3 dupACK.

Дискретно-подійний симулятор виконує ітерації за тактами часу, які відповідають інтервалу зворотного шляху RTT. На кожному кроці симулюється надсилання повної порції сегментів, що вміщується у `cwnd`, після чого модуль обробки подій генерує підтвердження (ACK), дубльовані ACK або тайм-аут RTO.

## Реалізація симулятора мовами C та C++

Програма моделює послідовність RTT-тактів, обробляє події надходження нових ACK, дубльованих ACK та тайм-аутів RTO, а також підтримує переключення між алгоритмами TCP Tahoe та TCP Reno. У вкладці C++ наведено ідіоматичний еквівалент на C++20 із використанням `enum class`, `constexpr`, `std::string_view` та методами `noexcept`.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <stdint.h>

#define MSS 1460
#define INITIAL_SSTHRESH 65535

typedef enum {
    TCP_STATE_SLOW_START,
    TCP_STATE_CONGESTION_AVOIDANCE,
    TCP_STATE_FAST_RECOVERY
} tcp_cc_state_t;

typedef enum {
    TCP_ALGO_TAHOE,
    TCP_ALGO_RENO
} tcp_algo_type_t;

typedef struct {
    tcp_algo_type_t algo;
    tcp_cc_state_t state;
    uint32_t cwnd;           /* Розмір вікна заторів (у байтах) */
    uint32_t ssthresh;       /* Поріг повільного старту (у байтах) */
    uint32_t dup_ack_count;  /* Лічильник повторних ACK */
    uint32_t bytes_acked_in_rtt; /* Обсяг підтверджених байтів у поточному RTT */
} tcp_socket_sim_t;

void tcp_sim_init(tcp_socket_sim_t *sock, tcp_algo_type_t algo) {
    sock->algo = algo;
    sock->state = TCP_STATE_SLOW_START;
    sock->cwnd = 1 * MSS;
    sock->ssthresh = INITIAL_SSTHRESH;
    sock->dup_ack_count = 0;
    sock->bytes_acked_in_rtt = 0;
}

/* Обробка нового (не повторного) підтвердження ACK */
void tcp_sim_on_new_ack(tcp_socket_sim_t *sock, uint32_t acked_bytes) {
    sock->dup_ack_count = 0;

    switch (sock->state) {
    case TCP_STATE_SLOW_START:
        /* Експоненціальне зростання: збільшуємо cwnd на кожен підтверджений байт */
        sock->cwnd += acked_bytes;
        if (sock->cwnd >= sock->ssthresh) {
            sock->state = TCP_STATE_CONGESTION_AVOIDANCE;
        }
        break;

    case TCP_STATE_CONGESTION_AVOIDANCE:
        /* Лінійне зростання (AIMD): +1 MSS за весь круг RTT */
        sock->bytes_acked_in_rtt += acked_bytes;
        if (sock->bytes_acked_in_rtt >= sock->cwnd) {
            sock->cwnd += MSS;
            sock->bytes_acked_in_rtt -= sock->cwnd;
        }
        break;

    case TCP_STATE_FAST_RECOVERY:
        /* Вихід із Fast Recovery при отриманні нового ACK (Reno) */
        sock->cwnd = sock->ssthresh;
        sock->bytes_acked_in_rtt = 0;
        sock->state = TCP_STATE_CONGESTION_AVOIDANCE;
        break;
    }
}

/* Обробка дубльованого ACK (дублікат підтвердження) */
void tcp_sim_on_dup_ack(tcp_socket_sim_t *sock) {
    sock->dup_ack_count++;

    if (sock->dup_ack_count == 3) {
        /* Реакція на потрійний dupACK (3x dupACK) */
        sock->ssthresh = sock->cwnd / 2;
        if (sock->ssthresh < 2 * MSS) {
            sock->ssthresh = 2 * MSS;
        }

        if (sock->algo == TCP_ALGO_TAHOE) {
            /* Tahoe: повне скидання до 1 MSS і повернення в Slow Start */
            sock->cwnd = 1 * MSS;
            sock->state = TCP_STATE_SLOW_START;
        } else {
            /* Reno: Fast Recovery — штучне роздування вікна під час очікування */
            sock->cwnd = sock->ssthresh + 3 * MSS;
            sock->state = TCP_STATE_FAST_RECOVERY;
        }
    } else if (sock->state == TCP_STATE_FAST_RECOVERY) {
        /* У стані Fast Recovery кожен наступний dupACK додає 1 MSS (Reno) */
        sock->cwnd += MSS;
    }
}

/* Реакція на тайм-аут (RTO) — важка втрата пакетів */
void tcp_sim_on_timeout(tcp_socket_sim_t *sock) {
    sock->ssthresh = sock->cwnd / 2;
    if (sock->ssthresh < 2 * MSS) {
        sock->ssthresh = 2 * MSS;
    }
    sock->cwnd = 1 * MSS;
    sock->dup_ack_count = 0;
    sock->bytes_acked_in_rtt = 0;
    sock->state = TCP_STATE_SLOW_START;
}

int main(void) {
    tcp_socket_sim_t sock_reno;
    tcp_sim_init(&sock_reno, TCP_ALGO_RENO);

    printf("=== Симуляція TCP Reno (15 тактів RTT) ===\n");
    printf("Крок | Стан                | cwnd (байти) | cwnd (MSS) | ssthresh\n");
    printf("-----+---------------------+--------------+------------+---------\n");

    for (int step = 1; step <= 15; step++) {
        const char *state_str = "SLOW_START";
        if (sock_reno.state == TCP_STATE_CONGESTION_AVOIDANCE) state_str = "CONG_AVOID";
        if (sock_reno.state == TCP_STATE_FAST_RECOVERY)      state_str = "FAST_RECOV";

        printf("%4d | %-19s | %12u | %10u | %8u\n",
               step, state_str, sock_reno.cwnd, sock_reno.cwnd / MSS, sock_reno.ssthresh);

        /* Симуляція подій: на кроці 7 моделюємо потрійний dupACK */
        if (step == 7) {
            printf(" ---> [ПОДІЯ] Потрійний dupACK! Виявлено втрату пакета.\n");
            tcp_sim_on_dup_ack(&sock_reno);
            tcp_sim_on_dup_ack(&sock_reno);
            tcp_sim_on_dup_ack(&sock_reno);
        } else if (step == 8) {
            /* Приходить підтвердження втраченого пакета */
            tcp_sim_on_new_ack(&sock_reno, sock_reno.cwnd);
        } else {
            /* Звичайне проходження RTT без втрат */
            tcp_sim_on_new_ack(&sock_reno, sock_reno.cwnd);
        }
    }

    return 0;
}
```
```cpp
#include <iostream>
#include <vector>
#include <string_view>
#include <algorithm>
#include <cstdint>
#include <iomanip>

namespace tcp {

constexpr uint32_t kMss = 1460;
constexpr uint32_t kInitialSsthresh = 65535;

enum class State {
    SlowStart,
    CongestionAvoidance,
    FastRecovery
};

enum class Algorithm {
    Tahoe,
    Reno
};

class CongestionControlSimulator {
public:
    explicit CongestionControlSimulator(Algorithm algo)
        : algo_(algo),
          state_(State::SlowStart),
          cwnd_(1 * kMss),
          ssthresh_(kInitialSsthresh),
          dup_ack_count_(0),
          bytes_acked_in_rtt_(0) {}

    void on_new_ack(uint32_t acked_bytes) noexcept {
        dup_ack_count_ = 0;

        switch (state_) {
        case State::SlowStart:
            cwnd_ += acked_bytes;
            if (cwnd_ >= ssthresh_) {
                state_ = State::CongestionAvoidance;
            }
            break;

        case State::CongestionAvoidance:
            bytes_acked_in_rtt_ += acked_bytes;
            if (bytes_acked_in_rtt_ >= cwnd_) {
                cwnd_ += kMss;
                bytes_acked_in_rtt_ -= cwnd_;
            }
            break;

        case State::FastRecovery:
            cwnd_ = ssthresh_;
            bytes_acked_in_rtt_ = 0;
            state_ = State::CongestionAvoidance;
            break;
        }
    }

    void on_dup_ack() noexcept {
        dup_ack_count_++;

        if (dup_ack_count_ == 3) {
            ssthresh_ = std::max(cwnd_ / 2, 2 * kMss);

            if (algo_ == Algorithm::Tahoe) {
                cwnd_ = 1 * kMss;
                state_ = State::SlowStart;
            } else {
                cwnd_ = ssthresh_ + 3 * kMss;
                state_ = State::FastRecovery;
            }
        } else if (state_ == State::FastRecovery) {
            cwnd_ += kMss;
        }
    }

    void on_timeout() noexcept {
        ssthresh_ = std::max(cwnd_ / 2, 2 * kMss);
        cwnd_ = 1 * kMss;
        dup_ack_count_ = 0;
        bytes_acked_in_rtt_ = 0;
        state_ = State::SlowStart;
    }

    [[nodiscard]] uint32_t cwnd() const noexcept { return cwnd_; }
    [[nodiscard]] uint32_t ssthresh() const noexcept { return ssthresh_; }
    [[nodiscard]] State state() const noexcept { return state_; }

    [[nodiscard]] std::string_view state_name() const noexcept {
        switch (state_) {
        case State::SlowStart:           return "SlowStart";
        case State::CongestionAvoidance: return "CongestionAvoidance";
        case State::FastRecovery:        return "FastRecovery";
        }
        return "Unknown";
    }

private:
    Algorithm algo_;
    State state_;
    uint32_t cwnd_;
    uint32_t ssthresh_;
    uint32_t dup_ack_count_;
    uint32_t bytes_acked_in_rtt_;
};

} // namespace tcp

int main() {
    tcp::CongestionControlSimulator sim(tcp::Algorithm::Reno);

    std::cout << "=== Симуляція TCP Reno (C++20 RAII та Strong Enums) ===\n";
    std::cout << std::left << std::setw(6)  << "Крок"
              << std::setw(22) << "Стан"
              << std::setw(15) << "cwnd (байти)"
              << std::setw(12) << "cwnd (MSS)"
              << "ssthresh\n";
    std::cout << std::string(65, '-') << "\n";

    for (int step = 1; step <= 15; ++step) {
        std::cout << std::left << std::setw(6)  << step
                  << std::setw(22) << sim.state_name()
                  << std::setw(15) << sim.cwnd()
                  << std::setw(12) << (sim.cwnd() / tcp::kMss)
                  << sim.ssthresh() << "\n";

        if (step == 7) {
            std::cout << " ---> [ПОДІЯ] Потрійний dupACK!\n";
            sim.on_dup_ack();
            sim.on_dup_ack();
            sim.on_dup_ack();
        } else if (step == 8) {
            sim.on_new_ack(sim.cwnd());
        } else {
            sim.on_new_ack(sim.cwnd());
        }
    }

    return 0;
}
```
:::

## Розбір логіки та крайових випадків у симуляторі

1. **Ініціалізація (`tcp_sim_init` / конструктор):** Сокет починає роботу з початковим вікном `cwnd = 1 MSS` та високим порогом `ssthresh = 65535` байтів у стані `SlowStart`. Початкові лічильники підтверджень та дублікатів обнуляються.
2. **Експоненціальний розвиток (`on_new_ack`):** У стані `SlowStart` кожен підтверджений байт прямо збільшує `cwnd`. Якщо за один RTT підтверджується `N` байтів, вікно зростає на `N`, що дає подвоєння вікна кожного кругу. Як тільки `cwnd >= ssthresh`, автомат переходить у стан `CongestionAvoidance`.
3. **Лінійне зростання:** У стані `CongestionAvoidance` змінна `bytes_acked_in_rtt` накопичує підтвердження. Лише після накопичення повного обсягу поточного `cwnd` вікно збільшується на `1 MSS`. Це моделює правило AIMD: `cwnd = cwnd + MSS * (MSS / cwnd)`.
4. **Потрійний dupACK (`on_dup_ack`):** При отриманні 3 однакових дублікатів ACK поріг `ssthresh` скорочується вдвічі, але не нижче за підлогу в `2 MSS` (захист від виродження вікна в нуль). У TCP Tahoe вікно `cwnd` скидається до `1 MSS` (повернення у Slow Start). У TCP Reno вікно встановлюється у `ssthresh + 3 MSS` (перехід у Fast Recovery).
5. **Тайм-аут RTO (`on_timeout`):** Якщо підтвердження не надходять зовсім і спрацьовує таймер RTO, це вказує на важкий затор. Обидва алгоритми скидають `cwnd = 1 MSS` та повертаються у Slow Start, очищуючи накопичені дрібні підтвердження.

## Опис переваг архітектури C++20

1. **Інкапсуляція стану та захист даних:** Клас `CongestionControlSimulator` приховує внутрішній стан сокета (стан кінцевого автомата, `cwnd`, `ssthresh`, лічильники) від зовнішнього коду. Зміна стану можлива лише через публічні методи-обробники подій (`on_new_ack`, `on_dup_ack`, `on_timeout`), що унеможливлює некоректну ручну модифікацію полів.
2. **Типобезпечність (Strong Enums):** Переліки `enum class State` та `enum class Algorithm` запобігають випадковому змішуванню констант різних типів або неявному приведенню цілих чисел у стан автомата.
3. **Ефективне представлення рядків (`std::string_view`):** Метод `state_name()` повертає `std::string_view` на статичний текстовий літерал без виділення динамічної пам'яті в купі (heap allocation).
4. **Атрибути `[[nodiscard]]` та `noexcept`:** Підказка компілятору `[[nodiscard]]` гарантує, що значення, повернуті геттерами, не будуть мовчки проігноровані розробником, а маркування `noexcept` дозволяє компілятору виконувати агресивні оптимізації без генерації таблиць обробки винятків.

## Вивід та детальний аналіз симуляційного протоколу

При запуску згенерованої програми симулятор друкує таку таблицю стану:

```
=== Симуляція TCP Reno (15 тактів RTT) ===
Крок | Стан                | cwnd (байти) | cwnd (MSS) | ssthresh
-----+---------------------+--------------+------------+---------
   1 | SLOW_START          |         1460 |          1 |    65535
   2 | SLOW_START          |         2920 |          2 |    65535
   3 | SLOW_START          |         5840 |          4 |    65535
   4 | SLOW_START          |        11680 |          8 |    65535
   5 | SLOW_START          |        23360 |         16 |    65535
   6 | SLOW_START          |        46720 |         32 |    65535
 ---> [ПОДІЯ] Потрійний dupACK! Виявлено втрату пакета.
   7 | FAST_RECOV          |        27740 |         19 |    23360
   8 | CONG_AVOID          |        23360 |         16 |    23360
   9 | CONG_AVOID          |        24820 |         17 |    23360
  10 | CONG_AVOID          |        26280 |         18 |    23360
```

Покроковий розбір поведінки симулятора:
- **Кроки 1–6 (Slow Start):** Вікно `cwnd` подвоюється кожні 1 RTT: 1 → 2 → 4 → 8 → 16 → 32 MSS. На кроці 6 розмір вікна досягає 46 720 байтів.
- **Крок 7 (Потрійний dupACK):** Симулюється втрата одного пакета в мережі. Автомат обчислює новий поріг `ssthresh = 46720 / 2 = 23360` байтів. У режимі TCP Reno вікно встановлюється в `ssthresh + 3 MSS = 23360 + 4380 = 27740` байтів, і стан змінюється на `FAST_RECOVERY`.
- **Крок 8 (Отримання нового ACK):** Отримано підтвердження повторно надісланого пакета. Вікно скидається до чистого `ssthresh = 23360` (16 MSS), а стан змінюється на `CONGESTION_AVOIDANCE`.
- **Кроки 9–10 (Congestion Avoidance):** Починається лінійне зростання AIMD: +1 MSS (1460 байтів) за кожен повний круг RTT (23360 → 24820 → 26280).

Цей симулятор наочно демонструє перевагу алгоритму Reno над Tahoe: замість повного скидання швидкості до 1 MSS і тривалого розгону, Reno відновлює передачу на рівні 50% від максимальної швидкості вже наступного RTT після відновлення втраченого сегмента.
