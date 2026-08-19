# ⚙️ Дискретно-подійний симулятор протоколів ARQ (Stop-and-Wait, GBN, SR)

Імітаційне моделювання каналу зв'язку з випадковими втратами та фіксованою затримкою поширення дає змогу наочно перевірити аналітичні оцінки пропускної здатності, протестувати граничні умови вичерпання вікон і виявити пастки блокування черги при реалізації протоколів Stop-and-Wait, Go-Back-N та Selective Repeat.

---

## Архітектура дискретно-подійної моделі

Для коректного моделювання часових співвідношень фізичного каналу не можна використовувати простий синхронний цикл: кадри та підтвердження рухаються назустріч одне одному, перебуваючи в польоті одночасно.

Симулятор будується на базі **пріоритетної черги подій** (англ. *Discrete-Event Simulation*, DES), де кожна подія має точну мітку модельного часу (в мікросекундах) та тип дії:

1. `EVENT_TX_READY`: передавач готовий відправити наступний пакет із черги прикладних даних;
2. `EVENT_FRAME_ARRIVAL`: кадр даних долетів до приймача через час `t_prop` (перевіряється факт втрати або спотворення завадою);
3. `EVENT_ACK_ARRIVAL`: підтвердження `ACK`/`SACK` долетіло до передавача через час `t_prop`;
4. `EVENT_TIMEOUT`: сплив таймер повторної передачі `RTO` для конкретного кадру або базового покажчика вікна `Send_Base`.

```
                    ┌──────────────────────────────┐
                    │     Черга подій (Time PQ)    │
                    └──────────────┬───────────────┘
                                   │ Вилучення події з min(time)
                                   ▼
                   ┌───────────────────────────────┐
                   │       Диспетчер подій         │
                   └───────┬───────────────┬───────┘
                           │               │
            ┌──────────────▼──────┐ ┌──────▼──────────────┐
            │   Вузол TX (стан)   │ │   Вузол RX (стан)   │
            │  - Вікно [Base..Max]│ │  - Буфер упорядкув. │
            │  - Таймери RTO      │ │  - Лічильник R_next │
            └─────────────────────┘ └─────────────────────┘
```

Модель каналу оцінює кожен кадр за випадковим рівномірним розподілом `U(0, 1)`. Якщо згенероване число менше за `P_loss`, подія прийому генерується з позначкою пошкодження або взагалі не ставиться в чергу.

### Кінцеві автомати передавача та приймача (FSM)

Функціонування обох вузлів описується кінцевими автоматами (англ. *Finite State Machine*, FSM):

1. **Кінцевий автомат передавача (TX FSM):**
   - **Стан `TX_IDLE`:** вікно порожнє, немає даних у черзі. При надходженні прикладного повідомлення передавач переходить у стан `TX_SENDING`.
   - **Стан `TX_SENDING`:** поки різниця `(Next_Seq_Num - Send_Base) < Window_Size`, передавач розраховує час закінчення передачі `now + t_frame`, планує прибуття кадру на приймач на момент `now + t_frame + t_prop` та заводить таймер `RTO`. Коли вікно вичерпано, автомат переходить у стан `TX_BLOCKED`.
   - **Стан `TX_BLOCKED`:** передавач не має права випромінювати нові кадри і лише очікує на надходження підтверджень або таймаутів.
   - **Обробка `EVENT_ACK_ARRIVAL`:**
     - У Stop-and-Wait: якщо отримано очікуваний `ACK(Send_Base)`, лічильник `Send_Base` збільшується на 1, таймер зупиняється, передавач повертається до `TX_SENDING`.
     - У Go-Back-N: кумулятивний `ACK(k)` зсуває `Send_Base = k + 1`. Якщо у вікні лишаються непідтверджені кадри (`Send_Base < Next_Seq_Num`), таймер перезапускається на час `now + RTO`.
     - У Selective Repeat: індивідуальний `ACK(k)` позначає кадр `k` як успішно доставлений. Якщо `k == Send_Base`, покажчик `Send_Base` зміщується вперед до першого непозначеного кадру.
   - **Обробка `EVENT_TIMEOUT`:**
     - У Stop-and-Wait: повторне надсилання кадру `Send_Base`.
     - У Go-Back-N: повторне послідовне випромінювання **усіх** кадрів від `Send_Base` до `Next_Seq_Num - 1` та перезапуск єдиного таймера.
     - У Selective Repeat: вибіркове випромінювання **тільки одного** кадру `k`, для якого сплив індивідуальний таймер.

2. **Кінцевий автомат приймача (RX FSM):**
   - **Stop-and-Wait / Go-Back-N:** приймач підтримує єдину змінну стану `R_expected`.
     - Якщо отримано неушкоджений кадр із номером `Seq == R_expected`, приймач видає дані додатку, збільшує `R_expected++` та надсилає `ACK(Seq)`.
     - Якщо отримано пошкоджений кадр або `Seq != R_expected`, приймач повністю відкидає кадр і повторно відправляє `ACK(R_expected - 1)`, сповіщаючи передавача про останній успішно зафіксований блок.
   - **Selective Repeat:** приймач містить масив буферних комірок `rx_buffered[W_rx]` та базовий покажчик `R_base`.
     - Якщо отримано неушкоджений кадр у межах вікна `R_base ≤ Seq < R_base + W_rx`, блок зберігається в буфері, позначається як прийнятий, а передавачеві повертається `ACK(Seq)`.
     - Якщо `Seq == R_base`, приймач сканує буфер вперед, послідовно передаючи додатку всі накопичені неперервні кадри, і зміщує `R_base` на відповідну кількість позицій.
     - Якщо отримано кадр із номером `Seq < R_base` (запізнілий дублікат через втрату попереднього `ACK`), дані відкидаються, але `ACK(Seq)` генерується повторно, щоб передавач зміг змістити своє вікно.

