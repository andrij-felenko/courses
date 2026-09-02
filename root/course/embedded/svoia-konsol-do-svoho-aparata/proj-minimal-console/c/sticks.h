#ifndef STICKS_H
#define STICKS_H

#include <stdbool.h>
#include <stdint.h>

#include "hal.h"

#define AXIS_ROLL     0
#define AXIS_PITCH    1
#define AXIS_THROTTLE 2
#define AXIS_YAW      3

#define AXIS_CENTER 1024
#define AXIS_MAX    2047

// Причини блокування передачі, які знаходить перевірка безпеки.
#define SAFETY_THROTTLE_UP 0x01
#define SAFETY_ARM_ON      0x02
#define SAFETY_AXIS_DEAD   0x04

typedef struct {
    uint16_t min;
    uint16_t center;
    uint16_t max;
    uint16_t deadband;
    uint8_t  expo_pct;   // частка кубічної складової кривої, 0..100
    uint8_t  alpha;      // вага свіжого відліку в IIR, 1/256
    bool     unipolar;   // вісь без центра (газ)
} axis_cfg_t;

uint16_t sticks_process(uint8_t ch, uint16_t raw);
uint8_t  sticks_dead_axes(void);
uint8_t  sticks_safety_check(const uint16_t *scaled, uint16_t switches);
uint8_t  sticks_aux_update(uint16_t switches);

#endif
