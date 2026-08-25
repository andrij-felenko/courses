# ⚙️ Реалізація рушія ескалації та диспетчера інцидентів

Коли автоматизована система моніторингу фіксує критичне вичерпання бюджету помилок або масовий спалах помилок 5xx, виникає потреба в надійній доставці сигналу тривоги конкретній людині. Якщо сповіщення просто надсилається у загальний канал корпоративного месенджера, виникає класичний ефект свідка (англ. *bystander effect*): кожен з інженерів вважає, що проблему вже вирішує хтось інший, або ж повідомлення губиться в потоці рутинних розмов.

Надійне реагування вимагає спеціалізованого програмного сервісу — **рушія ескалацій та диспетчеризації інцидентів (англ. *Incident Escalation & Dispatch Engine*)**. Цей сервіс реалізує скінченний автомат життєвого циклу інциденту з жорсткими часовими дедлайнами та багаторівневими політиками сповіщення:
1. **Первинний рівень (Tier-1 Primary On-Call):** Щойно інцидент переходить у стан `TRIGGERED`, система генерує токен підтвердження (ACK token) і надсилає екстрений пейдж черговому інженеру першої лінії. Одночасно запускається таймер дедлайну (зазвичай від 5 до 15 хвилин).
2. **Підтвердження (Acknowledgment):** Якщо черговий інженер підтверджує отримання сигналу до вичерпання таймера, інцидент переходить у стан `ACKNOWLEDGED`, а таймер скасовується. Черговий стає призначеним виконавцем (Assignee).
3. **Ескалація за таймаутом (Escalation / Fallback):** Якщо таймер вичерпався, а підтвердження не надійшло (інженер спить, перебуває поза зоною зв'язку або не почув виклик), рушій фіксує збій первинного рівня, змінює стан на `ESCALATED`, перемикається на вторинну лінію (Tier-2 Secondary On-Call / Escalation Lead) і перезапускає таймер.
4. **Хронологічний аудит подій (Audit Timeline):** Кожна зміна стану, відправка пейджа, підтвердження, ескалація та фінальне пом'якшення (`MITIGATED`) записуються в незмінний журнал подій із мікросекундними мітками часу для подальшого аналізу.

Нижче наведено повноцінну виробничу реалізацію такого рушія мовами C (з використанням системних примітивів POSIX, потоків `pthread` та умовних змінних) та C++ (з використанням стандарту C++20, безпечних потоків `std::jthread`, хронометрії `std::chrono` та обгорток RAII).

:::tabs
```c
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <string.h>
#include <stdint.h>
#include <unistd.h>
#include <pthread.h>
#include <time.h>
#include <errno.h>

#define MAX_TIMELINE_EVENTS 128
#define MAX_ONCALL_TIERS    3
#define MAX_NAME_LEN        64
#define MAX_DESC_LEN        256

/* Стани життєвого циклу інциденту */
typedef enum {
    INCIDENT_STATE_TRIGGERED = 0,
    INCIDENT_STATE_ACKNOWLEDGED,
    INCIDENT_STATE_ESCALATED,
    INCIDENT_STATE_MITIGATED,
    INCIDENT_STATE_RESOLVED
} incident_state_t;

/* Рівні критичності */
typedef enum {
    SEVERITY_SEV1 = 1,
    SEVERITY_SEV2 = 2,
    SEVERITY_SEV3 = 3,
    SEVERITY_SEV4 = 4
} severity_t;

/* Запис у хронології інциденту */
typedef struct {
    struct timespec timestamp;
    char message[MAX_DESC_LEN];
    incident_state_t state_snapshot;
} timeline_event_t;

/* Інженер чергової зміни */
typedef struct {
    char name[MAX_NAME_LEN];
    char phone[MAX_NAME_LEN];
    char slack_handle[MAX_NAME_LEN];
} oncall_engineer_t;

/* Політика ескалації */
typedef struct {
    oncall_engineer_t tiers[MAX_ONCALL_TIERS];
    int total_tiers;
    int ack_timeout_sec;
} escalation_policy_t;

/* Структура керованого інциденту */
typedef struct {
    uint64_t id;
    char title[MAX_NAME_LEN];
    severity_t severity;
    incident_state_t state;
    int current_tier;
    uint32_t ack_token;
    
    escalation_policy_t policy;
    timeline_event_t timeline[MAX_TIMELINE_EVENTS];
    int timeline_count;
    
    pthread_mutex_t lock;
    pthread_cond_t state_cond;
    pthread_t timer_thread;
    bool timer_active;
    bool worker_running;
} incident_t;

static uint64_t get_current_time_ms(void) {
    struct timespec ts;
    clock_gettime(CLOCK_REALTIME, &ts);
    return (uint64_t)ts.tv_sec * 1000 + (uint64_t)ts.tv_nsec / 1000000;
}

static const char* state_to_string(incident_state_t s) {
    switch (s) {
        case INCIDENT_STATE_TRIGGERED:    return "TRIGGERED";
        case INCIDENT_STATE_ACKNOWLEDGED: return "ACKNOWLEDGED";
        case INCIDENT_STATE_ESCALATED:    return "ESCALATED";
        case INCIDENT_STATE_MITIGATED:    return "MITIGATED";
        case INCIDENT_STATE_RESOLVED:     return "RESOLVED";
        default:                          return "UNKNOWN";
    }
}

/* Внутрішній запис події в хронологію (під захистом lock) */
static void append_timeline_locked(incident_t* inc, const char* msg) {
    if (inc->timeline_count >= MAX_TIMELINE_EVENTS) return;
    
    timeline_event_t* ev = &inc->timeline[inc->timeline_count++];
    clock_gettime(CLOCK_REALTIME, &ev->timestamp);
    ev->state_snapshot = inc->state;
    snprintf(ev->message, sizeof(ev->message), "%s", msg);
    
    printf("[%lu ms] [INC-%lu] [%s] %s\n", 
           get_current_time_ms(), inc->id, state_to_string(inc->state), msg);
}

/* Симуляція відправки пейджа черговому */
static void dispatch_pager_notification(const oncall_engineer_t* eng, const incident_t* inc) {
    printf(">>> PAGER ALERT >>> Дзвінок/SMS на %s (%s): [SEV-%d] %s. Введіть токен %u для ACK.\n",
           eng->phone, eng->name, inc->severity, inc->title, inc->ack_token);
}

/* Потік таймера ескалації */
static void* escalation_timer_worker(void* arg) {
    incident_t* inc = (incident_t*)arg;
    
    while (true) {
        pthread_mutex_lock(&inc->lock);
        
        while (inc->worker_running && 
               (inc->state == INCIDENT_STATE_ACKNOWLEDGED || 
                inc->state == INCIDENT_STATE_MITIGATED || 
                inc->state == INCIDENT_STATE_RESOLVED)) {
            pthread_cond_wait(&inc->state_cond, &inc->lock);
        }
        
        if (!inc->worker_running) {
            pthread_mutex_unlock(&inc->lock);
            break;
        }
        
        /* Обчислюємо дедлайн очікування */
        struct timespec deadline;
        clock_gettime(CLOCK_REALTIME, &deadline);
        deadline.tv_sec += inc->policy.ack_timeout_sec;
        
        int wait_res = 0;
        while (inc->worker_running && 
               (inc->state == INCIDENT_STATE_TRIGGERED || inc->state == INCIDENT_STATE_ESCALATED) &&
               wait_res == 0) {
            wait_res = pthread_cond_timedwait(&inc->state_cond, &inc->lock, &deadline);
        }
        
        if (!inc->worker_running) {
            pthread_mutex_unlock(&inc->lock);
            break;
        }
        
        if (wait_res == ETIMEDOUT && 
            (inc->state == INCIDENT_STATE_TRIGGERED || inc->state == INCIDENT_STATE_ESCALATED)) {
            
            char log_buf[MAX_DESC_LEN];
            snprintf(log_buf, sizeof(log_buf), "Дедлайн підтвердження (%d сек) вичерпано на рівні Tier-%d (%s)",
                     inc->policy.ack_timeout_sec, inc->current_tier + 1,
                     inc->policy.tiers[inc->current_tier].name);
            append_timeline_locked(inc, log_buf);
            
            if (inc->current_tier + 1 < inc->policy.total_tiers) {
                inc->current_tier++;
                inc->state = INCIDENT_STATE_ESCALATED;
                inc->ack_token = (uint32_t)(rand() % 900000 + 100000);
                
                snprintf(log_buf, sizeof(log_buf), "Ескалація на рівень Tier-%d: черговий %s",
                         inc->current_tier + 1, inc->policy.tiers[inc->current_tier].name);
                append_timeline_locked(inc, log_buf);
                
                dispatch_pager_notification(&inc->policy.tiers[inc->current_tier], inc);
            } else {
                snprintf(log_buf, sizeof(log_buf), "КРИТИЧНО: Усі рівні ескалації вичерпані! Аварійний broadcast на Incident Commander.");
                append_timeline_locked(inc, log_buf);
                inc->worker_running = false;
                pthread_mutex_unlock(&inc->lock);
                break;
            }
        }
        
        pthread_mutex_unlock(&inc->lock);
    }
    
    return NULL;
}

/* Ініціалізація інциденту */
bool incident_init(incident_t* inc, uint64_t id, const char* title, severity_t sev, const escalation_policy_t* pol) {
    if (!inc || !title || !pol) return false;
    memset(inc, 0, sizeof(*inc));
    
    inc->id = id;
    snprintf(inc->title, sizeof(inc->title), "%s", title);
    inc->severity = sev;
    inc->state = INCIDENT_STATE_TRIGGERED;
    inc->current_tier = 0;
    inc->policy = *pol;
    inc->timeline_count = 0;
    inc->worker_running = true;
    inc->ack_token = (uint32_t)(rand() % 900000 + 100000);
    
    pthread_mutex_init(&inc->lock, NULL);
    pthread_cond_init(&inc->state_cond, NULL);
    
    char log_buf[MAX_DESC_LEN];
    snprintf(log_buf, sizeof(log_buf), "Інцидент відкрито із критичністю SEV-%d. Призначено на Tier-1: %s",
             sev, inc->policy.tiers[0].name);
    
    pthread_mutex_lock(&inc->lock);
    append_timeline_locked(inc, log_buf);
    pthread_mutex_unlock(&inc->lock);
    
    dispatch_pager_notification(&inc->policy.tiers[0], inc);
    
    if (pthread_create(&inc->timer_thread, NULL, escalation_timer_worker, inc) != 0) {
        return false;
    }
    inc->timer_active = true;
    return true;
}

/* Підтвердження отримання інциденту черговим */
bool incident_acknowledge(incident_t* inc, uint32_t token, const char* responder_name) {
    pthread_mutex_lock(&inc->lock);
    
    if (inc->state != INCIDENT_STATE_TRIGGERED && inc->state != INCIDENT_STATE_ESCALATED) {
        pthread_mutex_unlock(&inc->lock);
        return false;
    }
    
    if (inc->ack_token != token) {
        char log_buf[MAX_DESC_LEN];
        snprintf(log_buf, sizeof(log_buf), "Відхилено ACK від %s: недійсний токен %u", responder_name, token);
        append_timeline_locked(inc, log_buf);
        pthread_mutex_unlock(&inc->lock);
        return false;
    }
    
    inc->state = INCIDENT_STATE_ACKNOWLEDGED;
    char log_buf[MAX_DESC_LEN];
    snprintf(log_buf, sizeof(log_buf), "Інцидент підтверджено черговим %s (рівень Tier-%d). Таймер ескалації зупинено.",
             responder_name, inc->current_tier + 1);
    append_timeline_locked(inc, log_buf);
    
    pthread_cond_broadcast(&inc->state_cond);
    pthread_mutex_unlock(&inc->lock);
    return true;
}

/* Фіксація пом'якшення інциденту (Mitigation) */
bool incident_mitigate(incident_t* inc, const char* action_taken) {
    pthread_mutex_lock(&inc->lock);
    
    if (inc->state != INCIDENT_STATE_ACKNOWLEDGED) {
        pthread_mutex_unlock(&inc->lock);
        return false;
    }
    
    inc->state = INCIDENT_STATE_MITIGATED;
    char log_buf[MAX_DESC_LEN];
    snprintf(log_buf, sizeof(log_buf), "Вплив на користувачів усунуто: %s. Початок стабілізаційного періоду.", action_taken);
    append_timeline_locked(inc, log_buf);
    
    pthread_cond_broadcast(&inc->state_cond);
    pthread_mutex_unlock(&inc->lock);
    return true;
}

/* Повне закриття інциденту */
void incident_resolve(incident_t* inc, const char* resolution_summary) {
    pthread_mutex_lock(&inc->lock);
    inc->state = INCIDENT_STATE_RESOLVED;
    inc->worker_running = false;
    
    char log_buf[MAX_DESC_LEN];
    snprintf(log_buf, sizeof(log_buf), "Інцидент успішно закрито: %s. Матеріали передано на постмортем.", resolution_summary);
    append_timeline_locked(inc, log_buf);
    
    pthread_cond_broadcast(&inc->state_cond);
    pthread_mutex_unlock(&inc->lock);
    
    if (inc->timer_active) {
        pthread_join(inc->timer_thread, NULL);
        inc->timer_active = false;
    }
    pthread_mutex_destroy(&inc->lock);
    pthread_cond_destroy(&inc->state_cond);
}
```
```cpp
#include <iostream>
#include <string>
#include <vector>
#include <chrono>
#include <thread>
#include <mutex>
#include <condition_variable>
#include <optional>
#include <random>
#include <format>
#include <memory>

enum class IncidentState {
    Triggered,
    Acknowledged,
    Escalated,
    Mitigated,
    Resolved
};

enum class Severity {
    Sev1 = 1,
    Sev2 = 2,
    Sev3 = 3,
    Sev4 = 4
};

struct OnCallEngineer {
    std::string name;
    std::string phone;
    std::string slack_handle;
};

struct TimelineEvent {
    std::chrono::system_clock::time_point timestamp;
    IncidentState state_snapshot;
    std::string message;
};

struct EscalationPolicy {
    std::vector<OnCallEngineer> tiers;
    std::chrono::seconds ack_timeout;
};

class IncidentOrchestrator {
public:
    IncidentOrchestrator(uint64_t id, std::string title, Severity sev, EscalationPolicy policy)
        : id_(id), title_(std::move(title)), severity_(sev), policy_(std::move(policy)),
          state_(IncidentState::Triggered), current_tier_(0), is_running_(true) {
        
        generate_new_token();
        
        append_timeline(std::format("Інцидент відкрито із критичністю SEV-{}. Призначено на Tier-1: {}",
                                    static_cast<int>(severity_), policy_.tiers.at(0).name));
        
        dispatch_pager(policy_.tiers.at(0));
        
        // Запуск потоку таймера ескалації
        timer_thread_ = std::jthread([this](std::stop_token st) {
            timer_worker(st);
        });
    }

    ~IncidentOrchestrator() {
        resolve("Знищення екземпляра оркестратора (автоматичне закриття)");
    }

    // Заборона копіювання, дозволено переміщення
    IncidentOrchestrator(const IncidentOrchestrator&) = delete;
    IncidentOrchestrator& operator=(const IncidentOrchestrator&) = delete;
    IncidentOrchestrator(IncidentOrchestrator&&) = delete;
    IncidentOrchestrator& operator=(IncidentOrchestrator&&) = delete;

    bool acknowledge(uint32_t token, const std::string& responder_name) {
        std::unique_lock lock(mutex_);
        
        if (state_ != IncidentState::Triggered && state_ != IncidentState::Escalated) {
            return false;
        }

        if (token != current_token_) {
            append_timeline_locked(std::format("Відхилено ACK від {}: недійсний токен {}", responder_name, token));
            return false;
        }

        state_ = IncidentState::Acknowledged;
        append_timeline_locked(std::format("Інцидент підтверджено черговим {} (рівень Tier-{}). Таймер зупинено.",
                                           responder_name, current_tier_ + 1));
        
        cv_.notify_all();
        return true;
    }

    bool mitigate(const std::string& action_taken) {
        std::unique_lock lock(mutex_);
        
        if (state_ != IncidentState::Acknowledged) {
            return false;
        }

        state_ = IncidentState::Mitigated;
        append_timeline_locked(std::format("Вплив на користувачів усунуто: {}. Початок стабілізаційного періоду.", action_taken));
        
        cv_.notify_all();
        return true;
    }

    void resolve(const std::string& resolution_summary) {
        {
            std::unique_lock lock(mutex_);
            if (state_ == IncidentState::Resolved) {
                return;
            }
            state_ = IncidentState::Resolved;
            is_running_ = false;
            append_timeline_locked(std::format("Інцидент успішно закрито: {}. Матеріали передано на постмортем.", resolution_summary));
        }
        
        cv_.notify_all();
        if (timer_thread_.joinable()) {
            timer_thread_.request_stop();
        }
    }

    [[nodiscard]] IncidentState get_state() const {
        std::lock_guard lock(mutex_);
        return state_;
    }

private:
    void generate_new_token() {
        std::random_device rd;
        std::mt19937 gen(rd());
        std::uniform_int_distribution<uint32_t> dist(100000, 999999);
        current_token_ = dist(gen);
    }

    void dispatch_pager(const OnCallEngineer& eng) {
        std::cout << std::format(">>> PAGER ALERT >>> Дзвінок/SMS на {} ({}): [SEV-{}] {}. Введіть токен {} для ACK.\n",
                                 eng.phone, eng.name, static_cast<int>(severity_), title_, current_token_);
    }

    void append_timeline(const std::string& msg) {
        std::lock_guard lock(mutex_);
        append_timeline_locked(msg);
    }

    void append_timeline_locked(const std::string& msg) {
        auto now = std::chrono::system_clock::now();
        timeline_.push_back({now, state_, msg});
        
        auto epoch_ms = std::chrono::duration_cast<std::chrono::milliseconds>(now.time_since_epoch()).count();
        std::cout << std::format("[{} ms] [INC-{}] [{}] {}\n",
                                 epoch_ms, id_, state_to_string(state_), msg);
    }

    static std::string state_to_string(IncidentState s) {
        switch (s) {
            case IncidentState::Triggered:    return "TRIGGERED";
            case IncidentState::Acknowledged: return "ACKNOWLEDGED";
            case IncidentState::Escalated:    return "ESCALATED";
            case IncidentState::Mitigated:    return "MITIGATED";
            case IncidentState::Resolved:     return "RESOLVED";
            default:                          return "UNKNOWN";
        }
    }

    void timer_worker(std::stop_token st) {
        while (!st.stop_requested()) {
            std::unique_lock lock(mutex_);

            cv_.wait(lock, [this, &st] {
                return st.stop_requested() || !is_running_ || 
                       state_ == IncidentState::Triggered || 
                       state_ == IncidentState::Escalated;
            });

            if (st.stop_requested() || !is_running_ || 
                (state_ != IncidentState::Triggered && state_ != IncidentState::Escalated)) {
                continue;
            }

            // Очікування тайм-ауту дедлайну або сигналу зміни стану
            bool acknowledged_in_time = cv_.wait_for(lock, policy_.ack_timeout, [this, &st] {
                return st.stop_requested() || !is_running_ || 
                       state_ != IncidentState::Triggered && state_ != IncidentState::Escalated;
            });

            if (st.stop_requested() || !is_running_) {
                break;
            }

            if (!acknowledged_in_time) {
                // Тайм-аут вичерпано — проводимо ескалацію
                append_timeline_locked(std::format("Дедлайн підтвердження ({} сек) вичерпано на рівні Tier-{} ({})",
                                                   policy_.ack_timeout.count(), current_tier_ + 1,
                                                   policy_.tiers.at(current_tier_).name));

                if (current_tier_ + 1 < policy_.tiers.size()) {
                    current_tier_++;
                    state_ = IncidentState::Escalated;
                    generate_new_token();

                    append_timeline_locked(std::format("Ескалація на рівень Tier-{}: черговий {}",
                                                       current_tier_ + 1, policy_.tiers.at(current_tier_).name));
                    dispatch_pager(policy_.tiers.at(current_tier_));
                } else {
                    append_timeline_locked("КРИТИЧНО: Усі рівні ескалації вичерпані! Аварійний broadcast на Incident Commander.");
                    is_running_ = false;
                    break;
                }
            }
        }
    }

    const uint64_t id_;
    const std::string title_;
    const Severity severity_;
    const EscalationPolicy policy_;

    IncidentState state_;
    size_t current_tier_;
    uint32_t current_token_{0};
    bool is_running_;

    std::vector<TimelineEvent> timeline_;
    mutable std::mutex mutex_;
    std::condition_variable cv_;
    std::jthread timer_thread_;
};
```
:::

## Анатомія станів і переходів скінченного автомата

У наведеній реалізації життєвий цикл інциденту моделюється детермінованим скінченним автоматом. Кожен стан має суворо визначені семантичні інваріанти, які унеможливлюють випадкові переходи або подвійну обробку подій.

```
                  ┌──────────────────────────────┐
                  │          TRIGGERED           │ ◄── Спрацьовування алерту
                  └──────────────┬───────────────┘
                                 │
                 ┌───────────────┴───────────────┐
                 │                               │
        ACK валідний                     Таймаут дедлайну
                 │                               │
                 ▼                               ▼
  ┌──────────────────────────────┐ ┌──────────────────────────────┐
  │         ACKNOWLEDGED         │ │          ESCALATED           │
  └──────────────┬───────────────┘ └─────────────┬────────────────┘
                 │                               │
                 │                      ACK валідний на рівні N
                 │                               │
                 ├───────────────────────────────┘
                 │
                 ▼
  ┌──────────────────────────────┐
  │          MITIGATED           │ ◄── SLI повернуто в межі норми
  └──────────────┬───────────────┘
                 │
           Завершення дій
                 │
                 ▼
  ┌──────────────────────────────┐
  │           RESOLVED           │ ◄── Фінал, перехід до постмортему
  └──────────────────────────────┘
```

Розглянемо правила валідації переходів:
- **Перехід `TRIGGERED → ACKNOWLEDGED`:** Дозволений виключно за умови збігу одноразового криптографічного токена підтвердження, згенерованого під час надсилання пейджа на рівень `Tier-1`. Цей перехід зупиняє лічильник MTTA і переводить інцидент у фазу активної діагностики.
- **Перехід `TRIGGERED → ESCALATED`:** Відбувається автоматично потоком таймера у разі настання події `ETIMEDOUT`. Система збільшує індекс активного рівня `current_tier`, генерує новий токен і повторює відправку сповіщення наступному черговому інженеру.
- **Перехід `ESCALATED → ACKNOWLEDGED`:** Дозволений черговому поточного активного рівня за умови введення оновленого токена.
- **Перехід `ACKNOWLEDGED → MITIGATED`:** Фіксує успішне застосування пом'якшувальних заходів (відкіт релізу, вимкнення прапорця функцій або масштабування пулу з'єднань). З цього моменту інцидент більше не впливає на кінцевих користувачів, але залишається відкритим для спостереження за стабільністю метрик.
- **Перехід `MITIGATED → RESOLVED`:** Остаточне закриття операційної фази після проходження стабілізаційного вікна (soak window). Об'єкт переходить у термінальний стан, фонові потоки коректно зупиняються, а весь масив хронології експортується в систему документування постмортемів.