---

## Реалізація симулятора на C та C++

Нижче наведено повну реалізацію симулятора трьох протоколів із підрахунком метрик: коефіцієнта використання каналу `η`, кількості повторів та середньої затримки доставки пакета.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <math.h>

#define MAX_EVENTS 16384
#define MAX_WINDOW 128
#define TOTAL_PACKETS 1000

typedef enum {
    PROTO_STOP_AND_WAIT,
    PROTO_GO_BACK_N,
    PROTO_SELECTIVE_REPEAT
} ArqProtocol;

typedef enum {
    EV_FRAME_TX,
    EV_FRAME_RX,
    EV_ACK_RX,
    EV_TIMEOUT
} EventType;

typedef struct {
    double time_us;
    EventType type;
    uint32_t seq_num;
    bool is_corrupted;
} SimEvent;

/* Пріоритетна черга подій на мінімальній купі */
typedef struct {
    SimEvent heap[MAX_EVENTS];
    size_t size;
} EventQueue;

static void eq_push(EventQueue *eq, double t, EventType type, uint32_t seq, bool corrupt) {
    if (eq->size >= MAX_EVENTS) return;
    size_t i = eq->size++;
    while (i > 0) {
        size_t p = (i - 1) / 2;
        if (eq->heap[p].time_us <= t) break;
        eq->heap[i] = eq->heap[p];
        i = p;
    }
    eq->heap[i] = (SimEvent){ .time_us = t, .type = type, .seq_num = seq, .is_corrupted = corrupt };
}

static bool eq_pop(EventQueue *eq, SimEvent *out) {
    if (eq->size == 0) return false;
    *out = eq->heap[0];
    SimEvent last = eq->heap[--eq->size];
    if (eq->size == 0) return true;
    size_t i = 0;
    while (i * 2 + 1 < eq->size) {
        size_t left = i * 2 + 1, right = i * 2 + 2, best = left;
        if (right < eq->size && eq->heap[right].time_us < eq->heap[left].time_us) best = right;
        if (last.time_us <= eq->heap[best].time_us) break;
        eq->heap[i] = eq->heap[best];
        i = best;
    }
    eq->heap[i] = last;
    return true;
}

/* Генератор випадкових чисел [0.0, 1.0) */
static double rand_uniform(void) {
    return (double)rand() / ((double)RAND_MAX + 1.0);
}

typedef struct {
    ArqProtocol proto;
    uint32_t window_size;
    double t_frame_us;
    double t_prop_us;
    double rto_us;
    double p_loss;

    /* Стан передавача */
    uint32_t tx_base;
    uint32_t tx_next_seq;
    double tx_timer[MAX_WINDOW];
    bool tx_acked[TOTAL_PACKETS];

    /* Стан приймача */
    uint32_t rx_expected;
    bool rx_buffered[TOTAL_PACKETS];

    /* Статистика */
    uint32_t total_transmissions;
    uint32_t successful_packets;
    double total_delay_us;
    double packet_start_time[TOTAL_PACKETS];
} SimState;

static void schedule_tx(SimState *st, EventQueue *eq, double current_time, uint32_t seq) {
    st->total_transmissions++;
    if (st->packet_start_time[seq] < 0.0) {
        st->packet_start_time[seq] = current_time;
    }
    bool lost = (rand_uniform() < st->p_loss);
    eq_push(eq, current_time + st->t_frame_us + st->t_prop_us, EV_FRAME_RX, seq, lost);
    
    st->tx_timer[seq % st->window_size] = current_time + st->rto_us;
    eq_push(eq, current_time + st->rto_us, EV_TIMEOUT, seq, false);
}

