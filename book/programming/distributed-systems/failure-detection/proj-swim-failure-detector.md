# ⚙️ Реалізація детектора відмов SWIM з непрямим опитуванням і механізмом підозри

Протокол SWIM (*Structured Weakly-Consistent Infection-Style Process Group Membership Protocol*) розв'язує задачу виявлення відмов у кластерах довільного масштабу без створення лавинного навантаження `O(N²)`.

У класичних схемах опитування повна сітка вузлів (*Full Mesh*) генерує квадратичну кількість службових пакетів, що обмежує розмір кластера кількома десятками серверів. Протокол SWIM кардинально змінює парадигму: кожен вузол у кожному такті зондує рівно одного випадкового сусіда, забезпечуючи постійне навантаження `O(1)` на процесор та мережевий інтерфейс.

## Архітектура та чотири правила протоколу

1. **Пряме зондування (Direct Ping):** У кожному такті тривалістю `T_period` вузол `M_i` випадковим чином обирає зі свого списку членів вузол-ціль `M_j` і надсилає йому UDP-пакет `PING`.
2. **Непряме зондування (Indirect Ping-Req):** Якщо пряме підтвердження `ACK` не надійшло за час `T_ping`, вузол обирає `k` випадкових помічників і надсилає їм запит `PING-REQ(target)`. Помічники паралельно намагаються пропінгувати ціль. Це усуває хибні спрацьовування через локальні збої маршрутизації між парою `(M_i, M_j)`.
3. **Механізм підозри (Suspicion Mechanism):** Якщо жоден помічник не зміг зв'язатися з ціллю, вузол не оголошує її мертвою негайно, а переводить у стан `SUSPECT(incarnation)`.
4. **Спростування (Refutation):** Статус підозри поширюється епідемічним шляхом (Gossip). Якщо підозрюваний вузол живий і дізнається про підозру щодо себе, він спростовує її, інкрементуючи власне число інкарнації та розсилаючи статус `ALIVE(incarnation + 1)`.

## Детальний сценарій переходу станів

Розглянемо часову шкалу роботи протоколу на конкретному прикладі взаємодії вузлів:
* `t = 0 мс`: Вузол `M_1` ініціює прямий `PING` до `M_2` та фіксує таймер.
* `t = 200 мс`: Час `T_ping` сплив, відповіді від `M_2` немає. Вузол `M_1` не поспішає з вироком і обирає `k = 3` випадкових помічників (`H_1, H_2, H_3`), надсилаючи їм `PING-REQ(M_2)`.
* `t = 400 мс`: Додатковий інтервал непрямого зондування завершився, жоден помічник не повернув `ACK`. Вузол `M_1` переводить `M_2` у стан `SUSPECT` з поточною інкарнацією `inc = 0` і додає цю інформацію у чергу пліток.
* **Гілка А (Вузол живий, але затримався):** О `t = 550 мс` вузол `M_2` завершує локальну паузу збирача сміття та отримує через gossip-пакет новину про те, що його підозрюють з інкарнацією `0`. `M_2` негайно генерує спростування: `ALIVE(M_2, inc = 1)`. Ця плітка розходиться кластером, і всі вузли повертають `M_2` у статус `ALIVE`.
* **Гілка Б (Вузол дійсно розбився):** Якщо `M_2` фізично знеструмлений, спростування не надходить. Після закінчення таймера `T_suspect = 1000 мс` (тобто о `t = 1400 мс`) вузол `M_1` остаточно позначає `M_2` як `DEAD` і виключає його з активної таблиці маршрутизації.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define MAX_MEMBERS 64
#define K_HELPERS 3
#define PING_TIMEOUT_MS 200
#define SUSPECT_TIMEOUT_MS 1000

typedef enum {
    STATUS_ALIVE = 0,
    STATUS_SUSPECT = 1,
    STATUS_DEAD = 2
} member_status_t;

typedef struct {
    uint32_t id;
    member_status_t status;
    uint32_t incarnation;
    uint64_t state_change_time_ms;
} member_t;