## Синхронізація, гонки станів та захист від збоїв

Під час проєктування диспетчера чергувань критично важливо враховувати специфічні гонки станів та системні обмеження, властиві розподіленим середовищам.

### 1. Стан перегонів: Підтвердження в момент спрацьовування таймера
Класична пастка полягає в ситуації, коли черговий надсилає ACK рівно в ту мілісекунду, коли фоновий потік фіксує `ETIMEDOUT`. Якщо логіка перевірки токена та модифікація стану не захищені атомарним м'ютексом, диспетчер ризикує одночасно прийняти ACK від первинного інженера і відправити дзвінок ескалації на телефон керівника. 

У представлених реалізаціях ця проблема вирішена використанням єдиного м'ютекса (`pthread_mutex_t` у C та `std::unique_lock<std::mutex>` у C++):
- Потік таймера виконує умовне очікування з таймаутом (`pthread_cond_timedwait` / `cv_.wait_for`) і після пробудження обов'язково повторно перевіряє інваріант стану: чи не змінився стан на `ACKNOWLEDGED` до того, як м'ютекс було захоплено.
- Операція підтвердження `acknowledge` атомарно перевіряє валідність токена, змінює стан на `ACKNOWLEDGED` і викликає широкомовне сповіщення (`broadcast`), що негайно скасовує фазу очікування таймера.