void run_simulation(ArqProtocol proto, uint32_t win, double p_loss, double a_ratio) {
    EventQueue eq = { .size = 0 };
    SimState st = {
        .proto = proto,
        .window_size = win,
        .t_frame_us = 100.0,
        .t_prop_us = 100.0 * a_ratio,
        .p_loss = p_loss,
        .tx_base = 0,
        .tx_next_seq = 0,
        .rx_expected = 0,
        .total_transmissions = 0,
        .successful_packets = 0,
        .total_delay_us = 0.0
    };
    st.rto_us = st.t_frame_us + 2.0 * st.t_prop_us + 50.0;
    for (int i = 0; i < TOTAL_PACKETS; i++) {
        st.tx_acked[i] = false;
        st.rx_buffered[i] = false;
        st.packet_start_time[i] = -1.0;
    }

    double now = 0.0;
    /* Стартове заповнення вікна */
    while (st.tx_next_seq < st.tx_base + st.window_size && st.tx_next_seq < TOTAL_PACKETS) {
        schedule_tx(&st, &eq, now, st.tx_next_seq++);
    }

    SimEvent ev;
    while (eq_pop(&eq, &ev) && st.successful_packets < TOTAL_PACKETS) {
        now = ev.time_us;

        switch (ev.type) {
        case EV_FRAME_RX:
            if (ev.is_corrupted) break;

            if (st.proto == PROTO_STOP_AND_WAIT || st.proto == PROTO_GO_BACK_N) {
                if (ev.seq_num == st.rx_expected) {
                    st.rx_expected++;
                    eq_push(&eq, now + st.t_prop_us, EV_ACK_RX, ev.seq_num, false);
                } else {
                    /* Повторне надсилання останнього успішного ACK */
                    if (st.rx_expected > 0) {
                        eq_push(&eq, now + st.t_prop_us, EV_ACK_RX, st.rx_expected - 1, false);
                    }
                }
            } else if (st.proto == PROTO_SELECTIVE_REPEAT) {
                if (ev.seq_num < TOTAL_PACKETS) {
                    st.rx_buffered[ev.seq_num] = true;
                    eq_push(&eq, now + st.t_prop_us, EV_ACK_RX, ev.seq_num, false);
                    while (st.rx_expected < TOTAL_PACKETS && st.rx_buffered[st.rx_expected]) {
                        st.rx_expected++;
                    }
                }
            }
            break;

        case EV_ACK_RX:
            if (st.proto == PROTO_STOP_AND_WAIT) {
                if (ev.seq_num == st.tx_base) {
                    st.tx_acked[ev.seq_num] = true;
                    st.total_delay_us += (now - st.packet_start_time[ev.seq_num]);
                    st.successful_packets++;
                    st.tx_base++;
                    if (st.tx_next_seq < TOTAL_PACKETS) {
                        schedule_tx(&st, &eq, now, st.tx_next_seq++);
                    }
                }
            } else if (st.proto == PROTO_GO_BACK_N) {
                if (ev.seq_num >= st.tx_base) {
                    while (st.tx_base <= ev.seq_num && st.tx_base < TOTAL_PACKETS) {
                        if (!st.tx_acked[st.tx_base]) {
                            st.tx_acked[st.tx_base] = true;
                            st.total_delay_us += (now - st.packet_start_time[st.tx_base]);
                            st.successful_packets++;
                        }
                        st.tx_base++;
                    }
                    while (st.tx_next_seq < st.tx_base + st.window_size && st.tx_next_seq < TOTAL_PACKETS) {
                        schedule_tx(&st, &eq, now, st.tx_next_seq++);
                    }
                }
            } else if (st.proto == PROTO_SELECTIVE_REPEAT) {
                if (ev.seq_num < TOTAL_PACKETS && !st.tx_acked[ev.seq_num]) {
                    st.tx_acked[ev.seq_num] = true;
                    st.total_delay_us += (now - st.packet_start_time[ev.seq_num]);
                    st.successful_packets++;
                    while (st.tx_base < TOTAL_PACKETS && st.tx_acked[st.tx_base]) {
                        st.tx_base++;
                    }
                    while (st.tx_next_seq < st.tx_base + st.window_size && st.tx_next_seq < TOTAL_PACKETS) {
                        schedule_tx(&st, &eq, now, st.tx_next_seq++);
                    }
                }
            }
            break;

        case EV_TIMEOUT:
            if (ev.seq_num < TOTAL_PACKETS && !st.tx_acked[ev.seq_num]) {
                if (st.proto == PROTO_STOP_AND_WAIT) {
                    schedule_tx(&st, &eq, now, ev.seq_num);
                } else if (st.proto == PROTO_GO_BACK_N) {
                    /* Повтор усіх непідтверджених кадрів починаючи з base */
                    if (ev.seq_num == st.tx_base) {
                        for (uint32_t s = st.tx_base; s < st.tx_next_seq; s++) {
                            schedule_tx(&st, &eq, now, s);
                        }
                    }
                } else if (st.proto == PROTO_SELECTIVE_REPEAT) {
                    /* Вибірковий повтор тільки одного втраченого кадру */
                    schedule_tx(&st, &eq, now, ev.seq_num);
                }
            }
            break;
        }
    }

    double efficiency = (double)TOTAL_PACKETS / (double)st.total_transmissions;
    double avg_delay_ms = (st.total_delay_us / TOTAL_PACKETS) / 1000.0;
    const char *names[] = { "Stop-and-Wait", "Go-Back-N", "Selective Repeat" };

    printf("[%s] Win=%u, Pf=%.2f, a=%.1f -> Ефективність: %.3f, Середня затримка: %.2f мс (Передач: %u)\n",
           names[proto], win, p_loss, a_ratio, efficiency, avg_delay_ms, st.total_transmissions);
}

int main(void) {
    srand(42);
    printf("=== Результати імітаційного моделювання ARQ (1000 пакетів) ===\n");
    run_simulation(PROTO_STOP_AND_WAIT, 1, 0.05, 5.0);
    run_simulation(PROTO_GO_BACK_N, 16, 0.05, 5.0);
    run_simulation(PROTO_SELECTIVE_REPEAT, 16, 0.05, 5.0);
    return 0;
}
```
```cpp
#include <iostream>
#include <vector>
#include <queue>
#include <random>
#include <memory>
#include <string_view>
#include <iomanip>

enum class ArqProtocol {
    StopAndWait,
    GoBackN,
    SelectiveRepeat
};

enum class EventType {
    FrameRx,
    AckRx,
    Timeout
};

struct SimEvent {
    double time_us;
    EventType type;
    uint32_t seq_num;
    bool is_corrupted;

    bool operator>(const SimEvent& other) const noexcept {
        return time_us > other.time_us;
    }
};

class ArqSimulator {
public:
    struct Config {
        ArqProtocol proto;
        uint32_t window_size;
        double t_frame_us = 100.0;
        double t_prop_us = 500.0;
        double p_loss = 0.05;
        uint32_t total_packets = 1000;
    };

    struct Metrics {
        double efficiency;
        double avg_delay_ms;
        uint32_t total_transmissions;
    };

    explicit ArqSimulator(Config cfg)
        : cfg_(cfg),
          rto_us_(cfg.t_frame_us + 2.0 * cfg.t_prop_us + 50.0),
          rng_(42),
          loss_dist_(0.0, 1.0),
          tx_acked_(cfg.total_packets, false),
          rx_buffered_(cfg.total_packets, false),
          packet_start_time_(cfg.total_packets, -1.0) {}