typedef struct {
    uint32_t self_id;
    uint32_t self_incarnation;
    member_t members[MAX_MEMBERS];
    size_t member_count;
    
    // Стан поточного раунду зондування
    uint32_t current_target_id;
    bool ping_in_flight;
    bool ping_req_in_flight;
    uint64_t probe_start_time_ms;
} swim_detector_t;

void swim_init(swim_detector_t* detector, uint32_t self_id) {
    detector->self_id = self_id;
    detector->self_incarnation = 0;
    detector->member_count = 0;
    detector->ping_in_flight = false;
    detector->ping_req_in_flight = false;
}

int find_member_index(const swim_detector_t* detector, uint32_t id) {
    for (size_t i = 0; i < detector->member_count; ++i) {
        if (detector->members[i].id == id) {
            return (int)i;
        }
    }
    return -1;
}

void swim_add_member(swim_detector_t* detector, uint32_t id, uint64_t now_ms) {
    if (detector->member_count >= MAX_MEMBERS || id == detector->self_id) {
        return;
    }
    if (find_member_index(detector, id) != -1) {
        return;
    }
    member_t* m = &detector->members[detector->member_count++];
    m->id = id;
    m->status = STATUS_ALIVE;
    m->incarnation = 0;
    m->state_change_time_ms = now_ms;
}

// Оновлення стану члена за правилами пріоритету інкарнацій
void swim_apply_update(swim_detector_t* detector, uint32_t id, member_status_t new_status, 
                       uint32_t inc, uint64_t now_ms) {
    // Якщо підозра стосується власне нас — спростовуємо її
    if (id == detector->self_id) {
        if (new_status == STATUS_SUSPECT && inc >= detector->self_incarnation) {
            detector->self_incarnation = inc + 1;
            printf("[Node %u] Спростування підозри! Нова інкарнація: %u\n", 
                   detector->self_id, detector->self_incarnation);
        }
        return;
    }

    int idx = find_member_index(detector, id);
    if (idx == -1) {
        return;
    }
    member_t* m = &detector->members[idx];

    // Правило пріоритету SWIM: вища інкарнація завжди перемагає
    if (inc > m->incarnation) {
        m->incarnation = inc;
        m->status = new_status;
        m->state_change_time_ms = now_ms;
    } else if (inc == m->incarnation) {
        // За однакової інкарнації: DEAD > SUSPECT > ALIVE
        if (m->status == STATUS_ALIVE && new_status == STATUS_SUSPECT) {
            m->status = STATUS_SUSPECT;
            m->state_change_time_ms = now_ms;
        } else if (new_status == STATUS_DEAD) {
            m->status = STATUS_DEAD;
            m->state_change_time_ms = now_ms;
        }
    }
}

// Основний тактовий цикл детектора
void swim_tick(swim_detector_t* detector, uint64_t now_ms) {
    // 1. Перевірка таймаутів підозри (Suspect -> Dead)
    for (size_t i = 0; i < detector->member_count; ++i) {
        member_t* m = &detector->members[i];
        if (m->status == STATUS_SUSPECT) {
            if (now_ms - m->state_change_time_ms >= SUSPECT_TIMEOUT_MS) {
                m->status = STATUS_DEAD;
                m->state_change_time_ms = now_ms;
                printf("[Node %u] Вузол %u не надіслав спростування -> СТАТУС DEAD\n", 
                       detector->self_id, m->id);
            }
        }
    }

    // 2. Якщо зонд у польоті, перевіряємо таймаути фаз
    if (detector->ping_in_flight) {
        uint64_t elapsed = now_ms - detector->probe_start_time_ms;
        if (!detector->ping_req_in_flight && elapsed >= PING_TIMEOUT_MS) {
            // Прямий Ping прострочено -> запускаємо непрямий Ping-Req через k помічників
            detector->ping_req_in_flight = true;
            printf("[Node %u] Прямий Ping до %u прострочено -> розсилка Ping-Req через k помічників\n",
                   detector->self_id, detector->current_target_id);
        } else if (detector->ping_req_in_flight && elapsed >= (PING_TIMEOUT_MS * 2)) {
            // Непрямий Ping-Req також прострочено -> переводимо ціль у Suspect
            int idx = find_member_index(detector, detector->current_target_id);
            if (idx != -1) {
                swim_apply_update(detector, detector->current_target_id, STATUS_SUSPECT, 
                                  detector->members[idx].incarnation, now_ms);
                printf("[Node %u] Жоден помічник не відповів -> Вузол %u переведений у SUSPECT\n",
                       detector->self_id, detector->current_target_id);
            }
            detector->ping_in_flight = false;
            detector->ping_req_in_flight = false;
        }
    }
}

