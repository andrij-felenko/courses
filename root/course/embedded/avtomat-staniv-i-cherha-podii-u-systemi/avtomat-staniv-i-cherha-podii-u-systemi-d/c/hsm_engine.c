// hsm_engine.c — Ядро диспетчеризації та обчислення LCA на C
#include "hsm_engine.h"

static const event_t pkg_entry = { Q_SIG_ENTRY, 0 };
static const event_t pkg_exit  = { Q_SIG_EXIT, 0 };
static const event_t pkg_init  = { Q_SIG_INIT, 0 };
static const event_t pkg_empty = { Q_SIG_EMPTY, 0 };

q_result_t hsm_top_state(hsm_t *me, const event_t *e) {
    (void)me;
    (void)e;
    return Q_RET_IGNORED;
}

void hsm_init(hsm_t *me, state_handler_t initial) {
    me->temp = initial;
    (*me->temp)(me, &pkg_init);
    me->state = me->temp;
    (*me->state)(me, &pkg_entry);
}

void hsm_dispatch(hsm_t *me, const event_t *e) {
    state_handler_t s = me->state;
    q_result_t res = Q_RET_SUPER;

    // 1. Спливання події від активного листка до вершини
    while (s != NULL && res == Q_RET_SUPER) {
        me->temp = NULL;
        res = (*s)(me, e);
        if (res == Q_RET_SUPER) {
            s = me->temp; // Перехід до батьківського суперстану
        }
    }

    // 2. Якщо стан повернув запит на перехід — виконуємо транзакцію LCA
    if (res == Q_RET_TRAN) {
        state_handler_t target = me->temp;
        state_handler_t src_path[MAX_STATE_DEPTH];
        state_handler_t dst_path[MAX_STATE_DEPTH];
        uint8_t src_depth = 0;
        uint8_t dst_depth = 0;

        // Побудова ланцюга предків джерела
        state_handler_t curr = me->state;
        while (curr != hsm_top_state && curr != NULL && src_depth < MAX_STATE_DEPTH) {
            src_path[src_depth++] = curr;
            me->temp = NULL;
            (*curr)(me, &pkg_empty);
            curr = me->temp;
        }

        // Побудова ланцюга предків цілі
        curr = target;
        while (curr != hsm_top_state && curr != NULL && dst_depth < MAX_STATE_DEPTH) {
            dst_path[dst_depth++] = curr;
            me->temp = NULL;
            (*curr)(me, &pkg_empty);
            curr = me->temp;
        }

        // Пошук найменшого спільного предка (LCA)
        int8_t lca_src = -1;
        int8_t lca_dst = -1;
        for (int8_t i = 0; i < src_depth; i++) {
            for (int8_t j = 0; j < dst_depth; j++) {
                if (src_path[i] == dst_path[j]) {
                    lca_src = i;
                    lca_dst = j;
                    break;
                }
            }
            if (lca_src >= 0) break;
        }

        // Виклик Exit-дій знизу вгору до знайденого LCA
        int8_t exit_limit = (lca_src >= 0) ? lca_src : src_depth;
        for (int8_t i = 0; i < exit_limit; i++) {
            (*src_path[i])(me, &pkg_exit);
        }

        // Виклик Entry-дій згори вниз від LCA до цільового стану
        int8_t entry_start = (lca_dst >= 0) ? (lca_dst - 1) : (dst_depth - 1);
        for (int8_t j = entry_start; j >= 0; j--) {
            (*dst_path[j])(me, &pkg_entry);
        }

        me->state = target;

        // Виконання початкового переходу цільового стану
        me->temp = NULL;
        if ((*me->state)(me, &pkg_init) == Q_RET_TRAN) {
            state_handler_t leaf = me->temp;
            (*leaf)(me, &pkg_entry);
            me->state = leaf;
        }
    }
}
