// hsm_engine.h — Заголовний файл компактного рушія HSM на C
#ifndef HSM_ENGINE_H
#define HSM_ENGINE_H

#include <stdint.h>
#include <stdbool.h>

#define MAX_STATE_DEPTH 8

enum {
    Q_SIG_EMPTY = 0,
    Q_SIG_ENTRY,
    Q_SIG_EXIT,
    Q_SIG_INIT,
    Q_SIG_USER_START = 10
};

typedef uint16_t signal_t;

typedef struct {
    signal_t sig;
    uint32_t param;
} event_t;

typedef enum {
    Q_RET_HANDLED,
    Q_RET_IGNORED,
    Q_RET_TRAN,
    Q_RET_SUPER
} q_result_t;

typedef struct hsm_tag hsm_t;
typedef q_result_t (*state_handler_t)(hsm_t *me, const event_t *e);

struct hsm_tag {
    state_handler_t state;  // Активний листовий стан
    state_handler_t temp;   // Тимчасовий стан під час транзакції
};

#define Q_TRAN(target_)  (((hsm_t *)me)->temp = (state_handler_t)(target_), Q_RET_TRAN)
#define Q_SUPER(super_)  (((hsm_t *)me)->temp = (state_handler_t)(super_), Q_RET_SUPER)
#define Q_HANDLED()      (Q_RET_HANDLED)
#define Q_IGNORED()      (Q_RET_IGNORED)

void hsm_init(hsm_t *me, state_handler_t initial);
void hsm_dispatch(hsm_t *me, const event_t *e);
q_result_t hsm_top_state(hsm_t *me, const event_t *e);

#endif // HSM_ENGINE_H