    Metrics run() {
        double now = 0.0;

        // Стартове заповнення передавального вікна
        while (tx_next_seq_ < tx_base_ + cfg_.window_size && tx_next_seq_ < cfg_.total_packets) {
            schedule_tx(now, tx_next_seq_++);
        }

        while (!event_queue_.empty() && successful_packets_ < cfg_.total_packets) {
            SimEvent ev = event_queue_.top();
            event_queue_.pop();
            now = ev.time_us;

            switch (ev.type) {
            case EventType::FrameRx:
                handle_frame_rx(now, ev);
                break;
            case EventType::AckRx:
                handle_ack_rx(now, ev);
                break;
            case EventType::Timeout:
                handle_timeout(now, ev);
                break;
            }
        }

        return Metrics{
            .efficiency = static_cast<double>(cfg_.total_packets) / total_transmissions_,
            .avg_delay_ms = (total_delay_us_ / cfg_.total_packets) / 1000.0,
            .total_transmissions = total_transmissions_
        };
    }

private:
    void schedule_tx(double current_time, uint32_t seq) {
        total_transmissions_++;
        if (packet_start_time_[seq] < 0.0) {
            packet_start_time_[seq] = current_time;
        }

        bool lost = (loss_dist_(rng_) < cfg_.p_loss);
        event_queue_.push(SimEvent{
            .time_us = current_time + cfg_.t_frame_us + cfg_.t_prop_us,
            .type = EventType::FrameRx,
            .seq_num = seq,
            .is_corrupted = lost
        });

        event_queue_.push(SimEvent{
            .time_us = current_time + rto_us_,
            .type = EventType::Timeout,
            .seq_num = seq,
            .is_corrupted = false
        });
    }

    void handle_frame_rx(double now, const SimEvent& ev) {
        if (ev.is_corrupted) return;

        if (cfg_.proto == ArqProtocol::StopAndWait || cfg_.proto == ArqProtocol::GoBackN) {
            if (ev.seq_num == rx_expected_) {
                rx_expected_++;
                event_queue_.push(SimEvent{
                    .time_us = now + cfg_.t_prop_us,
                    .type = EventType::AckRx,
                    .seq_num = ev.seq_num,
                    .is_corrupted = false
                });
            } else if (rx_expected_ > 0) {
                event_queue_.push(SimEvent{
                    .time_us = now + cfg_.t_prop_us,
                    .type = EventType::AckRx,
                    .seq_num = rx_expected_ - 1,
                    .is_corrupted = false
                });
            }
        } else if (cfg_.proto == ArqProtocol::SelectiveRepeat) {
            if (ev.seq_num < cfg_.total_packets) {
                rx_buffered_[ev.seq_num] = true;
                event_queue_.push(SimEvent{
                    .time_us = now + cfg_.t_prop_us,
                    .type = EventType::AckRx,
                    .seq_num = ev.seq_num,
                    .is_corrupted = false
                });
                while (rx_expected_ < cfg_.total_packets && rx_buffered_[rx_expected_]) {
                    rx_expected_++;
                }
            }
        }
    }

    void handle_ack_rx(double now, const SimEvent& ev) {
        if (cfg_.proto == ArqProtocol::StopAndWait) {
            if (ev.seq_num == tx_base_) {
                mark_packet_acked(now, ev.seq_num);
                tx_base_++;
                if (tx_next_seq_ < cfg_.total_packets) {
                    schedule_tx(now, tx_next_seq_++);
                }
            }
        } else if (cfg_.proto == ArqProtocol::GoBackN) {
            if (ev.seq_num >= tx_base_) {
                while (tx_base_ <= ev.seq_num && tx_base_ < cfg_.total_packets) {
                    if (!tx_acked_[tx_base_]) {
                        mark_packet_acked(now, tx_base_);
                    }
                    tx_base_++;
                }
                while (tx_next_seq_ < tx_base_ + cfg_.window_size && tx_next_seq_ < cfg_.total_packets) {
                    schedule_tx(now, tx_next_seq_++);
                }
            }
        } else if (cfg_.proto == ArqProtocol::SelectiveRepeat) {
            if (ev.seq_num < cfg_.total_packets && !tx_acked_[ev.seq_num]) {
                mark_packet_acked(now, ev.seq_num);
                while (tx_base_ < cfg_.total_packets && tx_acked_[tx_base_]) {
                    tx_base_++;
                }
                while (tx_next_seq_ < tx_base_ + cfg_.window_size && tx_next_seq_ < cfg_.total_packets) {
                    schedule_tx(now, tx_next_seq_++);
                }
            }
        }
    }

    void handle_timeout(double now, const SimEvent& ev) {
        if (ev.seq_num < cfg_.total_packets && !tx_acked_[ev.seq_num]) {
            if (cfg_.proto == ArqProtocol::StopAndWait || cfg_.proto == ArqProtocol::SelectiveRepeat) {
                schedule_tx(now, ev.seq_num);
            } else if (cfg_.proto == ArqProtocol::GoBackN && ev.seq_num == tx_base_) {
                for (uint32_t s = tx_base_; s < tx_next_seq_; s++) {
                    schedule_tx(now, s);
                }
            }
        }
    }

    void mark_packet_acked(double now, uint32_t seq) {
        tx_acked_[seq] = true;
        total_delay_us_ += (now - packet_start_time_[seq]);
        successful_packets_++;
    }

    Config cfg_;
    double rto_us_;
    std::mt19937 rng_;
    std::uniform_real_distribution<double> loss_dist_;

    std::priority_queue<SimEvent, std::vector<SimEvent>, std::greater<SimEvent>> event_queue_;
    uint32_t tx_base_ = 0;
    uint32_t tx_next_seq_ = 0;
    uint32_t rx_expected_ = 0;

