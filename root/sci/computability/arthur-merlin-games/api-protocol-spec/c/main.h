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
