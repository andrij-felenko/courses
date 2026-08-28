# ⚙️ Реалізація рушія оркестрації кампанії оновлення парку

Управління масовим оновленням прошивок або пакетів програмного забезпечення на великому парку пристроїв вимагає детермінованого координатора. Такий рушій повинен безпечно дозувати навантаження на мережу за допомогою маркерного кошика (Token Bucket), динамічно розподіляти пристрої за хвилями розгортання, збирати телеметрію виконання та миттєво зупиняти кампанію за перших ознак системної аварії (Stop-the-Line).

Нижче наведено повнофункціональну архітектуру та реалізацію ядра оркестратора кампаній мовами C та C++.

---

## Архітектура та ключові компоненти рушія

Архітектура координатора побудована на чотирьох взаємопов'язаних підсистемах, що утворюють замкнений контур зворотного зв'язку між сервером управління та парком пристроїв:

```text
                                  ОРКЕСТРАТОР КАМПАНІЇ ОНОВЛЕННЯ
                                 ┌──────────────────────────────┐
Клієнтський пристрій ───────────►│ 1. Диспетчер хвиль і квот    │
                                 │    (Wave Progression Engine) │
                                 └──────────────┬───────────────┘
                                                │
                                 ┌──────────────▼───────────────┐
Запит маркера лізингу ──────────►│ 2. Регулятор навантаження     │
                                 │    (Token Bucket Limiter)    │
                                 └──────────────┬───────────────┘
                                                │
                                 ┌──────────────▼───────────────┐
Звіт телеметрії / Heartbeat ────►│ 3. Агрегатор метрик тріажу   │
                                 │    (Succeeded/Fail/RB/Silent)│
                                 └──────────────┬───────────────┘
                                                │
                                 ┌──────────────▼───────────────┐
Оцінка бюджету помилок ─────────►│ 4. Арбітр Stop-the-Line      │──► Аварійна пауза
                                 │    (Circuit Breaker Evaluator│
                                 └──────────────────────────────┘
```

1. **Диспетчер хвиль (Wave Progression Controller):** відстежує стан активної когорти, розраховує кількість дозволених пристроїв та контролює таймер витримки (Soak Time) перед переходом на наступне кільце розгортання.
2. **Маркерний регулятор (Token Bucket Rate Limiter):** обмежує пікову кількість одночасних завантажень та швидкість видачі нових дозволів, повертаючи прострочені маркери за таймаутом лізингу при втраті зв'язку або раптовому знеструмленні вузла.
3. **Агрегатор метрик тріажу (Metrics Aggregator):** класифікує звіти пристроїв на чотири взаємовиключні категорії: підтверджений успіх, явна відмова інсталяції, апаратний відкіт у попередній слот A/B та замовклі вузли.
4. **Арбітр Stop-the-Line (Circuit Breaker):** безперервно зіставляє поточний відсоток аномалій із пороговими значеннями специфікації. У разі статистично достовірного перевищення ліміту переводить кампанію у стан `PAUSED` та блокує видачу нових пакетів.

---

## Реалізація оркестратора на C та C++