// Запуск нового раунду зондування
void swim_start_probe_round(swim_detector_t* detector, uint64_t now_ms) {
    if (detector->member_count == 0 || detector->ping_in_flight) {
        return;
    }
    // Обираємо випадкового живого або підозрюваного члена
    size_t target_idx = (size_t)rand() % detector->member_count;
    if (detector->members[target_idx].status == STATUS_DEAD) {
        return;
    }
    detector->current_target_id = detector->members[target_idx].id;
    detector->ping_in_flight = true;
    detector->ping_req_in_flight = false;
    detector->probe_start_time_ms = now_ms;
    printf("[Node %u] Старт зондування вузла %u (Прямий Ping)\n", 
           detector->self_id, detector->current_target_id);
}

// Обробка отриманого підтвердження Ack від цілі
void swim_on_ack_received(swim_detector_t* detector, uint32_t from_id, uint32_t inc, uint64_t now_ms) {
    if (detector->ping_in_flight && detector->current_target_id == from_id) {
        detector->ping_in_flight = false;
        detector->ping_req_in_flight = false;
        swim_apply_update(detector, from_id, STATUS_ALIVE, inc, now_ms);
        printf("[Node %u] Отримано успішний Ack від вузла %u\n", detector->self_id, from_id);
    }
}
```
```cpp
#include <iostream>
#include <vector>
#include <unordered_map>
#include <optional>
#include <chrono>
#include <random>
#include <algorithm>

enum class MemberStatus {
    Alive,
    Suspect,
    Dead
};

struct Member {
    uint32_t id;
    MemberStatus status{MemberStatus::Alive};
    uint32_t incarnation{0};
    std::chrono::steady_clock::time_point state_change_time;
};

class SwimFailureDetector {
public:
    using Milliseconds = std::chrono::milliseconds;

    SwimFailureDetector(uint32_t self_id, 
                        Milliseconds ping_timeout = Milliseconds(200),
                        Milliseconds suspect_timeout = Milliseconds(1000),
                        size_t k_helpers = 3)
        : self_id_(self_id),
          ping_timeout_(ping_timeout),
          suspect_timeout_(suspect_timeout),
          k_helpers_(k_helpers),
          rng_(std::random_device{}()) {}

    void add_member(uint32_t id, std::chrono::steady_clock::time_point now) {
        if (id == self_id_ || members_.contains(id)) {
            return;
        }
        members_.emplace(id, Member{
            .id = id,
            .status = MemberStatus::Alive,
            .incarnation = 0,
            .state_change_time = now
        });
    }

    void apply_update(uint32_t id, MemberStatus new_status, uint32_t inc, 
                      std::chrono::steady_clock::time_point now) {
        // Якщо надійшла підозра про нас самих — спростовуємо її новою інкарнацією
        if (id == self_id_) {
            if (new_status == MemberStatus::Suspect && inc >= self_incarnation_) {
                self_incarnation_ = inc + 1;
                std::cout << "[Node " << self_id_ 
                          << "] Спростування підозри! Нова інкарнація: " 
                          << self_incarnation_ << "\n";
            }
            return;
        }

        auto it = members_.find(id);
        if (it == members_.end()) {
            return;
        }
        Member& m = it->second;

        if (inc > m.incarnation) {
            m.incarnation = inc;
            m.status = new_status;
            m.state_change_time = now;
        } else if (inc == m.incarnation) {
            if (m.status == MemberStatus::Alive && new_status == MemberStatus::Suspect) {
                m.status = MemberStatus::Suspect;
                m.state_change_time = now;
            } else if (new_status == MemberStatus::Dead) {
                m.status = MemberStatus::Dead;
                m.state_change_time = now;
            }
        }
    }