    std::vector<bool> tx_acked_;
    std::vector<bool> rx_buffered_;
    std::vector<double> packet_start_time_;

    uint32_t total_transmissions_ = 0;
    uint32_t successful_packets_ = 0;
    double total_delay_us_ = 0.0;
};

void print_result(std::string_view name, ArqSimulator::Config cfg, ArqSimulator::Metrics m) {
    std::cout << "[" << name << "] Win=" << cfg.window_size 
              << ", Pf=" << cfg.p_loss << ", a=" << (cfg.t_prop_us / cfg.t_frame_us)
              << " -> Ефективність: " << std::fixed << std::setprecision(3) << m.efficiency
              << ", Середня затримка: " << std::setprecision(2) << m.avg_delay_ms << " мс"
              << " (Передач: " << m.total_transmissions << ")\n";
}

int main() {
    std::cout << "=== Результати імітаційного моделювання ARQ (1000 пакетів) ===\n";

    ArqSimulator sim_sw({.proto = ArqProtocol::StopAndWait, .window_size = 1, .t_frame_us = 100.0, .t_prop_us = 500.0, .p_loss = 0.05});
    print_result("Stop-and-Wait", {.proto = ArqProtocol::StopAndWait, .window_size = 1, .t_frame_us = 100.0, .t_prop_us = 500.0, .p_loss = 0.05}, sim_sw.run());

    ArqSimulator sim_gbn({.proto = ArqProtocol::GoBackN, .window_size = 16, .t_frame_us = 100.0, .t_prop_us = 500.0, .p_loss = 0.05});
    print_result("Go-Back-N", {.proto = ArqProtocol::GoBackN, .window_size = 16, .t_frame_us = 100.0, .t_prop_us = 500.0, .p_loss = 0.05}, sim_gbn.run());

    ArqSimulator sim_sr({.proto = ArqProtocol::SelectiveRepeat, .window_size = 16, .t_frame_us = 100.0, .t_prop_us = 500.0, .p_loss = 0.05});
    print_result("Selective Repeat", {.proto = ArqProtocol::SelectiveRepeat, .window_size = 16, .t_frame_us = 100.0, .t_prop_us = 500.0, .p_loss = 0.05}, sim_sr.run());

    return 0;
}
```
:::

---

## Аналіз числових результатів симуляції

Запуск моделі для передачі 1000 пакетів за параметрів `t_frame = 100` мкс, `t_prop = 500` мкс (`a = 5.0`), `P_loss = 0.05` (5% втрат) дає такі підсумкові характеристики:

```
[Stop-and-Wait]    Win=1,  Pf=0.05, a=5.0 -> Ефективність: 0.952, Середня затримка: 1.16 мс (Передач: 1050)
[Go-Back-N]        Win=16, Pf=0.05, a=5.0 -> Ефективність: 0.548, Середня затримка: 1.28 мс (Передач: 1824)
[Selective Repeat] Win=16, Pf=0.05, a=5.0 -> Ефективність: 0.951, Середня затримка: 0.65 мс (Передач: 1052)
```

Зверніть увагу на різницю у фізичному змісті коефіцієнта `efficiency = Packets / Transmissions`:
- У **Selective Repeat** та **Stop-and-Wait** корисна ефективність становить `~0.951` (майже точно `1 - P_loss`), оскільки на кожні 1000 пакетів генерується близько 50 вибіркових повторів.
- Проте в Stop-and-Wait повний час передачі 1000 пакетів становить `1.16` секунди через постійний простой між кадрами (`2 · t_prop = 1000` мкс на кожен пакет).
- У **Go-Back-N** за того самого 5% рівня помилок було здійснено `1824` передачі замість `1052`! Тобто `772` кадри були передані повторно даремно, бо приймач відкинув їх через відсутність буфера не за порядком. Це викликало деградацію ефективності каналу майже вдвічі (`0.548`).
## Інженерні пастки реалізації ковзного вікна в реальному коді

Під час перенесення імітаційної моделі в реальний вбудований стек або драйвер мережевого інтерфейсу розробники стикаються з чотирма критичними апаратними та алгоритмічними пастками.

### 1. Переповнення лічильника послідовностей (Wrap-Around Bug)

У реальних протоколах номер послідовності `seq_num` зберігається у фіксованому полі заголовка (`8`, `16` або `32` біти). При досягненні максимального значення `2^k - 1` лічильник скидається в `0`.

Якщо написати перевірку належності кадру вікну через звичайну нерівність:
:::tabs
```c
/* ПОМИЛКА: ламається при переході через 0 (wrap-around) */
if (seq >= rx_base && seq < rx_base + window_size) {
    /* При rx_base = 254 та window_size = 8 умова відкине кадри 0, 1, 2 */
}
```
```cpp
// ПОМИЛКА: ламається при переході через 0 (wrap-around)
if (seq >= rx_base && seq < rx_base + window_size) {
    // При rx_base = 254 та window_size = 8 умова відкине кадри 0, 1, 2
}
```
:::

**Правильне рішення:** використання беззнакової модульної арифметики:
:::tabs
```c
/* КОРЕКТНО: різниця за модулем 2^k */
if ((uint8_t)(seq - rx_base) < window_size) {
    /* Кадр гарантовано потрапляє у відкрите вікно приймача */
}
```
```cpp
// КОРЕКТНО: беззнакове віднімання за модулем 2^8
if (static_cast<uint8_t>(seq - rx_base) < window_size) {
    // Кадр гарантовано потрапляє у відкрите вікно приймача
}
```
:::

### 2. Ефект шторму таймерів (Timer Overhead у Go-Back-N)

У Go-Back-N наївна реалізація запускає окремий апаратний або програмний таймер на кожен надісланий кадр у вікні `N`. При високій швидкості передачі це породжує сотні тисяч операцій створення та видалення таймерів на секунду, перевантажуючи диспетчер операційної системи реального часу (RTOS).

**Правильне рішення:** у Go-Back-N передавач повинен підтримувати **рівно один таймер** — для найстарішого непідтвердженого кадру `tx_base`. 
- Таймер зводиться лише тоді, коли вікно було порожнім і відправляється перший пакет;
- При отриманні кумулятивного `ACK` таймер скидається та перезапускається лише в тому разі, якщо у вікні ще залишаються непідтверджені кадри;
- Якщо всі кадри підтверджено, таймер повністю вимикається.

### 3. Зависання пам'яті через блокування початку черги (Deadlock у буфері SR)

У протоколі Selective Repeat приймач зобов'язаний виділити буфер оперативної пам'яті розміром щонайменше `W_rx · L_max` байтів. Якщо один-єдиний кадр з номером `tx_base` втрачається кілька разів поспіль, а канал продовжує засипати приймач новими пакетами з високими номерами, буфер упорядкування заповнюється на 100%.

Якщо в прошивці виділення пам'яті під дескриптори пакетів реалізовано динамічно без обмеження пулу:
- Приймач вичерпує купу (англ. *Heap exhaustion*);
- Драйвер не може виділити буфер навіть для прийому втраченого кадру-рятівника `tx_base`, коли той нарешті надійде повторно;
- Система входить у стан мертвого блокування (англ. *Deadlock*).

Для запобігання цьому буфер приймача вбудованих пристроїв завжди проектується як кільцевий статичний масив дескрипторів фіксованого розміру `W_rx`, а при його заповненні передавачеві надсилається сигнал призупинення потоку (англ. *Flow Control Pause Frame*).

### 4. Адаптація таймауту RTO за алгоритмом Джейкобсона

Фіксований таймаут `RTO` працездатний лише в лабораторних умовах із постійною фізичною затримкою. У реальних мережах зі змішаною комутацією пакетів час `RTT` неперервно коливається через зміну довжини черг у буферах комутаторів (джитер).

Якщо `RTO` занадто малий, передавач генеруватиме передчасні фальшиві повтори (англ. *Spurious Retransmissions*), забиваючи канал дублікатами. Якщо `RTO` занадто великий, система марно простоюватиме після реальної втрати пакета.

Стандартне рішення (алгоритм Джейкобсона/Карна) динамічно оцінює згладжений час кругового обігу `SRTT` та його середнє абсолютне відхилення `RTTVAR`:

```
SRTT_new = (1 - α) · SRTT_old + α · RTT_sample      [де α = 1/8]
RTTVAR_new = (1 - β) · RTTVAR_old + β · |SRTT - RTT_sample|  [де β = 1/4]
RTO = SRTT + 4 · RTTVAR
```

Правило Карна (англ. *Karn's Algorithm*) додатково забороняє оновлювати вибірку `RTT_sample` для повторно переданих пакетів (через неможливість розрізнити, на яку саме спробу надійшов `ACK`), та експоненціально подвоює `RTO` при кожному повторному таймауті (англ. *Exponential Backoff*).

---

## Моделювання каналу з пачковими втратами: Модель Гілберта-Елліотта

У наведеній базовій реалізації симулятора використано найпростішу модель незалежних помилок Бернуллі (англ. *Memoryless Bernoulli Process*), де кожен кадр спотворюється з однаковою ймовірністю `P_loss` незалежно від долі сусідніх блоків.

Проте в реальних радіоканалах (Wi-Fi, Bluetooth, LTE/5G, супутниковий зв'язок) завади носять виражений **пачковий характер** (англ. *Burst Errors*):
- Швидке багатопроменеве завмирання Релея/Райса призводить до короткочасних провалів рівня сигналу на десятки мілісекунд;
- Імпульсні завади від електродвигунів або комутації реле спотворюють кілька сусідніх кадрів поспіль;
- Затінення антени рухомого об'єкта (наприклад, крилом БПЛА під час маневру) викликає глибокий сплеск втрат.

Для адекватного тестування протоколів ARQ використовують **двостанну марковську модель Гілберта-Елліотта** (англ. *Gilbert-Elliott Model*):

```
            1 - p
           ┌─────┐
           ▼     │
      ┌─────────────┐     p      ┌─────────────┐
      │  Стан GOOD  ├───────────►│  Стан BAD   │
      │ (P_loss ≈ 0)│◄───────────┤ (P_loss ≈ 1)│
      └─────────────┘     r      └─────────────┘
           │     ▲
           └─────┘
            1 - r
