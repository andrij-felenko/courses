typedef enum {
    RES_HANDLED,
    RES_IGNORED,
    RES_SUPER,
    RES_TRANSITION
} HsmResult;

struct Hsm;
typedef HsmResult (*StateHandler)(struct Hsm *me, const Event *ev);

typedef struct Hsm {
    StateHandler current_state;
    StateHandler next_state;
    void *user_context;
} Hsm;

void hsm_init(Hsm *me, StateHandler initial_state, void *user_context);
void hsm_dispatch(Hsm *me, const Event *ev);
void hsm_transition(Hsm *me, StateHandler target_state);
