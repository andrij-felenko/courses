#include "stm32f4xx_hal.h"
#include <stdio.h>
#include <stdbool.h>

// антидеренч однієї клавіші на «таймері краю»:
#define DEBOUNCE_MS 20

static bool     last_raw = false;  // сирий стан минулого разу
static bool     stable   = false;  // стан, якому вже віримо
static uint32_t t_edge   = 0;      // коли рівень востаннє смикнувся
static bool     reported = false;  // чи вже повідомили про це натискання

// raw — сирий результат сканування цієї клавіші (true = замкнено)
void debounce_key(bool raw) {
    uint32_t now = HAL_GetTick();      // мілісекунди від старту (тик SysTick)
    if (raw != last_raw) {             // рівень щойно змінився — перезапустити відлік
        t_edge = now;
        last_raw = raw;
    }
    if (now - t_edge >= DEBOUNCE_MS) { // протримався досить довго — вірити
        stable = raw;
    }
    if (stable && !reported) {         // стійке замикання, ще не повідомляли
        printf("натиск (свій антидеренч)\n");
        reported = true;               // одна подія на натискання
    }
    if (!stable) reported = false;     // клавіша відпустилась — готові до нового
}
