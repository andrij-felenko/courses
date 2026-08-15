# 📋 Інтерфейс специфікації Arthur-Merlin протоколів: структури даних, монети та стан верифікації

Цей довідковий документ містить повний формальний інтерфейсний контракт, структури даних та С- / C++-специфікацію протоколу виконання ігор Артура — Мерліна (Arthur-Merlin Proof Engine API), які визначають формат відкритих монет, структури повідомлень доводжувача, скінченний автомат станів, правила обробки помилок та параметри конфігурації імовірнісної верифікації.

## Огляд архітектури та модальностей інтерфейсу

Програмний інтерфейс системи верифікації Артура — Мерліна (AM Engine API) розроблено для забезпечення строгого архітектурного розділення між імовірнісним верифікатором з обмеженими ресурсами (Артур) та зовнішнім недетермінованим доводжувачем (Мерлін). Головне завдання цього інтерфейсу — надати надійний, високопродуктивний та безпечний інструментарій для генерування випадкових монет, передачі викликів через мережеві або внутрішньопроцесні канали, валідації повідомлень доводжувача та обчислення підсумкових імовірнісних оцінок надійності.

У теоретичній моделі Артура — Мерліна верифікатор володіє імовірнісним генератором і виконує поліномні детерміновані перевірки, тоді як Мерлін обчислює відповіді за рахунок необмежених ресурсів. На практичному рівні програмної реалізації це вимагає чіткого дотримання протокольних обмежень, запобігання витоку некоректних станів та мінімізації накладних витрат пам'яті у гарячому циклі верифікації.

Інтерфейс AM Engine API підтримує дві основні модальності взаємодії:
1. **Інтерактивний мережевий режим (Interactive Network Mode):** Артур та Мерлін виконують послідовний обмін повідомленнями через мережевий сокет (TCP/TLS або gRPC). Артур генерує публічні монети у реальному часі та надсилає їх у мережу, очікуючи відповіді від Мерліна з дотриманням таймаутів.
2. **Німовно-трансформований дерандомізований режим (Fiat-Shamir Non-Interactive Mode):** серія раундів публічних монет Артура замінюється послідовним хешуванням попередніх повідомлень за допомогою криптографічної хеш-функції (наприклад, BLAKE3 або SHA-256). У цьому режимі специфікація інтерфейсу використовується для побудови неінтерактивних аргументів знання (Zero-Knowledge Proofs / STARKs).

Система функціонує за принципом строгого скінченного автомата з явним контролем фаз протоколу:
- **Фаза ініціалізації (Initialization Phase):** налаштування толерантності до помилок, конфігурація джерела публічних монет, виділення буферів для повідомлень, перевірка відповідності цільового рівня обґрунтованості `target_soundness`.
- **Фаза публічного виклику (Public Coin Challenge Phase):** генерація випадкових монет Артура `r ∈ {0, 1}^q` та передача публічного контексту Мерліну.
- **Фаза відповіді Мерліна (Merlin Response Phase):** отримання доказового повідомлення `m ∈ {0, 1}^p` та перевірка цілісності переданих даних.
- **Фаза детермінованої перевірки (Verification Phase):** обчислення предиката `V(x, r, m)` та оновлення статистики довіри.
- **Фаза фінального вердикту (Final Verdict Phase):** підбиття підсумків усіх `k` раундів та формування підсумкового вердикту `AM_STATE_ACCEPTED` або `AM_STATE_REJECTED`.

```
                Скінченний автомат сесії верифікатора Артура
┌────────────────────┐   am_init_session()   ┌───────────────────────────┐
│ AM_STATE_UNINIT    │──────────────────────>│ AM_STATE_READY            │
└────────────────────┘                       └───────────────────────────┘
                                                           │
                                                           │ am_generate_challenge()
                                                           ▼
┌────────────────────┐    am_evaluate()      ┌───────────────────────────┐
│ AM_STATE_VERIFYING │<──────────────────────│ AM_STATE_WAITING_RESPONSE │
└────────────────────┘                       └───────────────────────────┘
          │                                                │
          │ Спростування (Soundness Failure)               │ Таймаут / Збій
          ▼                                                ▼
┌────────────────────┐                       ┌───────────────────────────┐
│ AM_STATE_REJECTED  │                       │ AM_STATE_ABORTED          │
└────────────────────┘                       └───────────────────────────┘
          │                                                │
          │ Успіх після k раундів                          │
          ▼                                                ▼
┌────────────────────────────────────────────────────────────────────────┐
│ AM_STATE_ACCEPTED (Формування підсумкового сертифіката довіри)       │
└────────────────────────────────────────────────────────────────────────┘
```