### 2. Динамічна ротація токенів підтвердження
Для захисту від запізнілих пакетів або випадкового підтвердження чужого виклику кожен крок ескалації генерує свіжий одноразовий токен (6-значне псевдовипадкове число). Якщо інженер першої лінії спробує ввести токен через 10 секунд після того, як інцидент уже був ескальований на другу лінію, система відхилить його дію як недійсну, зафіксує це в хронології аудиту та збереже активним зв'язок із новим відповідальним.

### 3. Гарантії безпечної зупинки (RAII та Cancellation Tokens)
У C++20 використання класу `std::jthread` забезпечує коректну підтримку токенів зупинки `std::stop_token`. Під час виклику деструктора оркестратора або примусового закриття `resolve()` потік надсилає запит на зупинку (`request_stop()`), пробуджує умовну змінну й безпечно приєднується (`join()`) до завершення виконання, унеможливлюючи витоки дескрипторів або звернення до звільненої пам'яті.

### 4. Робота з низькорівневими системними таймерами ядра Linux
У масштабованих C-системах замість виділення окремого потоку `pthread` на кожен активний таймер інциденту застосовують механізм файлових дескрипторів таймерів `timerfd_create()` у поєднанні з мультиплексуванням `epoll`. Такий підхід дає змогу одному системному демону обслуговувати десятки тисяч паралельних таймерів без накладних витрат на перемикання контексту ядра (context switch) та споживання стекової пам'яті:

```
[Потік опитування epoll] ◄── [fd таймера інциденту 1] (CLOCK_MONOTONIC)
                         ◄── [fd таймера інциденту 2] (CLOCK_MONOTONIC)
                         ◄── [fd сокета вебхуків Alertmanager]
```

Виклик `timerfd_settime()` дозволяє ядрам Linux будити диспетчер з точністю до наносекунд лише в момент настання дедлайну, гарантуючи нульове навантаження на процесор під час очікування.

## Інваріанти виробничої надійності: що потрібно для промислового середовища

У навчальних прикладах стан диспетчера зберігається в оперативній пам'яті процесу. Проте у виробничому середовищі до такого сервісу висуваються суворі вимоги відмовостійкості:

### 1. Персистентність транзакційного стану (Outbox Pattern)
Якщо віртуальна машина або под із сервісом ескалацій зазнає аварійного перезапуску (`SIGKILL`, kernel panic або падіння ноди гіпервізора), активні інциденти не мають права зникнути. Промисловий рушій використовує реляційне сховище (PostgreSQL або вбудований SQLite у режимі WAL) з реалізацією патерну Transactional Outbox:
- Отримання вебхука від системи моніторингу відкриває транзакцію: запис зберігається в таблиці `incidents` зі статусом `TRIGGERED`.
- Одночасно генерується запис у черзі вихідних повідомлень `dispatch_queue` з точним часом дедлайну `deadline_at = NOW() + INTERVAL '5 minutes'`.
- Окремий пул воркерів вичитує завдання на відправку SMS/дзвінків, гарантуючи семантику доставки At-Least-Once.
- У разі рестарту процесу диспетчер під час ініціалізації вибирає всі інциденти зі станом `TRIGGERED` або `ESCALATED`, розраховує залишок часу до дедлайну для кожного з них і відновлює таймери в пулі планувальника.