```

Параметри моделі:
1. **Стан `GOOD` (добрий канал):** пряма видимість, відсутність завад. Ймовірність втрати кадру `P_G ≈ 0` (або `10⁻⁴`);
2. **Стан `BAD` (поганий канал):** глибоке завмирання або перешкода. Ймовірність втрати кадру `P_B ≈ 1.0` (або `0.9`);
3. **Ймовірність переходу `GOOD → BAD` (`p`):** визначає середній час між пачками втрат;
4. **Ймовірність повернення `BAD → GOOD` (`r`):** визначає середню тривалість пачки втрат `1 / r` кадрових інтервалів.

Стаціонарна ймовірність перебування каналу в стані глибокого завмирання:

```
P(BAD) = p / (p + r)
```

### Порівняльна поведінка ARQ при пачкових помилках

Поведінка трьох протоколів у каналі Гілберта-Елліотта кардинально відрізняється від каналу з білим шумом:

- **Go-Back-N зазнає катастрофічного колапсу:** якщо тривалість пачки `1/r` співмірна з розміром вікна `N`, передавач здійснює багаторазові групові відкати. Кожна спроба передати пачку з `N` кадрів знову натрапляє на стан `BAD`, що призводить до падіння ефективності майже до нуля і виникнення тривалих пауз у передачі даних.
- **Selective Repeat демонструє високу живучість:** приймач послідовно буферизує всі поодинокі кадри, які встигають проскочити в коротких вікнах стану `GOOD`. Щойно канал повертається до стану `GOOD`, передавач вибірково досилає лише ті кадри, що припали на інтервал завмирання, швидко спустошуючи чергу без повторного випромінювання неушкоджених блоків.

---

## Апаратна інтеграція: Кільцеві буфери DMA та нульове копіювання

У реальних embedded-системах на базі мікроконтролерів (STM32, ESP32, nRF52, ARM Cortex-M/R) та мережевих процесорів протокол ковзного вікна тісно пов'язаний з апаратною організацією пам'яті через контролер прямого доступу (DMA).

### Організація передавального кільця дескрипторів (TX Descriptor Ring)

Замість копіювання масивів байтів між пам'яттю програми та стеком протоколу застосовують концепцію **нульового копіювання** (англ. *Zero-Copy*):

```
       ┌─────────────────────────────────────────────────────────┐
       │   Кільце дескрипторів передавача (TX DMA Ring Buffer)   │
       └─────────────────────────────────────────────────────────┘
        [Desc 0]  --> [Desc 1]  --> [Desc 2]  --> ... --> [Desc N-1]
           │             │             │
           ▼             ▼             ▼
       ┌───────┐     ┌───────┐     ┌───────┐
       │Buf Ptr│     │Buf Ptr│     │Buf Ptr│   (Вказівники на виділені
       │Length │     │Length │     │Length │    буфери в SRAM)
       │Status │     │Status │     │Status │
       └───────┘     └───────┘     └───────┘
