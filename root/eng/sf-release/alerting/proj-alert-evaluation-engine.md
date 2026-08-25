# ⚙️ Розробка рушія обчислення та маршрутизації алертів

Розробка автономної системи моніторингу вимагає створення компактного та високоефективного рушія обчислення правил (Alert Evaluation Engine), здатного працювати безпосередньо всередині бінарного файлу застосунку як вбудована бібліотека або як окремий сервісний демон. Такий рушій повинен виконувати повний цикл обробки сигналів телеметрії: від оцінки предикатів і контролю часових затримок до обчислення цифрових відбитків міток, дедуплікації та інгібування.

## Архітектура внутрішніх компонентів рушія

Надійний рушій обчислення складається з чотирьох взаємопов'язаних підсистем:

1. **Модуль скінченного автомата правил (Rule State Machine):**
   Керує життєвим циклом кожного окремого правила, відстежуючи час першого перетину порогу та захищаючи систему від хибних спрацьовувань через таймер затримки `for`.

2. **Модуль детермінованого цифрового відбитка (Label Fingerprinting):**
   Обчислює унікальний 64-бітний хеш для довільного набору пар ключ-значення міток. Гарантує повну стабільність хешу незалежно від внутрішнього порядку зберігання пар у пам'яті.

3. **Модуль приглушення та інгібування (Inhibition Engine):**
   Будує орієнтований ациклічний граф (DAG) залежностей між правилами для автоматичного блокування вторинних алертів під час активності батьківського сповіщення.

4. **Модуль диспетчеризації та сповіщень (Dispatch & Notification Router):**
   Перевіряє фільтри приглушення та передає готові пакети сповіщень у зовнішні канали зв'язку.

```
                  ┌────────────────────────────────────────┐
                  │          Потік часових рядів           │
                  └───────────────────┬────────────────────┘
                                      │
                                      ▼
                  ┌────────────────────────────────────────┐
                  │    Скінченний автомат правила (for)    │
                  │   INACTIVE ──► PENDING ──► FIRING      │
                  └───────────────────┬────────────────────┘
                                      │  (стан FIRING)
                                      ▼
                  ┌────────────────────────────────────────┐
                  │   Хешування міток (FNV-1a Fingerprint) │
                  └───────────────────┬────────────────────┘
                                      │
                                      ▼
                  ┌────────────────────────────────────────┐
                  │      Граф інгібування (Inhibition)     │
                  │    Батько FIRING ? ──► Блокувати       │
                  └───────────────────┬────────────────────┘
                                      │  (якщо не заблоковано)
                                      ▼
                  ┌────────────────────────────────────────┐
                  │    Диспетчер доставки (Dispatch)       │
                  └────────────────────────────────────────┘
```

## Скінченний автомат станів правила

Кожне правило моніторингу функціонує як детермінований скінченний автомат із чотирма станами:
- `ALERT_STATE_INACTIVE`: умова правила не виконується (`false`), таймери скинуто.
- `ALERT_STATE_PENDING`: умова стала істинною (`true`), запущено відлік таймера `for_duration`. Сповіщення черговим не надсилається.
- `ALERT_STATE_FIRING`: умова утримується довше ніж `for_duration`, алерт активний, генерується подія сповіщення.
- `ALERT_STATE_RESOLVED`: метрика повернулася в норму після стану `Firing`, генерується подія закриття інциденту.

## Повний вихідний код реалізації

Нижче наведено робочу реалізацію рушія обчислення та інгібування мовами C++20, C та Go.

