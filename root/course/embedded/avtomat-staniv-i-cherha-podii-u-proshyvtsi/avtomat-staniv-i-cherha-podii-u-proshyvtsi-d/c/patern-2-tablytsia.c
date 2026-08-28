#include <stdint.h>
#include <stdbool.h>

typedef enum {
    STATE_IDLE,
    STATE_ARMED,
    STATE_TRIGGERED,
    STATE_MAX
} SecurityState;

typedef enum {
    SIG_SENSOR_PIR,
    SIG_CODE_ENTERED,
    SIG_TIMEOUT,
    SIG_MAX
} SecuritySignal;

typedef struct SecurityFsm SecurityFsm;
typedef void (*TransitionAction)(SecurityFsm *fsm);

typedef struct {
    SecurityState next_state;
    TransitionAction action;
} TransitionEntry;

struct SecurityFsm {
    SecurityState state;
    bool siren_active;
};

// Дії переходів
static void act_sound_alarm(SecurityFsm *fsm) { fsm->siren_active = true; }
static void act_silence_alarm(SecurityFsm *fsm) { fsm->siren_active = false; }
static void act_arm_beep(SecurityFsm *fsm) { (void)fsm; /* короткий біп */ }

// Матриця переходів: рядок = стан, стовпчик = сигнал
static const TransitionEntry transition_table[STATE_MAX][SIG_MAX] = {
    [STATE_IDLE] = {
        [SIG_CODE_ENTERED] = { STATE_ARMED, act_arm_beep },
    },
    [STATE_ARMED] = {
        [SIG_SENSOR_PIR]   = { STATE_TRIGGERED, act_sound_alarm },
        [SIG_CODE_ENTERED] = { STATE_IDLE, NULL },
    },
    [STATE_TRIGGERED] = {
        [SIG_CODE_ENTERED] = { STATE_IDLE, act_silence_alarm },
        [SIG_TIMEOUT]      = { STATE_ARMED, act_silence_alarm },
    }
};

void security_fsm_dispatch(SecurityFsm *fsm, SecuritySignal sig) {
    if (fsm->state >= STATE_MAX || sig >= SIG_MAX) return;

    const TransitionEntry *t = &transition_table[fsm->state][sig];
    if (t->next_state != STATE_IDLE || t->action != NULL) {
        if (t->action) {
            t->action(fsm);
        }
        fsm->state = t->next_state;
    }
}
