// Невелика кільцева черга останніх міток фронтів — щоб зіставляти
// повідомлення з ПРАВИЛЬНИМ фронтом, навіть коли UART трохи відстав.
#define PPS_Q  4
static uint64_t edge_q[PPS_Q];
static uint32_t edge_q_idx[PPS_Q];      // індекс (pps_count) кожної збереженої мітки

// Викликати з головного циклу: перекласти нові фронти з ISR у чергу.
void pps_drain(void) {
    uint64_t st; uint32_t ix;
    while (pps_take(&st, &ix)) {
        uint32_t slot = ix % PPS_Q;
        edge_q[slot]     = st;
        edge_q_idx[slot] = ix;
    }
}

// Знайти в черзі мітку фронту з потрібним індексом; -1, якщо вже витиснена.
static int edge_lookup(uint32_t want_index, uint64_t *out) {
    uint32_t slot = want_index % PPS_Q;
    if (edge_q_idx[slot] == want_index) {
        *out = edge_q[slot];
        return 0;
    }
    return -1;                           // фронт "виїхав" з черги — розрив
}