:::tabs
```cpp
#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <unordered_map>
#include <chrono>
#include <memory>
#include <cstdint>
#include <algorithm>

namespace alerting {

using Clock = std::chrono::steady_clock;
using TimePoint = Clock::time_point;
using Seconds = std::chrono::seconds;

enum class AlertState {
    Inactive,
    Pending,
    Firing,
    Resolved
};

std::string_view stateToString(AlertState state) {
    switch (state) {
        case AlertState::Inactive: return "INACTIVE";
        case AlertState::Pending:  return "PENDING";
        case AlertState::Firing:   return "FIRING";
        case AlertState::Resolved: return "RESOLVED";
    }
    return "UNKNOWN";
}

// 64-бітне детерміноване FNV-1a хешування міток (Fingerprint)
uint64_t computeFingerprint(const std::unordered_map<std::string, std::string>& labels) {
    std::vector<std::pair<std::string_view, std::string_view>> sortedLabels;
    sortedLabels.reserve(labels.size());
    for (const auto& [k, v] : labels) {
        sortedLabels.emplace_back(k, v);
    }
    // Лексикографічне сортування обов'язкове для стабільності хешу
    std::sort(sortedLabels.begin(), sortedLabels.end());

    uint64_t hash = 0xcbf29ce484222325ULL;
    constexpr uint64_t prime = 0x100000001b3ULL;

    for (const auto& [k, v] : sortedLabels) {
        for (char c : k) { hash ^= static_cast<uint8_t>(c); hash *= prime; }
        hash ^= 0xff; hash *= prime; // байт-розділювач між ключем і значенням
        for (char c : v) { hash ^= static_cast<uint8_t>(c); hash *= prime; }
        hash ^= 0xfe; hash *= prime; // байт-розділювач між парами
    }
    return hash;
}

struct AlertRule {
    std::string name;
    std::unordered_map<std::string, std::string> labels;
    std::unordered_map<std::string, std::string> annotations;
    Seconds forDuration;
    AlertState state{AlertState::Inactive};
    TimePoint stateChangeTime{};
    uint64_t fingerprint{0};

    AlertRule(std::string ruleName, 
              std::unordered_map<std::string, std::string> lbls,
              std::unordered_map<std::string, std::string> annos,
              Seconds duration)
        : name(std::move(ruleName)),
          labels(std::move(lbls)),
          annotations(std::move(annos)),
          forDuration(duration) {
        labels["alertname"] = name;
        fingerprint = computeFingerprint(labels);
    }

    void evaluate(bool conditionMet, TimePoint now, const auto& notifyCallback) {
        switch (state) {
            case AlertState::Inactive:
                if (conditionMet) {
                    if (forDuration == Seconds(0)) {
                        state = AlertState::Firing;
                        stateChangeTime = now;
                        notifyCallback(*this, "Alert triggered immediately (for = 0)");
                    } else {
                        state = AlertState::Pending;
                        stateChangeTime = now;
                    }
                }
                break;

            case AlertState::Pending:
                if (!conditionMet) {
                    state = AlertState::Inactive;
                    stateChangeTime = now;
                } else if (now - stateChangeTime >= forDuration) {
                    state = AlertState::Firing;
                    stateChangeTime = now;
                    notifyCallback(*this, "Condition sustained across for-duration");
                }
                break;

            case AlertState::Firing:
                if (!conditionMet) {
                    state = AlertState::Resolved;
                    stateChangeTime = now;
                    notifyCallback(*this, "Metric recovered to normal state");
                    state = AlertState::Inactive;
                }
                break;

            case AlertState::Resolved:
                state = conditionMet ? AlertState::Pending : AlertState::Inactive;
                stateChangeTime = now;
                break;
        }
    }
};

struct InhibitionRule {
    std::string sourceAlertName;
    std::string targetAlertName;
    std::vector<std::string> equalLabels; // мітки, які мають збігатися

    bool suppresses(const AlertRule& source, const AlertRule& target) const {
        if (source.state != AlertState::Firing) return false;
        if (source.name != sourceAlertName || target.name != targetAlertName) return false;

        for (const auto& lbl : equalLabels) {
            auto itSrc = source.labels.find(lbl);
            auto itTgt = target.labels.find(lbl);
            if (itSrc == source.labels.end() || itTgt == target.labels.end()) return false;
            if (itSrc->second != itTgt->second) return false;
        }
        return true;
    }
};

class AlertEngine {
private:
    std::vector<std::unique_ptr<AlertRule>> rules_;
    std::vector<InhibitionRule> inhibitionRules_;

public:
    void addRule(std::unique_ptr<AlertRule> rule) {
        rules_.push_back(std::move(rule));
    }

    void addInhibition(InhibitionRule rule) {
        inhibitionRules_.push_back(std::move(rule));
    }

    void process(const std::unordered_map<std::string, bool>& conditions, TimePoint now) {
        auto notify = [this](const AlertRule& firingRule, std::string_view reason) {
            // Перевірка правил інгібування перед відправкою сповіщення
            for (const auto& inh : inhibitionRules_) {
                for (const auto& other : rules_) {
                    if (inh.suppresses(*other, firingRule)) {
                        std::cout << "[SUPPRESSED] Alert '" << firingRule.name 
                                  << "' inhibited by parent '" << other->name << "'\n";
                        return;
                    }
                }
            }

            std::cout << "[DISPATCH] Alert: " << firingRule.name 
                      << " | State: " << stateToString(firingRule.state)
                      << " | Fingerprint: " << std::hex << firingRule.fingerprint << std::dec
                      << " | Reason: " << reason << "\n";
        };

        for (auto& rule : rules_) {
            auto it = conditions.find(rule->name);
            bool isMet = (it != conditions.end() && it->second);
            rule->evaluate(isMet, now, notify);
        }
    }
};

} // namespace alerting

int main() {
    using namespace alerting;
    AlertEngine engine;

    // Реєструємо батьківське правило (NodeDown) та дочірнє (InstanceHighLatency)
    engine.addRule(std::make_unique<AlertRule>(
        "NodeDown",
        std::unordered_map<std::string, std::string>{{"cluster", "prod-eu"}, {"node", "node-01"}},
        std::unordered_map<std::string, std::string>{{"summary", "Host is unreachable"}},
        Seconds(2)
    ));

    engine.addRule(std::make_unique<AlertRule>(
        "InstanceHighLatency",
        std::unordered_map<std::string, std::string>{{"cluster", "prod-eu"}, {"node", "node-01"}},
        std::unordered_map<std::string, std::string>{{"summary", "API latency p99 > 500ms"}},
        Seconds(2)
    ));

    // Правило інгібування: NodeDown глушить InstanceHighLatency на тому ж вузлі
    engine.addInhibition(InhibitionRule{
        .sourceAlertName = "NodeDown",
        .targetAlertName = "InstanceHighLatency",
        .equalLabels = {"cluster", "node"}
    });

    auto now = Clock::now();
    std::cout << "--- Крок 1: Початок збою (Latency + NodeDown у стані PENDING) ---\n";
    engine.process({{"NodeDown", true}, {"InstanceHighLatency", true}}, now);

    now += Seconds(3);
    std::cout << "\n--- Крок 2: Час минув (Обидва перейшли в FIRING, але Latency інгібовано) ---\n";
    engine.process({{"NodeDown", true}, {"InstanceHighLatency", true}}, now);

    now += Seconds(5);
    std::cout << "\n--- Крок 3: Вузол відновився (NodeDown RESOLVED) ---\n";
    engine.process({{"NodeDown", false}, {"InstanceHighLatency", false}}, now);

    return 0;
}
```
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <stdbool.h>
#include <time.h>