## Специфікація станів автомата та кодів повернення

Для забезпечення безпеки обчислень та сумісності між різними мовними платформами специфікація AM Engine стандартизує всі коди станів та помилок.

### 1. Деталізація кодів станів автомата (am_state_t)

Кожен екземпляр верифікаційної сесії Артура у будь-який момент часу перебуває у строго одному з наступних станів:

- **`AM_STATE_UNINIT` (значення `0x00`):** початковий стан об'єкта до виклику процедури ініціалізації `am_init_session`. Внутрішні буфери монет та лічильники раундів у цьому стані не виділені. Будь-який спроба викликати функції генерації викликів або перевірки з цього стану негайно повертає помилку `AM_ERR_STATE_MISMATCH`.
- **`AM_STATE_READY` (значення `0x01`):** сесія успішно ініціалізована та готова до запуску нового раунду взаємодії. Буфери монет очищені, а лічильник поточного раунду перебуває у коректній позиції.
- **`AM_STATE_WAITING_RESPONSE` (значення `0x02`):** Артур успішно згенерував публічний виклик `r` і опублікував його для Мерліна. У цьому стані верифікатор блокує генерацію нових монет і очікує надходження доказового конверта від Мерліна.
- **`AM_STATE_VERIFYING` (значення `0x03`):** верифікатор отримав відповідь від Мерліна та виконує детермінований обчислювальний предикат `V(x, r, m)`.
- **`AM_STATE_ACCEPTED` (значення `0x04`):** підсумковий термінальний стан успіху. Усі `k` раундів протоколу пройшли перевірку, і розрахована імовірність помилки є меншою або рівною `target_soundness`.
- **`AM_STATE_REJECTED` (значення `0x05`):** підсумковий термінальний стан відмови. Доводжувач Мерлін припустився помилки принаймні в одному з раундів, що свідчить про хибність початкового твердження або спробу фальсифікації доказу.
- **`AM_STATE_ABORTED` (значення `0x06`):** термінальний стан аварійного розриву. Виникає при мережевих таймаутах, виснаженні джерела ентропії або пошкодженні цілісності пам'яті.

### 2. Деталізація кодів помилок (am_error_t)

Усі функції API повертають від'ємні значення у разі виникнення помилок та `0` при успішному завершенні:

- **`AM_SUCCESS` (значення `0`):** операцію завершено без жодних зауважень.
- **`AM_ERR_INVALID_PARAM` (значення `-1`):** у функцію передано недійсний вхідний аргумент. Прикладами є `NULL`-вказівник на контекст сесії, конфігурація з `total_rounds == 0`, або нульова довжина буфера монет.
- **`AM_ERR_ENTROPY_FAILURE` (значення `-2`):** системний генератор випадкових чисел (CSPRNG) не зміг виділити необхідну кількість байтів ентропії. Виникає у разі виснаження пулу `/dev/urandom` або збою апаратного RNG.
- **`AM_ERR_BUFFER_OVERFLOW` (значення `-3`):** розмір доказового повідомлення, наданого Мерліном, перевищує максимально допустимий розмір `max_message_size`, що захищає Артура від атак типу «відмова в обслуговуванні» (DoS) та переповнення буфера.
- **`AM_ERR_TIMEOUT` (значення `-4`):** Мерлін не надав відповідь протягом часу `timeout_ms`.
- **`AM_ERR_VERIFICATION_FAILED` (значення `-5`):** обчислення предиката `V(x, r, m)` повернуло значення `false`.
- **`AM_ERR_STATE_MISMATCH` (значення `-6`):** порушено порядок виклику функцій автомата (наприклад, спроба обробити відповідь у стані `AM_STATE_READY`).

## Повний довідник структур даних у C та C++

Нижче наведено повний вихідний код заголовочних файлів специфікації мовами C (`arthur_merlin_spec.h`) та C++ (`arthur_merlin_spec.hpp`), які містять визначення всіх необхідних типів, структур даних та прототипів функцій.