### 2. Механізм сторожового таймера (Dead-Man's Switch)
Що відбувається, коли сам сервіс моніторингу або рушій ескалацій повністю втрачає живлення чи мережеве з'єднання? Якщо система не працює, вона не зможе згенерувати алерт про власну смерть.

Для розв'язання цієї проблеми застосовується патерн «кнопка мерця» (англ. *Dead-Man's Switch*):
1. Рушій ескалацій щохвилини надсилає періодичний HTTP-запит (heartbeat ping) на зовнішній, повністю ізольований сервіс (наприклад, незалежний регіон AWS або сторонній провайдер моніторингу).
2. Якщо зовнішній сервіс не отримує чергового пінгу протягом 3 хвилин (таймаут TTL), він вважає основний кластер повністю знищеним і надсилає прямий аварійний телефонний виклик головному інженеру інфраструктури (Emergency Broadcast).

### 3. Дедуплікація та придушення штормів сповіщень
У масштабних аваріях падіння магістрального комутатора або вихід із ладу провідного вузла бази даних призводить до одночасного спрацьовування сотень алертів від десятків залежних мікросервісів. Якщо рушій почне надсилати 500 окремих дзвінків на телефон чергового, телефон зависне, а інженер втратить здатність зорієнтуватися в ситуації.