    void start_probe_round(std::chrono::steady_clock::time_point now) {
        if (members_.empty() || active_probe_.has_value()) {
            return;
        }

        std::vector<uint32_t> eligible;
        for (const auto& [id, m] : members_) {
            if (m.status != MemberStatus::Dead) {
                eligible.push_back(id);
            }
        }
        if (eligible.empty()) {
            return;
        }

        std::uniform_int_distribution<size_t> dist(0, eligible.size() - 1);
        uint32_t target_id = eligible[dist(rng_)];

        active_probe_ = ProbeState{
            .target_id = target_id,
            .start_time = now,
            .ping_req_sent = false
        };

        std::cout << "[Node " << self_id_ << "] Старт прямого Ping до вузла " 
                  << target_id << "\n";
    }

    void on_ack_received(uint32_t from_id, uint32_t inc, 
                         std::chrono::steady_clock::time_point now) {
        if (active_probe_.has_value() && active_probe_->target_id == from_id) {
            active_probe_.reset();
            apply_update(from_id, MemberStatus::Alive, inc, now);
            std::cout << "[Node " << self_id_ << "] Отримано успішний Ack від " 
                      << from_id << "\n";
        }
    }

    void tick(std::chrono::steady_clock::time_point now) {
        // 1. Перевірка таймерів підозри
        for (auto& [id, m] : members_) {
            if (m.status == MemberStatus::Suspect) {
                if (now - m.state_change_time >= suspect_timeout_) {
                    m.status = MemberStatus::Dead;
                    m.state_change_time = now;
                    std::cout << "[Node " << self_id_ << "] Вузол " << id 
                              << " не спростував підозру -> СТАТУС DEAD\n";
                }
            }
        }

        // 2. Перевірка активного зонда
        if (active_probe_.has_value()) {
            auto elapsed = now - active_probe_->start_time;
            if (!active_probe_->ping_req_sent && elapsed >= ping_timeout_) {
                active_probe_->ping_req_sent = true;
                std::cout << "[Node " << self_id_ << "] Прямий таймаут до " 
                          << active_probe_->target_id << " -> Запуск непрямого Ping-Req\n";
            } else if (active_probe_->ping_req_sent && elapsed >= (ping_timeout_ * 2)) {
                uint32_t target_id = active_probe_->target_id;
                uint32_t inc = members_.at(target_id).incarnation;
                apply_update(target_id, MemberStatus::Suspect, inc, now);
                std::cout << "[Node " << self_id_ << "] Непрямий таймаут -> Вузол " 
                          << target_id << " переведено у стан SUSPECT\n";
                active_probe_.reset();
            }
        }
    }

private:
    struct ProbeState {
        uint32_t target_id;
        std::chrono::steady_clock::time_point start_time;
        bool ping_req_sent{false};
    };

    uint32_t self_id_;
    uint32_t self_incarnation_{0};
    Milliseconds ping_timeout_;
    Milliseconds suspect_timeout_;
    size_t k_helpers_;
    