typedef enum {
    STATE_INACTIVE,
    STATE_PENDING,
    STATE_FIRING,
    STATE_RESOLVED
} AlertState;

const char* state_to_str(AlertState s) {
    switch (s) {
        case STATE_INACTIVE: return "INACTIVE";
        case STATE_PENDING:  return "PENDING";
        case STATE_FIRING:   return "FIRING";
        case STATE_RESOLVED: return "RESOLVED";
        default:             return "UNKNOWN";
    }
}

typedef struct {
    char key[64];
    char val[64];
} Label;

typedef struct {
    char name[64];
    Label labels[8];
    int label_count;
    int for_seconds;
    AlertState state;
    time_t state_change_time;
    uint64_t fingerprint;
} AlertRuleC;

// Хешування рядка алгоритмом FNV-1a
uint64_t fnv1a_hash(const char* str, uint64_t hash) {
    const uint64_t prime = 0x100000001b3ULL;
    while (*str) {
        hash ^= (uint8_t)(*str++);
        hash *= prime;
    }
    return hash;
}

uint64_t compute_c_fingerprint(const AlertRuleC* r) {
    uint64_t hash = 0xcbf29ce484222325ULL;
    for (int i = 0; i < r->label_count; ++i) {
        hash = fnv1a_hash(r->labels[i].key, hash);
        hash ^= 0xff;
        hash = fnv1a_hash(r->labels[i].val, hash);
        hash ^= 0xfe;
    }
    return hash;
}