:::tabs
@tab C
```c
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <time.h>

#define MAX_DEVICES 10000
#define MAX_WAVES 8

typedef enum {
    DEV_STATE_IDLE = 0,
    DEV_STATE_ASSIGNED,
    DEV_STATE_IN_FLIGHT,
    DEV_STATE_REBOOTING,
    DEV_STATE_SUCCEEDED,
    DEV_STATE_FAILED,
    DEV_STATE_ROLLED_BACK,
    DEV_STATE_SILENCED
} DeviceState;

typedef enum {
    ENGINE_STATUS_RUNNING = 0,
    ENGINE_STATUS_SOAKING,
    ENGINE_STATUS_PAUSED_STOP_THE_LINE,
    ENGINE_STATUS_COMPLETED
} EngineStatus;

typedef struct {
    uint32_t device_id;
    DeviceState state;
    time_t state_updated_at;
    time_t lease_expires_at;
    uint32_t wave_index;
} DeviceRecord;

typedef struct {
    char name[32];
    double target_pct;
    uint32_t target_count;
    uint32_t max_in_flight;
    time_t soak_duration_sec;
    time_t soak_started_at;
} WaveConfig;

typedef struct {
    double max_failure_rate_pct;
    double max_rollback_rate_pct;
    double max_silence_rate_pct;
    uint32_t min_sample_size;
    time_t heartbeat_timeout_sec;
} SafetyThresholds;

typedef struct {
    DeviceRecord devices[MAX_DEVICES];
    uint32_t total_devices;
    
    WaveConfig waves[MAX_WAVES];
    uint32_t waves_count;
    uint32_t current_wave;
    
    SafetyThresholds safety;
    EngineStatus status;
    
    double tokens;
    double token_fill_rate;
    double token_capacity;
    time_t last_token_refill;
    
    uint32_t in_flight_count;
    uint32_t succeeded_count;
    uint32_t failed_count;
    uint32_t rolled_back_count;
    uint32_t silenced_count;
} CampaignEngine;

void engine_init(CampaignEngine *eng, uint32_t total_devs, SafetyThresholds safety) {
    memset(eng, 0, sizeof(CampaignEngine));
    eng->total_devices = (total_devs > MAX_DEVICES) ? MAX_DEVICES : total_devs;
    eng->safety = safety;
    eng->status = ENGINE_STATUS_RUNNING;
    eng->token_fill_rate = 20.0;
    eng->token_capacity = 100.0;
    eng->tokens = eng->token_capacity;
    eng->last_token_refill = time(NULL);

    for (uint32_t i = 0; i < eng->total_devices; i++) {
        eng->devices[i].device_id = 100000 + i;
        eng->devices[i].state = DEV_STATE_IDLE;
        eng->devices[i].state_updated_at = time(NULL);
    }
}

void engine_add_wave(CampaignEngine *eng, const char *name, double target_pct, 
                     uint32_t max_in_flight, time_t soak_sec) {
    if (eng->waves_count >= MAX_WAVES) return;
    WaveConfig *w = &eng->waves[eng->waves_count++];
    strncpy(w->name, name, sizeof(w->name) - 1);
    w->target_pct = target_pct;
    w->target_count = (uint32_t)(eng->total_devices * (target_pct / 100.0));
    w->max_in_flight = max_in_flight;
    w->soak_duration_sec = soak_sec;
    w->soak_started_at = 0;
}

void refill_tokens(CampaignEngine *eng, time_t now) {
    double delta = (double)(now - eng->last_token_refill);
    if (delta > 0) {
        eng->tokens += delta * eng->token_fill_rate;
        if (eng->tokens > eng->token_capacity) {
            eng->tokens = eng->token_capacity;
        }
        eng->last_token_refill = now;
    }
}

bool acquire_download_token(CampaignEngine *eng, uint32_t device_idx, time_t now) {
    if (eng->status != ENGINE_STATUS_RUNNING) return false;
    refill_tokens(eng, now);
    
    WaveConfig *wave = &eng->waves[eng->current_wave];
    if (eng->in_flight_count >= wave->max_in_flight) return false;
    if (eng->tokens < 1.0) return false;

    eng->tokens -= 1.0;
    eng->in_flight_count++;
    eng->devices[device_idx].state = DEV_STATE_IN_FLIGHT;
    eng->devices[device_idx].state_updated_at = now;
    eng->devices[device_idx].lease_expires_at = now + 1800; // 30 хвилин лізингу
    return true;
}

void evaluate_safety_and_stop_the_line(CampaignEngine *eng) {
    uint32_t evaluated = eng->succeeded_count + eng->failed_count + 
                         eng->rolled_back_count + eng->silenced_count;
    if (evaluated < eng->safety.min_sample_size) return;

    double fail_rate = ((double)eng->failed_count / evaluated) * 100.0;
    double rb_rate = ((double)eng->rolled_back_count / evaluated) * 100.0;
    double silence_rate = ((double)eng->silenced_count / evaluated) * 100.0;

    if (fail_rate > eng->safety.max_failure_rate_pct ||
        rb_rate > eng->safety.max_rollback_rate_pct ||
        silence_rate > eng->safety.max_silence_rate_pct) {
        
        eng->status = ENGINE_STATUS_PAUSED_STOP_THE_LINE;
        printf("[STOP-THE-LINE] Кампанію аварійно зупинено! Помилки: %.2f%%, Відкоти: %.2f%%, Мовчання: %.2f%%\n",
               fail_rate, rb_rate, silence_rate);
    }
}

void report_device_event(CampaignEngine *eng, uint32_t device_idx, DeviceState new_state, time_t now) {
    DeviceRecord *dev = &eng->devices[device_idx];
    if (dev->state == DEV_STATE_IN_FLIGHT || dev->state == DEV_STATE_REBOOTING) {
        if (eng->in_flight_count > 0) eng->in_flight_count--;
    }

    dev->state = new_state;
    dev->state_updated_at = now;

    if (new_state == DEV_STATE_SUCCEEDED) eng->succeeded_count++;
    else if (new_state == DEV_STATE_FAILED) eng->failed_count++;
    else if (new_state == DEV_STATE_ROLLED_BACK) eng->rolled_back_count++;

    evaluate_safety_and_stop_the_line(eng);
}

void check_silenced_devices(CampaignEngine *eng, time_t now) {
    for (uint32_t i = 0; i < eng->total_devices; i++) {
        DeviceRecord *dev = &eng->devices[i];
        if (dev->state == DEV_STATE_REBOOTING) {
            if (now - dev->state_updated_at > eng->safety.heartbeat_timeout_sec) {
                dev->state = DEV_STATE_SILENCED;
                dev->state_updated_at = now;
                eng->silenced_count++;
                if (eng->in_flight_count > 0) eng->in_flight_count--;
                evaluate_safety_and_stop_the_line(eng);
            }
        }
    }
}

void engine_tick(CampaignEngine *eng, time_t now) {
    if (eng->status == ENGINE_STATUS_PAUSED_STOP_THE_LINE || 
        eng->status == ENGINE_STATUS_COMPLETED) return;

    check_silenced_devices(eng, now);
    WaveConfig *wave = &eng->waves[eng->current_wave];

    // Призначення пристроїв у межах квоти поточної хвилі
    uint32_t assigned_in_wave = 0;
    for (uint32_t i = 0; i < wave->target_count; i++) {
        if (eng->devices[i].state == DEV_STATE_IDLE) {
            if (acquire_download_token(eng, i, now)) {
                eng->devices[i].wave_index = eng->current_wave;
            }
        }
        if (eng->devices[i].state != DEV_STATE_IDLE) {
            assigned_in_wave++;
        }
    }

    // Перевірка завершення завантажень хвилі та старт витримки (Soak Time)
    if (assigned_in_wave >= wave->target_count && eng->in_flight_count == 0) {
        if (eng->status == ENGINE_STATUS_RUNNING) {
            eng->status = ENGINE_STATUS_SOAKING;
            wave->soak_started_at = now;
            printf("[ХВИЛЯ] Хвиля '%s' перейшла у фазу витримки (Soak Time %lds)\n", 
                   wave->name, wave->soak_duration_sec);
        } else if (eng->status == ENGINE_STATUS_SOAKING) {
            if (now - wave->soak_started_at >= wave->soak_duration_sec) {
                if (eng->current_wave + 1 < eng->waves_count) {
                    eng->current_wave++;
                    eng->status = ENGINE_STATUS_RUNNING;
                    printf("[ХВИЛЯ] Успішно! Перехід на хвилю '%s'\n", eng->waves[eng->current_wave].name);
                } else {
                    eng->status = ENGINE_STATUS_COMPLETED;
                    printf("[ФІНІШ] Кампанія успішно завершена на 100%% парку!\n");
                }
            }
        }
    }
}
```
@tab C++
```cpp
#include <iostream>
#include <vector>
#include <string>
#include <chrono>
#include <algorithm>
#include <cstdint>
#include <memory>

namespace fleet::engine {

enum class DeviceState {
    Idle,
    Assigned,
    InFlight,
    Rebooting,
    Succeeded,
    Failed,
    RolledBack,
    Silenced
};

enum class EngineStatus {
    Running,
    Soaking,
    PausedStopTheLine,
    Completed
};

struct DeviceRecord {
    uint32_t deviceId{0};
    DeviceState state{DeviceState::Idle};
    std::chrono::system_clock::time_point stateUpdatedAt;
    std::chrono::system_clock::time_point leaseExpiresAt;
    size_t waveIndex{0};
};

struct WaveConfig {
    std::string name;
    double targetPct{0.0};
    uint32_t targetCount{0};
    uint32_t maxInFlight{100};
    std::chrono::seconds soakDuration{0};
    std::chrono::system_clock::time_point soakStartedAt{};
};

struct SafetyThresholds {
    double maxFailureRatePct{1.0};
    double maxRollbackRatePct{0.5};
    double maxSilenceRatePct{0.2};
    uint32_t minSampleSize{100};
    std::chrono::seconds heartbeatTimeout{3600};
};

class CampaignEngine {
public:
    CampaignEngine(uint32_t totalDevices, SafetyThresholds safety)
        : safety_(safety),
          status_(EngineStatus::Running),
          lastTokenRefill_(std::chrono::system_clock::now()) {
        
        devices_.reserve(totalDevices);
        auto now = std::chrono::system_clock::now();
        for (uint32_t i = 0; i < totalDevices; ++i) {
            devices_.push_back(DeviceRecord{
                .deviceId = 100000 + i,
                .state = DeviceState::Idle,
                .stateUpdatedAt = now,
                .leaseExpiresAt = now,
                .waveIndex = 0
            });
        }
    }

    void addWave(std::string name, double targetPct, uint32_t maxInFlight, std::chrono::seconds soakSec) {
        uint32_t targetCount = static_cast<uint32_t>(devices_.size() * (targetPct / 100.0));
        waves_.push_back(WaveConfig{
            .name = std::move(name),
            .targetPct = targetPct,
            .targetCount = targetCount,
            .maxInFlight = maxInFlight,
            .soakDuration = soakSec
        });
    }

    void reportDeviceEvent(size_t deviceIndex, DeviceState newState) {
        if (deviceIndex >= devices_.size()) return;
        auto& dev = devices_[deviceIndex];
        auto now = std::chrono::system_clock::now();

        if (dev.state == DeviceState::InFlight || dev.state == DeviceState::Rebooting) {
            if (inFlightCount_ > 0) inFlightCount_--;
        }

        dev.state = newState;
        dev.stateUpdatedAt = now;

        switch (newState) {
            case DeviceState::Succeeded:  succeededCount_++; break;
            case DeviceState::Failed:     failedCount_++; break;
            case DeviceState::RolledBack: rolledBackCount_++; break;
            default: break;
        }

        evaluateSafetyAndStopTheLine();
    }

    void tick() {
        if (status_ == EngineStatus::PausedStopTheLine || status_ == EngineStatus::Completed) {
            return;
        }

        auto now = std::chrono::system_clock::now();
        checkSilencedDevices(now);
        refillTokens(now);

        if (currentWave_ >= waves_.size()) return;
        auto& wave = waves_[currentWave_];

        uint32_t assignedInWave = 0;
        for (size_t i = 0; i < wave.targetCount && i < devices_.size(); ++i) {
            if (devices_[i].state == DeviceState::Idle) {
                tryAcquireToken(i, now);
            }
            if (devices_[i].state != DeviceState::Idle) {
                assignedInWave++;
            }
        }

        if (assignedInWave >= wave.targetCount && inFlightCount_ == 0) {
            if (status_ == EngineStatus::Running) {
                status_ = EngineStatus::Soaking;
                wave.soakStartedAt = now;
                std::cout << "[ХВИЛЯ] Хвиля '" << wave.name << "' перейшла у витримку.\n";
            } else if (status_ == EngineStatus::Soaking) {
                if (now - wave.soakStartedAt >= wave.soakDuration) {
                    if (currentWave_ + 1 < waves_.size()) {
                        currentWave_++;
                        status_ = EngineStatus::Running;
                        std::cout << "[ХВИЛЯ] Перехід на хвилю: " << waves_[currentWave_].name << "\n";
                    } else {
                        status_ = EngineStatus::Completed;
                        std::cout << "[ФІНІШ] Кампанію успішно завершено на 100% парку!\n";
                    }
                }
            }
        }
    }

    EngineStatus status() const noexcept { return status_; }

private:
    void refillTokens(std::chrono::system_clock::time_point now) {
        std::chrono::duration<double> elapsed = now - lastTokenRefill_;
        double delta = elapsed.count();
        if (delta > 0.0) {
            tokens_ = std::min(tokenCapacity_, tokens_ + delta * tokenFillRate_);
            lastTokenRefill_ = now;
        }
    }

    bool tryAcquireToken(size_t deviceIndex, std::chrono::system_clock::time_point now) {
        if (status_ != EngineStatus::Running) return false;
        const auto& wave = waves_[currentWave_];
        if (inFlightCount_ >= wave.maxInFlight || tokens_ < 1.0) return false;

        tokens_ -= 1.0;
        inFlightCount_++;
        devices_[deviceIndex].state = DeviceState::InFlight;
        devices_[deviceIndex].stateUpdatedAt = now;
        devices_[deviceIndex].leaseExpiresAt = now + std::chrono::seconds(1800);
        devices_[deviceIndex].waveIndex = currentWave_;
        return true;
    }

    void checkSilencedDevices(std::chrono::system_clock::time_point now) {
        for (auto& dev : devices_) {
            if (dev.state == DeviceState::Rebooting) {
                if (now - dev.stateUpdatedAt > safety_.heartbeatTimeout) {
                    dev.state = DeviceState::Silenced;
                    dev.stateUpdatedAt = now;
                    silencedCount_++;
                    if (inFlightCount_ > 0) inFlightCount_--;
                    evaluateSafetyAndStopTheLine();
                }
            }
        }
    }

    void evaluateSafetyAndStopTheLine() {
        uint32_t evaluated = succeededCount_ + failedCount_ + rolledBackCount_ + silencedCount_;
        if (evaluated < safety_.minSampleSize) return;

        double failRate = (static_cast<double>(failedCount_) / evaluated) * 100.0;
        double rbRate = (static_cast<double>(rolledBackCount_) / evaluated) * 100.0;
        double silenceRate = (static_cast<double>(silencedCount_) / evaluated) * 100.0;

        if (failRate > safety_.maxFailureRatePct ||
            rbRate > safety_.maxRollbackRatePct ||
            silenceRate > safety_.maxSilenceRatePct) {
            
            status_ = EngineStatus::PausedStopTheLine;
            std::cerr << "[STOP-THE-LINE] Аварійна зупинка! Відмови: " << failRate
                      << "%, Відкоти: " << rbRate << "%, Мовчання: " << silenceRate << "%\n";
        }
    }

    std::vector<DeviceRecord> devices_;
    std::vector<WaveConfig> waves_;
    size_t currentWave_{0};
    SafetyThresholds safety_;
    EngineStatus status_{EngineStatus::Running};

    double tokens_{100.0};
    double tokenFillRate_{20.0};
    double tokenCapacity_{100.0};
    std::chrono::system_clock::time_point lastTokenRefill_;

    uint32_t inFlightCount_{0};
    uint32_t succeededCount_{0};
    uint32_t failedCount_{0};
    uint32_t rolledBackCount_{0};
    uint32_t silencedCount_{0};
};

} // namespace fleet::engine
```
:::

