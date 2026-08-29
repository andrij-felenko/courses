#ifndef EVSE_H
#define EVSE_H

#include <stdbool.h>
#include <stdint.h>

#include "evse_events.h"

typedef struct evse_s evse_t;

/*
 * Патерн «покажчик на функцію стану»: поточний стан — це функція, яка вміє
 * обробити подію. Службові EVT_ENTRY та EVT_EXIT рушій підсовує їй сам під час
 * переходу, тож дії входу й виходу лежать поруч із рештою логіки стану.
 */
typedef void (*evse_state_fn)(evse_t *me, const event_t *e);

struct evse_s {
    evse_state_fn state;
    bool          authorized;      /* картку прикладено й прийнято */
    bool          settling;        /* триває вікно перехідних процесів */
    uint32_t      card_id;         /* номер прийнятої картки */
    uint8_t       current_limit_a; /* дозволений струм, А */
    uint16_t      fault_code;      /* що саме зупинило станцію */
};

void evse_init(evse_t *me);
void evse_dispatch(evse_t *me, const event_t *e);

const char *evse_state_name(const evse_t *me);
const char *evse_fault_name(uint16_t fault_code);

extern evse_t g_evse;

#endif /* EVSE_H */