:::tabs
```c
#ifndef ARTHUR_MERLIN_SPEC_H
#define ARTHUR_MERLIN_SPEC_H

#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

/* Переліки кодів станів та помилок */
typedef enum {
    AM_STATE_UNINIT = 0,
    AM_STATE_READY = 1,
    AM_STATE_WAITING_RESPONSE = 2,
    AM_STATE_VERIFYING = 3,
    AM_STATE_ACCEPTED = 4,
    AM_STATE_REJECTED = 5,
    AM_STATE_ABORTED = 6
} am_state_t;

typedef enum {
    AM_SUCCESS = 0,
    AM_ERR_INVALID_PARAM = -1,
    AM_ERR_ENTROPY_FAILURE = -2,
    AM_ERR_BUFFER_OVERFLOW = -3,
    AM_ERR_TIMEOUT = -4,
    AM_ERR_VERIFICATION_FAILED = -5,
    AM_ERR_STATE_MISMATCH = -6
} am_error_t;

/* Структура конфігурації параметрів AM-протоколу */
typedef struct {
    uint32_t total_rounds;         /* Кількість раундів ампліфікації (k) */
    size_t coin_bits_per_round;    /* Довжина випадкового виклику Артура (q) */
    size_t max_message_size;       /* Максимальний розмір відповіді Мерліна (p) */
    double target_soundness;       /* Цільова межа імовірності помилки (наприклад 1e-9) */
    uint32_t timeout_ms;           /* Часовий ліміт очікування відповіді у мс */
    bool enable_logging;           /* Прапорець детального логування сесії */
} am_config_t;

/* Конверт публічного виклику Артура (Arthur Challenge Envelope) */
typedef struct {
    uint32_t round_index;          /* Порядковий номер поточного раунду (1..k) */
    uint64_t timestamp_ns;         /* Часова мітка генерації монет у наносекундах */
    uint8_t* coin_bytes;           /* Буфер публічних випадкових бітів Артура */
    size_t coin_len;               /* Фактичний розмір виклику у байтах */
} am_challenge_t;

/* Конверт відповіді Мерліна (Merlin Proof Response Envelope) */
typedef struct {
    uint32_t round_index;          /* Порядковий номер раунду, на який відповідає Мерлін */
    uint8_t* proof_bytes;          /* Буфер доказового повідомлення Мерліна */
    size_t proof_len;              /* Фактичний розмір доказового повідомлення */
    uint64_t execution_time_us;    /* Час обчислення відповіді Мерліном у мкс */
} am_response_t;

/* Структура контексту сесії верифікатора Артура */
typedef struct am_session {
    am_state_t current_state;      /* Поточний стан автомата */
    am_config_t config;            /* Параметри конфігурації сесії */
    uint32_t current_round;        /* Поточний активний раунд */
    uint32_t successful_rounds;    /* Кількість успішно пройдених раундів */
    am_challenge_t active_challenge;/* Поточний активний виклик */
    void* user_data;               /* Допоміжний вказівник на дані користувача */
} am_session_t;

/* Прототипи функцій API специфікації C */
am_error_t am_init_session(am_session_t* session, const am_config_t* config);
am_error_t am_free_session(am_session_t* session);

am_error_t am_generate_challenge(am_session_t* session, am_challenge_t* challenge);
am_error_t am_process_response(am_session_t* session, const am_response_t* response);
am_error_t am_evaluate_round(am_session_t* session, bool (*verifier_predicate)(const am_challenge_t*, const am_response_t*, void*));

am_state_t am_get_state(const am_session_t* session);
double am_calculate_current_soundness(const am_session_t* session);

#ifdef __cplusplus
}
#endif

#endif /* ARTHUR_MERLIN_SPEC_H */
```
```cpp
#ifndef ARTHUR_MERLIN_SPEC_HPP
#define ARTHUR_MERLIN_SPEC_HPP

#include <vector>
#include <cstdint>
#include <cstddef>
#include <string>
#include <functional>
#include <memory>
#include <chrono>
#include <system_error>

namespace am_protocol {

enum class State : uint8_t {
    Uninitialized = 0,
    Ready,
    WaitingResponse,
    Verifying,
    Accepted,
    Rejected,
    Aborted
};

enum class ErrorCode : int {
    Success = 0,
    InvalidParam = -1,
    EntropyFailure = -2,
    BufferOverflow = -3,
    Timeout = -4,
    VerificationFailed = -5,
    StateMismatch = -6
};

/* Спеціалізована категорія помилок C++ std::error_category */
class ProtocolErrorCategory : public std::error_category {
public:
    const char* name() const noexcept override { return "ArthurMerlinProtocol"; }
    std::string message(int ev) const override {
        switch (static_cast<ErrorCode>(ev)) {
            case ErrorCode::Success: return "Успішне виконання";
            case ErrorCode::InvalidParam: return "Недійсний параметр конфігурації";
            case ErrorCode::EntropyFailure: return "Збій генератора випадкових монет";
            case ErrorCode::BufferOverflow: return "Переповнення буфера доказу";
            case ErrorCode::Timeout: return "Перевищено часовий ліміт очікування відповіді";
            case ErrorCode::VerificationFailed: return "Перевірка предиката повернула помилку";
            case ErrorCode::StateMismatch: return "Некоректний стан автомата сесії";
            default: return "Невідома помилка протоколу";
        }
    }
};

struct Config {
    std::size_t total_rounds{10};
    std::size_t coin_bits_per_round{256};
    std::size_t max_message_size{4096};
    double target_soundness{1e-6};
    std::chrono::milliseconds timeout{1000};
    bool enable_logging{false};
};

struct ChallengeEnvelope {
    std::uint32_t round_index{0};
    std::chrono::nanoseconds timestamp;
    std::vector<std::uint8_t> coin_bytes;
};

struct ResponseEnvelope {
    std::uint32_t round_index{0};
    std::vector<std::uint8_t> proof_bytes;
    std::chrono::microseconds execution_time;
};

using VerifierPredicate = std::function<bool(const ChallengeEnvelope&, const ResponseEnvelope&)>;

class VerifierSession {
public:
    explicit VerifierSession(const Config& config);
    ~VerifierSession() = default;

    VerifierSession(const VerifierSession&) = delete;
    VerifierSession& operator=(const VerifierSession&) = delete;

    VerifierSession(VerifierSession&&) noexcept = default;
    VerifierSession& operator=(VerifierSession&&) noexcept = default;

    ChallengeEnvelope generate_challenge();
    State process_and_verify(const ResponseEnvelope& response, const VerifierPredicate& predicate);

    [[nodiscard]] State state() const noexcept { return current_state_; }
    [[nodiscard]] std::size_t current_round() const noexcept { return current_round_; }
    [[nodiscard]] double current_soundness() const noexcept;

private:
    Config config_;
    State current_state_{State::Ready};
    std::size_t current_round_{0};
    std::size_t successful_rounds_{0};
    ChallengeEnvelope active_challenge_;
};

} // namespace am_protocol

#endif /* ARTHUR_MERLIN_SPEC_HPP */
```
:::