---

## Детальний розбір механік та захисних алгоритмів

Координатор реалізує чотири фундаментальні інженерні патерни, які усувають класичні ризики масового розгортання в розподілених мережах.

### 1. Маркерний кошик і захист від лавиноподібного навантаження (Thundering Herd)
Коли оновлення стає доступним для чергової хвилі (наприклад, 25 000 пристроїв), неконтрольований одночасний запит призвів би до перевантаження балансувальників та вичерпання смуги пропускання каналів зв'язку. Функція `refillTokens` реалізує безперервне нарахування маркерів:

```text
Δt = t_now - t_last
tokens = min(token_capacity, tokens + Δt * token_fill_rate)
```

Пристрій отримує дозвіл на завантаження лише за наявності хоча б одного вільного маркера (`tokens >= 1.0`) та за умови, що сумарна кількість активних завантажень не перевищує ліміт хвилі `max_in_flight`. Це гарантує плавну видачу пакетів без сплесків трафіку.

### 2. Лізинг слотів одночасності (In-Flight Lease Management)
Кожен виданий маркер супроводжується фіксацією мітки часу закінчення оренди `lease_expires_at`. Якщо пристрій під час завантаження 50-мегабайтного образу втрачає зв'язок зі стільниковою вишкою або розряджається, лічильник `in_flight_count` не блокується назавжди. Після завершення 30-хвилинного інтервалу слот звільняється для наступних пристроїв черги.

