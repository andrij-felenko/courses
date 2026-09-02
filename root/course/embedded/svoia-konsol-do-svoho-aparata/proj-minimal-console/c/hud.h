#ifndef HUD_H
#define HUD_H

#include <stdbool.h>
#include <stdint.h>

#include "link.h"
#include "power.h"

typedef struct {
    uint16_t     pack_mv;        // акумулятор самого пульта
    batt_level_t batt_level;
    uint8_t      link_pct;       // якість зворотного каналу за нашим підрахунком
    uint16_t     lost_frames;
    bool         armed;
    uint8_t      safety_faults;
    telemetry_t  air;
} hud_state_t;

void hud_set_state(const hud_state_t *state);
void hud_service(void);   // рендерить і віддає рівно одну сторінку за виклик

#endif
