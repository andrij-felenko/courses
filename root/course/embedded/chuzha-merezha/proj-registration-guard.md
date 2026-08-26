# ⚙️ Сторож стільникової реєстрації та живлення модема

Головна небезпека для автономного стільникового пристрою — потрапити в нескінченний цикл аварійного пошуку мережі (*cell search*). Коли базова станція оператора вимикається на обслуговування, знеструмлюється або відхиляє реєстрацію із системною помилкою (*Permanent Reject*, наприклад 3GPP Cause #11 «PLMN not allowed»), радіомодем переходить у режим максимальної потужності передавача, безперервно скануючи всі доступні частотні канали. При струмі споживання 150–350 мА такий некерований пошук здатний повністю розрядити літієвий елемент живлення за лічені години.

У цій практичній вставці розібрано архітектуру, роботу зі стільниковими AT-командами та реалізацію вбудованого автомата станів, який реалізує захист від блокувань, очищення чорних списків модема та експоненційний відступ спроб реєстрації (*Registration Backoff*).

### Механіка взаємодії: чому лінійний код приречений

У навчальних прикладах роботу з модемом часто пишуть лінійно: відправити `AT+CREG?`, зробити блокуючу затримку `delay(2000)` і перевірити відповідь. У реальному полі такий підхід призводить до зависання мікроконтролера з кількох причин:

1. **Непередбачуваний час виконання команд реєстрації:** команди ручного або автоматичного вибору оператора (`AT+COPS=0`, `AT+COPS=1,2,"..."`) змушують модем сканувати радіоефір і узгоджувати сигналізацію з базовою станцією. Цей процес може тривати від 5 до 120 секунд. Будь-який фіксований лінійний таймаут або викличе хибну помилку, або заблокує весь потік виконання прошивки.
2. **Асинхронні сповіщення (URC — Unsolicited Result Codes):** модем може будь-якої миті надіслати в UART сповіщення про зміну стану мережі (наприклад, `+CEREG: 1` або `+CSQ: 21,99`) прямо посеред прийому відповіді на зовсім іншу команду. Якщо парсер не відокремлює URC від синхронних відповідей `OK` / `ERROR`, буфер відповідей зламається.
3. **Енергетична вартість безперервного сканування:** під час пошуку базової станції радіотракт модема працює на максимальній чутливості, послідовно налаштовуючи синтезатор частот на кожен канал діапазонів LTE (Band 1, 3, 7, 8, 20 тощо). Кожен цикл сканування споживає до 1.5–3.0 Дж енергії.

### Архітектура автомата реєстрації

Автомат станів повністю розділяє логіку керування часом, подачу живлення на модем та обробку відповідей через UART:

```
[POWER_OFF] ──(Таймер пробудження)──► [MODEM_BOOT]
     ▲                                      │
     │                                      ▼
[DEEP_SLEEP] ◄──(Backoff-пауза)───── [CHECK_REG] ──(Успіх)──► [ONLINE_TX]
     ▲                                      │                     │
     │                                      ▼                     │
     └───────────(Вичерпано ліміт)─── [STUCK_RECOVERY] ◄──────────┘
                                   (AT+CFUN=0 / AT+CFUN=1)    (Помилка сокета)
```

Послідовність станів та їхнє призначення:
1. **`POWER_OFF` / `BOOT`**: подача напруги на регулятор живлення модема або імпульс на вхід `PWRKEY` (зазвичай низький рівень тривалістю 500–1200 мс). Мікроконтролер очікує готовності інтерфейсу, циклічно надсилаючи команду синхронізації швидкості `AT\r`.
2. **`CHECK_REG`**: підписка на розширені статуси реєстрації (`AT+CEREG=2\r` для мереж LTE або `AT+CREG=2\r` для 2G/3G) та періодичний запит статусу.
   - Статус `1` (*Registered, home network*) або `5` (*Registered, roaming*) свідчить про успішне приєднання до стільника та перехід у стан готовності передачі `ONLINE_TX`.
   - Статус `2` (*Not registered, searching*) означає активний пошук соти. Для цього стану встановлюється жорсткий захисний ліміт часу (45 секунд).
   - Статус `3` (*Registration denied*) сигналізує про те, що оператор відхилив запит (наприклад, через відсутність оплати, блокування роумінгу або збій HSS).
3. **`STUCK_RECOVERY`**: якщо вичерпано таймаут пошуку або отримано статус `Denied`, автомат переходить до процедури виведення модема зі стану зависання. Виконується скидання радіомодуля командою `AT+CFUN=0` (переведення в режим мінімального споживання зі скиданням кешу PLMN), пауза 1 секунда, повернення в робочий режим `AT+CFUN=1` та примусовий автоматичний вибір мережі `AT+COPS=0`.
4. **`BACKOFF_SLEEP`**: модем повністю знеструмлюється апаратним транзисторним ключем (або переводиться в режим глибокого сну PSM із струмом менше 5 мкА). Мікроконтролер встановлює апаратний таймер RTC на інтервал експоненційного відступу. Інтервал подвоюється після кожної невдалої спроби: 1 хв → 2 хв → 4 хв → ... до стелі у 4 години.

### Простеження крайових випадків

Розгляньмо, як автомат реагує на типові нештатні ситуації в польових умовах:

- **Випадок 1: Базова станція аварійно знеструмлена (віялове відключення).** Модем вмикається, намагається зареєструватися, проводить у стані пошуку 45 секунд і фіксує таймаут. Замість того, щоб продовжувати пошук і спалити батарею, автомат переходить у `BACKOFF_SLEEP`. Перша пауза становить 1 хвилину, наступна — 2 хвилини, далі — 4, 8, 16 хвилин. Якщо електропостачання вежі відновлять через 6 годин, пристрій витратить лише кілька коротких 45-секундних імпульсів замість безперервного 6-годинного навантаження.
- **Випадок 2: Помилка білінгу або Cause #11 (PLMN not allowed).** Базова станція повертає відмову, і модем заносить ідентифікатор мережі до списку заборонених `FPLMN` на SIM-картці. Лінійний перезапуск мікроконтролера тут не допоможе, оскільки модем пам'ятає заборону в NVRAM. Автомат у стані `STUCK_RECOVERY` примусово виконує цикл `AT+CFUN=0` → `AT+CFUN=1` та `AT+COPS=0`, що змушує модем очистити оперативний кеш відмов і наново ініціювати процедуру селекції стільника.
- **Випадок 3: Зависання внутрішнього TCP-стека модема («чорна діра» NAT).** Якщо сокет відкрито, але відправка даних завершується помилкою через тихе видалення запису операторським шлюзом, стан `ONLINE_TX` фіксує помилку сокета і скеровує автомат у `STUCK_RECOVERY` для повного перезапуску сесії зв'язку.

### Реалізація сторожа реєстрації

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

typedef enum {
    GUARD_STATE_POWER_OFF,
    GUARD_STATE_BOOT,
    GUARD_STATE_CHECK_REG,
    GUARD_STATE_ONLINE_TX,
    GUARD_STATE_RECOVERY,
    GUARD_STATE_BACKOFF_SLEEP
} guard_state_t;

typedef struct {
    guard_state_t state;
    uint32_t state_enter_time_ms;
    uint32_t backoff_interval_sec;
    uint8_t  failed_attempts;
    bool     radio_registered;
} cellular_guard_t;

#define MAX_REG_TIMEOUT_MS     45000UL
#define BASE_BACKOFF_SEC       60UL
#define MAX_BACKOFF_SEC        14400UL // 4 години максимум
#define MAX_CONSECUTIVE_FAILS  3

void cellular_guard_init(cellular_guard_t *guard) {
    guard->state = GUARD_STATE_POWER_OFF;
    guard->state_enter_time_ms = 0;
    guard->backoff_interval_sec = BASE_BACKOFF_SEC;
    guard->failed_attempts = 0;
    guard->radio_registered = false;
}

// Заглушки апаратних дій платформи
extern void modem_hardware_power(bool enable);
extern bool modem_send_at_cmd(const char *cmd, const char *expected_resp, uint32_t timeout_ms);
extern int  modem_query_registration_status(void); // повертає 1 (home), 5 (roam), 2 (search), 3 (denied)

void cellular_guard_step(cellular_guard_t *guard, uint32_t now_ms) {
    uint32_t elapsed_in_state = now_ms - guard->state_enter_time_ms;

    switch (guard->state) {
    case GUARD_STATE_POWER_OFF:
        modem_hardware_power(true);
        guard->state = GUARD_STATE_BOOT;
        guard->state_enter_time_ms = now_ms;
        break;

    case GUARD_STATE_BOOT:
        if (modem_send_at_cmd("AT\r", "OK", 1000)) {
            // Налаштовуємо розширені відповіді реєстрації
            modem_send_at_cmd("AT+CEREG=2\r", "OK", 1000);
            guard->state = GUARD_STATE_CHECK_REG;
            guard->state_enter_time_ms = now_ms;
        } else if (elapsed_in_state > 10000) {
            // Модем не відповів на UART за 10 секунд — аварійне відновлення
            guard->state = GUARD_STATE_RECOVERY;
            guard->state_enter_time_ms = now_ms;
        }
        break;

    case GUARD_STATE_CHECK_REG: {
        int reg_status = modem_query_registration_status();
        if (reg_status == 1 || reg_status == 5) {
            // Успішно зареєстровано в мережі
            guard->radio_registered = true;
            guard->failed_attempts = 0;
            guard->backoff_interval_sec = BASE_BACKOFF_SEC; // скидаємо backoff
            guard->state = GUARD_STATE_ONLINE_TX;
            guard->state_enter_time_ms = now_ms;
        } else if (reg_status == 3 || elapsed_in_state > MAX_REG_TIMEOUT_MS) {
            // Мережа відхилила пристрій (Denied) або вичерпано 45 с пошуку
            guard->failed_attempts++;
            guard->state = GUARD_STATE_RECOVERY;
            guard->state_enter_time_ms = now_ms;
        }
        break;
    }

    case GUARD_STATE_RECOVERY:
        // Примусовий перезапуск радіотракту: вимикаємо RF, вмикаємо RF, скидаємо PLMN
        modem_send_at_cmd("AT+CFUN=0\r", "OK", 3000);
        modem_send_at_cmd("AT+CFUN=1\r", "OK", 3000);
        modem_send_at_cmd("AT+COPS=0\r", "OK", 5000); // Автоматичний вибір оператора

        // Переходимо в захисний сон з експоненційним інтервалом
        modem_hardware_power(false);
        guard->state = GUARD_STATE_BACKOFF_SLEEP;
        guard->state_enter_time_ms = now_ms;
        break;

    case GUARD_STATE_BACKOFF_SLEEP:
        if (elapsed_in_state >= guard->backoff_interval_sec * 1000UL) {
            // Експоненційне збільшення інтервалу (1хв -> 2хв -> 4хв -> ... до 4 год)
            guard->backoff_interval_sec *= 2;
            if (guard->backoff_interval_sec > MAX_BACKOFF_SEC) {
                guard->backoff_interval_sec = MAX_BACKOFF_SEC;
            }
            guard->state = GUARD_STATE_POWER_OFF;
            guard->state_enter_time_ms = now_ms;
        }
        break;

    case GUARD_STATE_ONLINE_TX:
        // Тут виконується прикладне відправлення телеметрії.
        // При фатальній помилці сокета повертаємося в RECOVERY.
        break;
    }
}
```
```cpp
#include <cstdint>
#include <chrono>
#include <string_view>
#include <optional>
#include <algorithm>

using namespace std::chrono_literals;

enum class GuardState {
    PowerOff,
    Boot,
    CheckRegistration,
    OnlineTransmission,
    Recovery,
    BackoffSleep
};

enum class RegistrationStatus {
    NotSearching = 0,
    HomeNetwork = 1,
    Searching = 2,
    RegistrationDenied = 3,
    Unknown = 4,
    Roaming = 5
};

class IModemHardware {
public:
    virtual ~IModemHardware() = default;
    virtual void setPower(bool enable) = 0;
    virtual bool sendCommand(std::string_view cmd, std::string_view expected, std::chrono::milliseconds timeout) = 0;
    virtual RegistrationStatus queryRegistration() = 0;
};

class CellularRegistrationGuard {
public:
    explicit CellularRegistrationGuard(IModemHardware& hw)
        : hardware_(hw) {}

    void process(std::chrono::milliseconds now) {
        const auto elapsed = now - stateEnterTime_;

        switch (state_) {
        case GuardState::PowerOff:
            hardware_.setPower(true);
            transitionTo(GuardState::Boot, now);
            break;

        case GuardState::Boot:
            if (hardware_.sendCommand("AT\r", "OK", 1000ms)) {
                hardware_.sendCommand("AT+CEREG=2\r", "OK", 1000ms);
                transitionTo(GuardState::CheckRegistration, now);
            } else if (elapsed > 10000ms) {
                transitionTo(GuardState::Recovery, now);
            }
            break;

        case GuardState::CheckRegistration: {
            const auto status = hardware_.queryRegistration();
            if (status == RegistrationStatus::HomeNetwork || status == RegistrationStatus::Roaming) {
                failedAttempts_ = 0;
                backoffInterval_ = baseBackoff_;
                transitionTo(GuardState::OnlineTransmission, now);
            } else if (status == RegistrationStatus::RegistrationDenied || elapsed > maxRegistrationTimeout_) {
                ++failedAttempts_;
                transitionTo(GuardState::Recovery, now);
            }
            break;
        }

        case GuardState::Recovery:
            // Очищення чорних списків модема та примусовий автоматичний вибір мережі
            hardware_.sendCommand("AT+CFUN=0\r", "OK", 3000ms);
            hardware_.sendCommand("AT+CFUN=1\r", "OK", 3000ms);
            hardware_.sendCommand("AT+COPS=0\r", "OK", 5000ms);

            hardware_.setPower(false);
            transitionTo(GuardState::BackoffSleep, now);
            break;

        case GuardState::BackoffSleep:
            if (elapsed >= backoffInterval_) {
                backoffInterval_ = std::min(backoffInterval_ * 2, maxBackoff_);
                transitionTo(GuardState::PowerOff, now);
            }
            break;

        case GuardState::OnlineTransmission:
            break;
        }
    }

    [[nodiscard]] GuardState currentState() const noexcept { return state_; }
    [[nodiscard]] std::chrono::seconds currentBackoff() const noexcept { return backoffInterval_; }

private:
    void transitionTo(GuardState newState, std::chrono::milliseconds now) noexcept {
        state_ = newState;
        stateEnterTime_ = now;
    }

    IModemHardware& hardware_;
    GuardState state_{GuardState::PowerOff};
    std::chrono::milliseconds stateEnterTime_{0ms};

    static constexpr auto baseBackoff_ = 60s;
    static constexpr auto maxBackoff_ = 14400s; // 4 години
    static constexpr auto maxRegistrationTimeout_ = 45000ms;

    std::chrono::seconds backoffInterval_{baseBackoff_};
    std::uint32_t failedAttempts_{0};
};
```
:::

### Практичні рекомендації з налагодження

1. **Моніторинг ліній UART логічним аналізатором:** при розробці обов'язково підключайте логічний аналізатор або другий USB-UART перехідник паралельно лініям `TX`/`RX` модема. Текстовий лог AT-команд із точними мітками часу дозволяє миттєво побачити, яка саме команда зависла або чому модем повернув `+CEREG: 3`.
2. **Апаратна лінія скидання (RESET_N):** ніколи не залишайте вивід апаратного скидання модема непідключеним. Якщо прошивка модема зависне через стрибок напруги під час передачі, лише короткий імпульс на лінію `RESET_N` (або повне знеструмлення через силовий ключ) поверне чипсет до життя.
3. **Контроль напруги живлення під час передачі:** у момент виходу передавача в ефір струм споживання стільникового модема утворює короткі імпульсні піки до 2.0 А (у мережах 2G) або до 0.5–0.8 А (у мережах LTE). Якщо вхідна ємність на виводі `VBAT` недостатня або внутрішній опір батареї зріс на морозі, напруга просяде нижче порогу відключення модема (зазвичай 3.3 В), викликаючи циклічний перезапуск (*Brownout Reset*). Сторож реєстрації зафіксує це як зависання на стадії `BOOT`.