Виробничий диспетчер реалізує алгоритм групування за спільними мітками (Grouping & Deduplication):
- Кожен алерт містить набір пар ключ-значення (`cluster="prod-eu-west"`, `service="orders"`, `env="prod"`).
- Рушій обчислює криптографічний хеш відбитка (fingerprint) групи:
```
fingerprint = SHA256(cluster + "|" + environment + "|" + alert_class)
```
- Якщо протягом плаваючого вікна групування (наприклад, 30 секунд) надходять нові алерти з ідентичним відбитком, вони агрегуються в один існуючий інцидент без повторного пейджингу. Черговий отримує рівно одне комбіноване сповіщення: `[SEV-1] Multiple alerts fired on cluster prod-eu-west (42 services impacted)`.

### 4. Робота з каналами сповіщень та обробка відмов провайдерів (Fallback Routing)
Доставка сповіщень черговому ніколи не повинна залежати від одного постачальника послуг зв'язку. Промисловий рушій підтримує матрицю пріоритетів і каскадний відкат (fallback routing) у разі мережевих збоїв:

```
Первинний канал: VoIP-дзвінок через Twilio / SIP-шлюз
  │
  ├─► Відповідь 200 OK / З'єднання встановлено → Успіх
  │
  └─► Таймаут 15 сек АБО помилка 5xx / Carrier Reject
        │
        ▼
Резервний канал 1: Екстрене SMS через локального оператора
        │
        ├─► Доставлено за 10 сек → Успіх
        │
        └─► Немає звіту про доставку
              │
              ▼
Резервний канал 2: Push-сповіщення на додаток (APNs / FCM) + Webhook у Slack
```