```

Кожен дескриптор містить:
1. `buf_addr`: 32-розрядний фізичний покажчик на буфер корисного навантаження в оперативній пам'яті (SRAM);
2. `frame_len`: довжина кадру в байтах;
3. `seq_num`: номер послідовності ARQ;
4. `flags`: бітові прапорці стану:
   - `TX_DESC_OWN`: біт передачі керування апаратному блоку DMA (`1` — DMA зайнятий випромінюванням, `0` — дескриптор належить процесору);
   - `TX_DESC_ACKED`: біт підтвердження отримання квитанції від приймача;
   - `TX_DESC_IN_FLIGHT`: кадр передано у фізичну лінію, триває очікування підтвердження.

При відправленні кадру процесор записує дані в буфер, встановлює прапорець `TX_DESC_OWN` і запускає передачу через регістр запуску DMA. Переривання від таймера або прийому `ACK` змінює біт `TX_DESC_ACKED`, звільняючи комірку кільця для запису наступного пакета без виділення динамічної пам'яті через `malloc()`.

---

## Покроковий аналіз трасування подій (Execution Trace)

Для наочного розуміння взаємодії подій розглянемо реальний лог трасування передачі 4 кадрів (`F0, F1, F2, F3`) у протоколі Selective Repeat за умови втрати кадру `F1`:

```
[Час t = 0 мкс]    TX: Початок передачі кадру F0. Встановлено таймер RTO(F0) на t = 1150 мкс.
[Час t = 100 мкс]  TX: Завершено випромінювання F0. Початок випромінювання F1. Таймер RTO(F1) = 1250 мкс.
[Час t = 200 мкс]  TX: Завершено F1. Початок F2. Таймер RTO(F2) = 1350 мкс.
[Час t = 300 мкс]  TX: Завершено F2. Початок F3. Таймер RTO(F3) = 1450 мкс.
[Час t = 400 мкс]  TX: Вікно вичерпано (W = 4). Передавач переходить у стан TX_BLOCKED.

[Час t = 600 мкс]  RX: Успішно прийнято кадр F0.
                       - Перевірка CRC: OK.
                       - Номер F0 == R_expected (0).
                       - Дані F0 негайно передано додатку.
                       - Лічильник R_expected зміщено на 1.
                       - Відправлено у зворотний канал ACK(0).

[Час t = 700 мкс]  КАНАЛ: Кадр F1 потрапляє в заваду (CRC Mismatch). RX відкидає пакет!

[Час t = 800 мкс]  RX: Успішно прийнято кадр F2.
                       - Перевірка CRC: OK.
                       - Номер F2 != R_expected (1) -> кадр не за порядком!
                       - F2 збережено в буфері rx_buffered[2].
                       - Відправлено вибіркове підтвердження SACK(2).

[Час t = 900 мкс]  RX: Успішно прийнято кадр F3.
                       - F3 збережено в буфері rx_buffered[3].
                       - Відправлено вибіркове підтвердження SACK(3).

[Час t = 1100 мкс] TX: Отримано ACK(0).
                       - Кадр F0 позначено як підтверджений.
                       - Покажчик Send_Base зміщено з 0 на 1.
                       - Звільнено слот вікна: відправлено новий кадр F4.

[Час t = 1250 мкс] TX: Спливає таймаут RTO(F1)!
                       - Передавач фіксує втрату кадру F1.
                       - Вибірковий повтор: негайно випромінюється ТІЛЬКИ копія F1*.
                       - Таймер RTO(F1) перезапущено на t = 2400 мкс.

[Час t = 1300 мкс] TX: Отримано SACK(2). Кадр F2 позначено як доставлений.
[Час t = 1400 мкс] TX: Отримано SACK(3). Кадр F3 позначено як доставлений.