## Функціональний контракт та специфікація методів

Даний розділ деталізує передблоки, постблоки та інваріанти кожної функції специфікації у мовних реалізаціях C та C++.

### 1. Процедура ініціалізації сесії

:::tabs
```c
am_error_t am_init_session(am_session_t* session, const am_config_t* config);
```
```cpp
VerifierSession::VerifierSession(const Config& config);
```
:::

- **Призначення:** створення нової верифікаційної сесії Артура, перевірка параметрів та виділення системної пам'яті під буфери монет.
- **Передблоки:**
  - `session != NULL` та `config != NULL`.
  - `config->total_rounds >= 1`.
  - `config->coin_bits_per_round >= 8` та `config->coin_bits_per_round % 8 == 0`.
  - `config->max_message_size > 0`.
- **Постблоки:**
  - У разі успіху `session->current_state` встановлюється в `AM_STATE_READY`.
  - Поле `session->current_round` скидається в 0.
  - Поле `session->successful_rounds` скидається в 0.
  - Повертається значення `AM_SUCCESS` (або створюється екземпляр `VerifierSession` у C++).
- **Помилки:** якщо перевірка передблоків не пройшла, повертається `AM_ERR_INVALID_PARAM` (або генерується виняток `std::invalid_argument` у C++), а сесія залишається у стані `AM_STATE_UNINIT`.

### 2. Генерація публічного виклику

:::tabs
```c
am_error_t am_generate_challenge(am_session_t* session, am_challenge_t* challenge);
```
```cpp
ChallengeEnvelope VerifierSession::generate_challenge();
```
:::