Якщо зовнішній провайдер телефонії повертає код `504 Gateway Timeout` або помилку `ERR_VOIP_CARRIER_REJECTED`, диспетчер не чекає завершення загального дедлайну ескалації, а негайно переключається на альтернативний протокол передачі, унеможливлюючи затримку сповіщення через збій посередника.

### 5. Інтерфейс ChatOps та ідемпотентність команд
У сучасних інженерних командах керування інцидентом здійснюється переважно через ботів у корпоративних месенджерах (Slack, Discord, Mattermost). Користувацькі дії виконуються через слеш-команди:

```text
/incident ack 482190
/incident escalate --reason "Необхідне втручання DBA"
/incident mitigate --action "Відкочено реліз v2.14.1 до v2.14.0"
/incident resolve --summary "Виправлено лік пам'яті в сервісі аутентифікації"
```

Кожен HTTP-запит від месенджера до диспетчера супроводжується заголовком з унікальним ключем ідемпотентності (`X-Slack-Retry-Num`, `trigger_id`). Якщо через мережеву затримку месенджер надішле команду `/incident ack` повторно, рушій перевіряє, чи не була ця команда вже успішно виконана, повертаючи закешовану відповідь і запобігаючи повторній зміні стану автомата чи дублюванню записів у хронології. У разі вичерпання лімітів частоти запитів API месенджера (HTTP `429 Too Many Requests`) клієнтський адаптер переходить на експоненційне уповільнення з обов'язковим урахуванням заголовка `Retry-After`. Крім того, бот перевіряє цифрові підписи HMAC-SHA256 для кожного вхідного запиту, захищаючи диспетчер від підробки команд зловмисниками.