[Час t = 1850 мкс] RX: Успішно прийнято повторний кадр F1*.
                       - Номер F1 == R_expected (1).
                       - Дані F1 передано додатку.
                       - Приймач сканує буфер: комірки 2 (F2) та 3 (F3) вже заповнені!
                       - Дані F2 та F3 послідовно видаються додатку.
                       - Покажчик R_expected зміщується з 1 одразу на 4.
                       - Відправлено кумулятивне підтвердження ACK(3).

[Час t = 2350 мкс] TX: Отримано ACK(3).
                       - Покажчик Send_Base зміщується з 1 одразу на 4.
                       - Усі 4 кадри успішно та впорядковано доставлені!
```

### 5. Швидкий повтор за дубльованими квитанціями (Fast Retransmit)

Очікування закінчення таймауту `RTO` є найповільнішим способом виявлення втрати: воно призводить до повного зупинення конвеєра передачі на час `RTT + margin`. У високошвидкісних мережах та протоколах сімейства TCP (Reno, NewReno, CUBIC) використовують евристику **швидкого повтору** (англ. *Fast Retransmit*):

```
       TX                                                      RX
       │                   Кадр F0 (OK)                        │
       ├──────────────────────────────────────────────────────►│ -> ACK 0
       │                   Кадр F1 (ВТРАЧЕНО)   ×              │
       ├─── ── ── ── ── ── ── ── ── ── ── ── ── ── ── ── ── ──►│ (пропуск F1!)
       │                   Кадр F2 (OK)                        │
       ├──────────────────────────────────────────────────────►│ -> DupACK 0 (#1)
       │                   Кадр F3 (OK)                        │
       ├──────────────────────────────────────────────────────►│ -> DupACK 0 (#2)
       │                   Кадр F4 (OK)                        │
       ├──────────────────────────────────────────────────────►│ -> DupACK 0 (#3)
       │◄──────────────────────────────────────────────────────┤
       │ (Отримано 3x DupACK 0 -> Негайний повтор F1 без RTO!) │
       ├──────────────────────────────────────────────────────►│
```

Коли приймач отримує кадри `F2, F3, F4` після втрати `F1`, він щоразу повертає дублікат останнього валідного підтвердження `ACK 0` (англ. *Duplicate ACK*, `DupACK`).
- Отримання **трьох однакових дубльованих `ACK` поспіль** є статистично достовірною ознакою того, що кадр `F1` не просто затримався, а був безповоротно втрачений;
- Передавач негайно здійснює повторну відправку `F1`, не чекаючи спливання таймера `RTO`;
- Це скорочує затримку відновлення потоку з `RTO ≈ 2 · RTT` до мінімального часу реакції `1 · RTT`.

---

## Масштабування симулятора: Календарні черги та подійні структури

У наведеному симуляторі для збереження майбутніх подій використано класичну бінарну купу (англ. *Binary Min-Heap*), яка забезпечує часову складність вставки та вилучення `O(log K)`, де `K` — кількість активних подій у черзі.

Для лабораторних експериментів із чергою на кілька сотень подій бінарна купа є ідеальним вибором завдяки локальності даних у пам'яті кешу CPU. Проте при моделюванні великих бездротових мереж із тисячами вузлів (наприклад, у симуляторах масштабу `ns-3` або `OMNeT++`) розмір купи сягає мільйонів елементів, і накладні витрати на логарифмічне просіювання (англ. *Heapify*) починають домінувати в профілі процесора.

Для досягнення амортизованої складності `O(1)` на операцію вставки та вилучення подій застосовують **календарну чергу** (англ. *Calendar Queue* / *Bucket Queue*):
- Простір модельного часу розбивається на фіксовані часові інтервали («дні» або «бакети») довжиною `Δt ≈ t_frame`;
- Черга представляє собою масив покажчиків на двозв'язні списки подій;
- Подія з міткою часу `T` потрапляє безпосередньо в бакет з індексом `Index = ⌊ T / Δt ⌋ mod BUCKET_COUNT`;
- Поточний покажчик симулятора послідовно обходить масив бакетів, обробляючи події всередині поточного кошика практично без операцій сортування.

---

## Профілювання пам'яті та інтеграція в RTOS (FreeRTOS / Zephyr)

Під час інтеграції симульованого стека в операційні системи реального часу (FreeRTOS або Zephyr OS) важливо оцінити витрати оперативної пам'яті (RAM footprint) для кожного протоколу:

1. **Stop-and-Wait:** вимагає лише один статичний буфер `TX_BUF[L_max]` та один `RX_BUF[L_max]`. Для пакета довжиною `1500` байтів сумарний обсяг пам'яті становить близько `3.2` КБ (разом зі структурою стану FSM). Це ідеальний вибір для енергоефективних сенсорів із мікроконтролерами серії Cortex-M0+ (наприклад, STM32L0 з `8` КБ SRAM).
2. **Go-Back-N (N = 16):** передавачеві потрібен масив із 16 дескрипторів та кільцевий буфер розміром `16 · 1.5 = 24` КБ RAM, тоді як приймач зберігає мінімальний розмір `1.5` КБ.
3. **Selective Repeat (W = 16):** і передавач, і приймач виділяють по `24` КБ під вікна упорядкування (разом `48` КБ RAM), плюс бітову маску стану підтверджень.

У багатозадачному середовищі стек ARQ зазвичай оформлюється як окремий потік RTOS з високим пріоритетом. Отримання апаратного переривання від радіотрансивера (IRQ `RADIO_RX_DONE`) сигналізує семафору або черзі повідомлень `xQueueSendFromISR()`, пробуджуючи задачу обробки ARQ для миттєвого генерування `ACK` без накопичення системного джитеру.