void rule_init(AlertRuleC* r, const char* name, int for_sec) {
    strncpy(r->name, name, sizeof(r->name) - 1);
    r->label_count = 0;
    r->for_seconds = for_sec;
    r->state = STATE_INACTIVE;
    r->state_change_time = 0;
    r->fingerprint = 0;
}

void rule_add_label(AlertRuleC* r, const char* k, const char* v) {
    if (r->label_count < 8) {
        strncpy(r->labels[r->label_count].key, k, 63);
        strncpy(r->labels[r->label_count].val, v, 63);
        r->label_count++;
    }
    r->fingerprint = compute_c_fingerprint(r);
}

void rule_evaluate(AlertRuleC* r, bool condition_met, time_t now) {
    switch (r->state) {
        case STATE_INACTIVE:
            if (condition_met) {
                if (r->for_seconds == 0) {
                    r->state = STATE_FIRING;
                    r->state_change_time = now;
                    printf("[DISPATCH] Alert: %s | State: FIRING | Fingerprint: %llx\n", 
                           r->name, (unsigned long long)r->fingerprint);
                } else {
                    r->state = STATE_PENDING;
                    r->state_change_time = now;
                }
            }
            break;

        case STATE_PENDING:
            if (!condition_met) {
                r->state = STATE_INACTIVE;
                r->state_change_time = now;
            } else if ((now - r->state_change_time) >= r->for_seconds) {
                r->state = STATE_FIRING;
                r->state_change_time = now;
                printf("[DISPATCH] Alert: %s | State: FIRING | Fingerprint: %llx\n", 
                       r->name, (unsigned long long)r->fingerprint);
            }
            break;

        case STATE_FIRING:
            if (!condition_met) {
                r->state = STATE_RESOLVED;
                r->state_change_time = now;
                printf("[DISPATCH] Alert: %s | State: RESOLVED | Normalization\n", r->name);
                r->state = STATE_INACTIVE;
            }
            break;

        case STATE_RESOLVED:
            r->state = condition_met ? STATE_PENDING : STATE_INACTIVE;
            r->state_change_time = now;
            break;
    }
}

int main(void) {
    AlertRuleC r;
    rule_init(&r, "DiskSpaceLow", 3);
    rule_add_label(&r, "mount", "/var/lib/data");
    rule_add_label(&r, "tier", "storage");

    time_t t = 1000;
    printf("--- t=1000: Condition true -> State PENDING ---\n");
    rule_evaluate(&r, true, t);

    printf("--- t=1002: Condition true (< 3s) -> State PENDING ---\n");
    rule_evaluate(&r, true, t + 2);

    printf("--- t=1004: Condition true (>= 3s) -> State FIRING ---\n");
    rule_evaluate(&r, true, t + 4);

    printf("--- t=1010: Condition false -> State RESOLVED ---\n");
    rule_evaluate(&r, false, t + 10);

    return 0;
}
```
```go
package main