- **Призначення:** отримання випадкових бітів монет Артура через криптографічно стійкий генератор та заповнення об'єкта виклику.
- **Передблоки:**
  - Стан автомата повинен бути `AM_STATE_READY` або `AM_STATE_VERIFYING` (при переході до наступного раунду).
  - Поточний раунд `current_round < total_rounds`.
- **Постблоки:**
  - `current_round` збільшується на 1.
  - Поле `round_index` виклику отримує значення `current_round`.
  - Буфер монет заповнюється випадковими байтами розміром `coin_bits_per_round / 8`.
  - Стан сесії переходить у `AM_STATE_WAITING_RESPONSE`.
- **Помилки:** у разі неможливості згенерувати випадкові монети повертається `AM_ERR_ENTROPY_FAILURE` (або кидається `std::system_error` з кодом `ErrorCode::EntropyFailure`), а стан переходить у `AM_STATE_ABORTED`.

### 3. Обробка відповіді та перевірка

:::tabs
```c
am_error_t am_evaluate_round(
    am_session_t* session,
    bool (*verifier_predicate)(const am_challenge_t*, const am_response_t*, void*)
);
```
```cpp
State VerifierSession::process_and_verify(
    const ResponseEnvelope& response,
    const VerifierPredicate& predicate
);
```
:::

- **Призначення:** виконання детермінованої перевірки Артура над випадковими монетами та відповіддю Мерліна.
- **Передблоки:**
  - Стан автомата дорівнює `AM_STATE_WAITING_RESPONSE`.
  - Переданий предикат `verifier_predicate` або `predicate` є дійсним (`non-null`).
- **Постблоки:**
  - Обчислюється результат предиката.
  - Якщо предикат повернув `true`:
    - Кількість успішних раундів збільшується на 1.
    - Якщо `current_round == total_rounds`, стан переходить у `AM_STATE_ACCEPTED`.
    - Інакше стан змінюється на `AM_STATE_VERIFYING`.
  - Якщо предикат повернув `false`:
    - Стан негайно змінюється на `AM_STATE_REJECTED`.
    - Повертається `AM_ERR_VERIFICATION_FAILED` (у C++) або кодується відмова у повертаній структурі.

### 4. Розрахунок поточного рівня обґрунтованості

:::tabs
```c
double am_calculate_current_soundness(const am_session_t* session);
```
```cpp
double VerifierSession::current_soundness() const noexcept;
```
:::

- **Призначення:** математичний розрахунок поточної ймовірності помилки верифікації на основі кількості пройдених раундів.
- **Формула розрахунку:**

```
Soundness(k) = (1/2)^k
```

де `k = successful_rounds`. Для 10 успішних раундів значення становить `(0.5)^10 = 0.0009765625`, а для 40 раундів — близько `9.09e-13`.

## Конфігураційна матриця та інженерні вимоги до ресурсів

Для практичного розгортання верифікатора Артура у високонавантажених або embedded-системах наведено стандартні технічні профілі конфігурації:

```
                  Матриця конфігураційних профілів AM Engine
┌──────────────────────────┬───────────────────┬───────────────────┬───────────────────┐
│ Параметр конфігурації    │ Профіль LIGHT     │ Профіль STANDARD  │ Профіль HARDENED  │
├──────────────────────────┼───────────────────┼───────────────────┼───────────────────┤
│ total_rounds (k)         │ 10                │ 30                │ 80                │
│ coin_bits_per_round (q)  │ 128 bits          │ 256 bits          │ 512 bits          │
│ max_message_size (p)     │ 1024 bytes        │ 64 KB             │ 1 MB              │
│ target_soundness         │ 1e-3 (0.001)      │ 1e-9 (10⁻⁹)       │ 1e-24 (10⁻²⁴)     │
│ timeout_ms               │ 500 ms            │ 2000 ms           │ 10000 ms          │
│ Джерело ентропії         │ /dev/urandom      │ OpenSSL RAND      │ Апаратний HSM     │
│ Витрати RAM на сесію     │ ~ 2 KB            │ ~ 128 KB          │ ~ 2 MB            │
└──────────────────────────┴───────────────────┴───────────────────┴───────────────────┘
```

Розроблена специфікація надає повний, математично обґрунтований та програмно захищений контракт для інтеграції імовірнісних доведень Артура — Мерліна у сучасні обчислювальні комплекси.