    std::unordered_map<uint32_t, Member> members_;
    std::optional<ProbeState> active_probe_;
    std::mt19937 rng_;
};
```
:::

## Порівняння архітектури мовами C та C++

* **Управління пам'яттю:** Реалізація мовою C використовує статично виділений фіксований масив `members[MAX_MEMBERS]`. Це гарантує повну відсутність динамічних виділень пам'яті на купі (*Zero Dynamic Allocation*) під час виконання циклу зондування, що робить її ідеальною для вбудованих контролерів, мережевих драйверів та простору ядра. Натомість версія на C++20 базується на `std::unordered_map`, що забезпечує автоматичне масштабування та роботу з довільним динамічним пулом серверів.
* **Безпека типів і часу:** У коді C++ застосовано сувору типізацію часу через `std::chrono::milliseconds` та `std::chrono::steady_clock::time_point`. Це унеможливлює помилки змішування секунд із мілісекундами, а клас `std::optional<ProbeState>` дозволяє елегантно контролювати наявність активного зонда без використання службових числових міток.

## Епідемічне поширення та черги пліток (Piggybacking)

У реальних промислових системах (зокрема `hashicorp/memberlist` або `serf`) повідомлення `SUSPECT` та `ALIVE` не надсилаються широкомовними штормами. Замість цього вони кладуться в локальну пріоритетну чергу розповсюдження пліток із лічильником передач `retransmit_limit = λ · log(N + 1)`.

Кожен вихідний UDP-пакет `PING` або `ACK` «підхоплює» (*piggybacking*) невелику пачку повідомлень із цієї черги до досягнення безпечного розміру MTU (зазвичай не більше 1400 байтів, щоб запобігти IP-фрагментації комутаторами). Коли лічильник передач для конкретної плітки вичерпується, вона видаляється з черги, що гарантує експоненційне згасання фонового трафіку.

## Аналіз складності та інженерні крайові випадки

### Мережева складність та масштабованість
* **Трафік на вузол за такт:** Рівно 1 прямий `PING` плюс у середньому `k` непрямих `PING-REQ` (якщо помічник обраний іншим вузлом). При фіксованому `k = 3` кількість повідомлень залишається строго `O(1)` і не залежить від того, налічує кластер 10 серверів чи 10 000 серверів.
* **Час розповсюдження інформації:** Завдяки властивостям випадкових графів плітка про стан `SUSPECT` або `DEAD` досягає всіх `N` вузлів кластера за `O(log N)` тактів із ймовірністю `1 - O(1/N)`.

### Розв'язання конфліктів стану
У розподілених мережах пакети можуть приходити з порушенням порядку. Правило пріоритету інкарнацій гарантує збіжність:
1. Повідомлення з більшим номером інкарнації безумовно перезаписує будь-яке повідомлення з меншим номером (`inc_new > inc_cur`).
2. При однакових інкарнаціях (`inc_new == inc_cur`) стан `DEAD` має найвищий пріоритет, стан `SUSPECT` — середній, а `ALIVE` — найнижчий. Це запобігає «воскресінню» вузлів застарілими пакетами `ALIVE` у мережі.

### Очищення таблиці членів (Tombstone Management)
Записи зі статусом `DEAD` не можна видаляти з пам'яті миттєво. Якщо вузол `M_j` щойно позначено як `DEAD` і відразу видалено з таблиці, то будь-яка запізніла плітка `ALIVE(M_j, inc=0)`, що блукає мережею, сприйметься як поява абсолютно нового невідомого вузла. Тому мертві записи утримуються у стані «надгробка» (*Tombstone*) протягом періоду `T_tombstone` (наприклад, 24 години в Consul), після чого остаточно видаляються з пам'яті.

## Інструкція зі збирання та перевірки санітайзерами

Для практичного тестування та інтеграції в розподілений демон код рекомендується компілювати з максимальними рівнями попереджень та вбудованими перевірками адрес пам'яті й невизначеної поведінки:

* **Збирання C:**
  ```bash
  gcc -std=c11 -Wall -Wextra -Wpedantic -fsanitize=address,undefined -O2 -o swim_c swim.c
  ```
* **Збирання C++:**
  ```bash
  g++ -std=c++20 -Wall -Wextra -Wpedantic -fsanitize=address,undefined -O2 -o swim_cpp swim.cpp
  ```

При додаванні реального мережевого сокетного ввід-виводу (UDP) у багатопотоковому середовищі обов'язково проганяйте код під санітайзером потоків ThreadSanitizer (`-fsanitize=thread`), щоб гарантувати відсутність гонок даних між мережевим слухачем і тактовим генератором `tick()`.