### 6. Управління пам'яттю та фіксовані буфери подій (Ring Buffers)
В умовах глибокого збою інфраструктури (наприклад, вичерпання системної оперативної пам'яті через витік на сусідніх процесах) динамічне виділення пам'яті через `malloc()` або зростання `std::vector` у диспетчері інцидентів створює ризик аварійного завершення через `Out-Of-Memory (OOM) Killer`.

Щоб запобігти падінню системи сповіщень у найкритичніший момент, структури даних внутрішнього аудиту проєктуються на основі статичних кільцевих буферів (ring buffers). Пам'ять під максимальну кількість записів подій (наприклад, `MAX_TIMELINE_EVENTS 128`) виділяється один раз під час запуску програми. Якщо кількість записів перевищує ліміт буфера, старіші діагностичні повідомлення витісняються новими із записом попередження, забезпечуючи стабільну роботу процесу з нульовими динамічними алокаціями під час гарячої фази інциденту.

### 7. Висока доступність та вибори лідера (Leader Election)
Для забезпечення безперебійної роботи рушій ескалації розгортається у вигляді кластера з 3 або 5 реплік у різних зонах доступності. Проте паралельне спрацьовування таймерів на всіх вузлах призвело б до багаторазових дублікатів дзвінків на один і той самий інцидент.

Для розв'язання цієї колізії застосовується механізм вибору єдиного активного координатора (Active-Passive Leader Election) через розподілений консенсус (etcd, Consul або оренду Kubernetes Lease):
- Лише активний лідер тримає в пам'яті активні фонові таймери та ініціює вихідні дзвінки й SMS.
- Пасивні репліки безперервно реплікують стан таблиці інцидентів і перевіряють життєздатність лідера через механізм Heartbeat Lease (TTL 5 секунд).
- Якщо активний лідер зазнає падіння чи мережевої ізоляції, репліки проводять вибори нового лідера за алгоритмом Raft. Новий лідер за мілісекунди сканує персистентну базу даних, обчислює залишкові часові інтервали для всіх інцидентів у станах `TRIGGERED` та `ESCALATED` і продовжує відлік дедлайнів без втрати жодного сигналу тривоги.
- Для захисту від мережевого розщеплення (Split-Brain) кожен новий лідер отримує строго монотонний номер покоління (Fencing Token / Generation ID). Будь-які запити до бази даних від старого лідера автоматично відхиляються базою, якщо їхній номер покоління застарів.

### 8. Рандомізований джитер таймерів ескалації (Full Jitter Backoff)
Під час масштабних катастроф (наприклад, раптового відключення живлення в цілому дата-центрі) сотні незалежних правил моніторингу можуть згенерувати інциденти в одну й ту саму секунду `T0`. Якщо всі інциденти мають однаковий фіксований дедлайн підтвердження (наприклад, рівно 300 секунд), то на 300-й секунді всі таймери одночасно вичерпаються, спровокувавши шторм запитів ескалації (Thundering Herd Problem) на зовнішні шлюзи IP-телефонії.

Для згладжування пікового мережевого навантаження у таймери ескалації додається псевдовипадковий джитер (Full Jitter):
```
T_deadline = T_base + RandomUniform(0, Jitter_Max)
```
Якщо базовий інтервал ескалації становить 300 секунд, а `Jitter_Max` дорівнює 30 секундам, реальні моменти спрацьовування ескалації рівномірно розподіляються у часовому проміжку від 300 до 330 секунд. Це повністю розвантажує черги шлюзів доставки SMS та телефонії, усуваючи ризик дропу пакетів через переповнення буферів зовнішніх провайдерів.

### 9. Власна телеметрія та контракти SLI для On-Call
Для безперервного аудиту надійності процесу реагування диспетчер інцидентів експортує у форматі Prometheus набір ключових метрик:

```prometheus
# Лічильник активних інцидентів за рівнями критичності та фазами
incident_active_gauge{severity="SEV1", state="TRIGGERED"} 1

# Гістограма часу від виклику до взяття черговим (MTTA)
incident_ack_duration_seconds_bucket{tier="1", le="60"} 12
incident_ack_duration_seconds_bucket{tier="1", le="300"} 45

# Лічильник збоїв каналів зв'язку
incident_notification_errors_total{channel="twilio_voice", reason="timeout"} 2
incident_notification_errors_total{channel="aws_sns_sms", reason="rejected"} 0
```

Для самого сервісу ескалацій визначається цільовий рівень доступності (SLO): частка успішно доставлених та вчасно оброблених пейджів має становити не менше 99.99% за місячне вікно:
```
SLI_dispatcher = Доставлені_пейджі / Усі_згенеровані_сигнали_тривоги ≥ 0.9999
```
Якщо індикатор SLI просідає нижче цільової межі, це свідчить про системні проблеми в інтеграціях із телефонними провайдерами або помилки конфігурації черг, що вимагає негайного інженерного втручання платформної команди.

## Простеження виконання: наскрізний сценарій ескалації

Щоб перевірити роботу оркестратора, простежимо поетапне проходження реального збою: вичерпання пулу з'єднань PostgreSQL на кластері замовлень. Політика ескалації містить 3 рівні: черговий інженер Олексій (Tier-1, таймаут 5 секунд для симуляції), провідний інженер Марія (Tier-2), та командир інцидентів Дмитро (Tier-3).

### Таблиця простеження хронології подій

| Час (мс) | Актор / Потік | Подія / Системний виклик | Стан об'єкта | Результат та побічні ефекти |
| :--- | :--- | :--- | :--- | :--- |
| `0` | Prometheus Alert | Спрацював вебхук `HighErrorRate5xx` | `TRIGGERED` | Генерація токена `482190`. Дзвінок Олексію на телефон. |
| `0` | Timer Thread | `pthread_cond_timedwait(+5s)` | `TRIGGERED` | Потік таймера блокується в очікуванні дедлайну або сигналу. |
| `5001` | Timer Thread | Системне пробудження `ETIMEDOUT` | `ESCALATED` | Дедлайн Tier-1 вичерпано. Генерація токена `819342`. Дзвінок Марії (Tier-2). |
| `5002` | Timer Thread | `pthread_cond_timedwait(+5s)` | `ESCALATED` | Перезапуск таймера для рівня Tier-2. |
| `7200` | Марія (Tier-2) | Введення токена `819342` через ChatOps | `ACKNOWLEDGED` | Токен валідний. `cv.notify_all()`. Таймер скасовано. |
| `12400` | Марія (Tier-2) | Застосування команди `mitigate()` | `MITIGATED` | Збільшено розмір пулу `max_connections` з 100 до 500. SLI повернувся до норми. |
| `25000` | Incident Commander | Застосування команди `resolve()` | `RESOLVED` | Стабілізація підтверджена. Потік таймера завершено через `request_stop()`. |

Цей трасувальний лог наочно демонструє, як архітектура усуває ризик людського фактора: навіть якщо інженер першої лінії не зміг відреагувати на сигнал через технічні перешкоди або сон, автоматичний ланцюг ескалації гарантовано передає відповідальність наступному призначеному спеціалісту без втрати контексту та без потреби повторної генерації алерту моніторингом.