import (
	"crypto/sha256"
	"encoding/hex"
	"fmt"
	"sort"
	"time"
)

type AlertState int

const (
	StateInactive AlertState = iota
	StatePending
	StateFiring
	StateResolved
)

func (s AlertState) String() string {
	return [...]string{"INACTIVE", "PENDING", "FIRING", "RESOLVED"}[s]
}

type AlertRule struct {
	Name            string
	Labels          map[string]string
	ForDuration     time.Duration
	State           AlertState
	StateChangeTime time.Time
	Fingerprint     string
}

func NewAlertRule(name string, labels map[string]string, forDuration time.Duration) *AlertRule {
	labels["alertname"] = name
	rule := &AlertRule{
		Name:        name,
		Labels:      labels,
		ForDuration: forDuration,
		State:       StateInactive,
	}
	rule.Fingerprint = rule.computeFingerprint()
	return rule
}

func (r *AlertRule) computeFingerprint() string {
	keys := make([]string, 0, len(r.Labels))
	for k := range r.Labels {
		keys = append(keys, k)
	}
	sort.Strings(keys)

	h := sha256.New()
	for _, k := range keys {
		h.Write([]byte(k + ":" + r.Labels[k] + ";"))
	}
	return hex.EncodeToString(h.Sum(nil))[:16]
}

func (r *AlertRule) Evaluate(conditionMet bool, now time.Time, notify func(r *AlertRule, reason string)) {
	switch r.State {
	case StateInactive:
		if conditionMet {
			if r.ForDuration == 0 {
				r.State = StateFiring
				r.StateChangeTime = now
				notify(r, "Triggered immediately")
			} else {
				r.State = StatePending
				r.StateChangeTime = now
			}
		}
	case StatePending:
		if !conditionMet {
			r.State = StateInactive
			r.StateChangeTime = now
		} else if now.Sub(r.StateChangeTime) >= r.ForDuration {
			r.State = StateFiring
			r.StateChangeTime = now
			notify(r, "Sustained across for-duration")
		}
	case StateFiring:
		if !conditionMet {
			r.State = StateResolved
			r.StateChangeTime = now
			notify(r, "Normalized")
			r.State = StateInactive
		}
	case StateResolved:
		if conditionMet {
			r.State = StatePending
		} else {
			r.State = StateInactive
		}
		r.StateChangeTime = now
	}
}