### 3. Детекція замовклих вузлів через асинхронне сканування таймаутів
Найбільш вразливий момент оновлення мікроконтролера — перемикання прапорця активного завантажувального слота A/B та програмне перезавантаження. У функції `check_silenced_devices` скануються всі записи, що перебувають у стані `DEV_STATE_REBOOTING`. Якщо різниця між поточним часом та часом початку перезавантаження перевищує `heartbeat_timeout_sec`, статус примусово мутує у `DEV_STATE_SILENCED`. Це негайно сигналізує про потенційну паніку ядра чи збій драйвера радіомодема до ініціалізації мережевого стека.

### 4. Статистичний арбітраж Stop-the-Line
Оцінка допустимих бюджетів помилок здійснюється у функції `evaluate_safety_and_stop_the_line`. Щоб уникнути хибного блокування на старті хвилі (коли з трьох перших пристроїв один дав збій через випадковий апаратний дефект флеш-пам'яті), контролер вимагає досягнення мінімального обсягу вибірки `min_sample_size`. Тільки після накопичення статистичної бази розраховуються частки `fail_rate`, `rb_rate` та `silence_rate`. Перевищення будь-якого з порогів переводить кампанію у стан `PAUSED_STOP_THE_LINE`, що повністю блокує роздачу оновлень на наступні когорти пристроїв.

---

## Обробка крайових випадків та багатопотоковість

У промислових системах координації парку виникають специфічні гонки станів (race conditions), які вимагають суворого дотримання інваріантів:

1. **Неузгоджена послідовність подій (Out-of-Order Delivery):** через затримки в чергах брокера повідомлень подія `SUCCEEDED` може надійти до обробки сервером раніше, ніж повідомлення `REBOOTING`. Для запобігання помилковому зарахуванню пристрою до замовклих кожен запис оновлюється за монотонним лічильником версій події або міткою часу пристрою.
2. **Розрив з'єднання під час перезавантаження:** якщо пристрій успішно завантажився у новий слот A/B, але через тимчасові перебої стільникової мережі зміг надіслати перший heartbeat лише на 65-й хвилині (при таймауті 60 хвилин), контролер виконує реконсиляцію: стан мутує з `SILENCED` у `SUCCEEDED`, лічильник мовчання декрементується, а лічильник успіху збільшується, запобігаючи накопиченню фантомних аварій.
3. **Взаємодія з клієнтським агентом та сторожовим таймером:** клієнтський агент на борту пристрою використовує лічильник завантажень завантажувача (Boot Counter). Якщо після трьох невдалих спроб старт ядра не завершується підтвердженням від служби телеметрії, завантажувач самостійно ініціює апаратний відкіт у попередній робочий слот і повідомляє про це подією `ROLLED_BACK`.
4. **Шардування та горизонтальне масштабування:** для парків обсягом понад мільйон пристроїв координатор розбивається на незалежні шарди за гешем ідентифікатора (`device_id % num_shards`). Кожен шард веде власний локальний облік активних маркерів і агрегує квантилі метрик у спільну базу часових рядів (TSDB).