func main() {
	rule := NewAlertRule("HighCPU", map[string]string{"host": "prod-app-01"}, 2*time.Second)
	now := time.Now()

	notify := func(r *AlertRule, reason string) {
		fmt.Printf("[DISPATCH] Alert: %s | State: %s | Fingerprint: %s | Reason: %s\n",
			r.Name, r.State, r.Fingerprint, reason)
	}

	fmt.Println("--- Step 1: Condition Met (Pending) ---")
	rule.Evaluate(true, now, notify)

	fmt.Println("\n--- Step 2: Time elapsed (Firing) ---")
	rule.Evaluate(true, now.Add(3*time.Second), notify)

	fmt.Println("\n--- Step 3: Condition cleared (Resolved) ---")
	rule.Evaluate(false, now.Add(5*time.Second), notify)
}
```
:::

## Покроковий розбір виконання та ланцюга подій

Простежимо роботу коду крок за кроком під час змодельованого інциденту:

1. **Крок 1 (`t = 0`):**
   На сервері виникає аварія: падає вузол `node-01` (`NodeDown = true`) і водночас зростає затримка API на цьому ж вузлі (`InstanceHighLatency = true`).
   Обидва правила мають `forDuration = 2s`. Рушій фіксує перехід обох правил із `Inactive` у `Pending`, запам'ятовуючи поточну мітку часу `stateChangeTime`. **Жодного виклику notify не відбувається** — диспетчер мовчить, захищаючи інженера від реакції на короткочасні сплески.

2. **Крок 2 (`t = 3s`):**
   Минуло 3 секунди (більше ніж `forDuration = 2s`). Умова збою залишається істинною.
   - Правило `NodeDown` переходить у стан `Firing`. Рушій перевіряє правила інгібування: для `NodeDown` активних блокувальників немає, тому сповіщення успішно надсилається (`[DISPATCH] Alert: NodeDown`).
   - Правило `InstanceHighLatency` також намагається перейти у `Firing`. Проте рушій знаходить активне правило інгібування: джерело `NodeDown` уже перебуває у стані `Firing`, а мітки `cluster="prod-eu"` та `node="node-01"` повністю збігаються. Сповіщення блокується (`[SUPPRESSED] Alert 'InstanceHighLatency' inhibited by parent 'NodeDown'`). Інженер отримує лише один кореневий виклик.

3. **Крок 3 (`t = 8s`):**
   Вузол відновлено, обидві умови стають `false`. Правило `NodeDown` генерує сповіщення про нормалізацію (`[DISPATCH] Alert: NodeDown | State: RESOLVED`), після чого автомати повертаються в режим очікування `Inactive`.

## Аналіз складності та архітектурних рішень

### 1. Алгоритмічна складність оцінки правил:
- **Обчислення відбитка (Fingerprint):** Сортування `K` міток вимагає часу `O(K · log K)`. Оскільки кількість міток в одному правилі зазвичай не перевищує 10–15, накладні витрати на хешування мізерні (менше 50 наносекунд на сучасних процесорах).
- **Перевірка інгібування:** Для `M` активних правил та `I` правил інгібування перевірка виконується за `O(I · M)`. При зростанні кількості правил до десятків тисяч використовується індексація за хеш-таблицями міток замість повного перебору.

### 2. Монотонний годинник проти астрономічного:
У реалізації C++ обов'язково використовується `std::chrono::steady_clock`, а не `system_clock`. Астрономічний годинник операційної системи може стрибати назад через синхронізацію NTP, що призведе до зависання таймера `for` або передчасного хибного спрацьовування.

### 3. Недетермінованість хешу відбитка:
Якщо ітеруватись по хеш-таблиці `std::unordered_map` без попереднього лексикографічного сортування ключів, порядок обходу залежатиме від внутрішнього розміщення кошиків у пам'яті. Той самий набір міток отримає різні відбитки в різних процесах, що повністю зламає дедуплікацію.

### 4. Витік пам'яті на динамічних мітках (High Churn):
Якщо в мітки алерту потрапляють динамічні ідентифікатори (наприклад, `user_id` або `request_id`), таблиця правил накопичуватиме мільйони унікальних об'єктів. Рушій повинен містити тайм-аут очищення (Garbage Collection) для видалення правил у стані `Inactive`, які не оновлювалися понад 1 годину.

### 5. Ациклічність графа інгібування (Inhibition DAG):
Якщо конфігурація містить циклічні залежності (наприклад, правило А глушить Б, а Б глушить А), рушій може потрапити в стан невизначеності або взаємного блокування. Під час завантаження конфігурації рушій зобов'язаний виконати топологічне сортування та перевірку графа на відсутність циклів за допомогою алгоритму Тар'яна або Кана.

### 6. Багатопотокова синхронізація без блокування гарячого шляху:
Для систем під навантаженням понад 100 000 метрик на секунду рушій використовує структуру подвійної буферизації (Double Buffering) або копіювання при записі (Copy-on-Write). Оцінка правил читає незмінний знімок таблиці міток, тоді як фоновий потік оновлює стани без блокування гарячого шляху обробки сповіщень.

### 7. Збереження стану при плановому перезапуску (State Persistence):
Під час граціозної зупинки процесу (Graceful Shutdown) рушій зберігає карту активних таймерів `stateChangeTime` у локальний журнал випереджального запису (WAL — Write-Ahead Log). Це гарантує, що плановий перезапуск демона моніторингу не призведе до скидання 5-хвилинного таймера `for` та запізнення критичного сповіщення.
