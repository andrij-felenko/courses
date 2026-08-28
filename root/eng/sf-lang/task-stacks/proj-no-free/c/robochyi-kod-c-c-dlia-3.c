#include "freertos/FreeRTOS.h"
#include "freertos/portmacro.h"

static portMUX_TYPE pool_mux = portMUX_INITIALIZER_UNLOCKED;

void *pool_alloc_safe(void)
{
    void *blk;
    portENTER_CRITICAL(&pool_mux);
    blk = pool_alloc();
    portEXIT_CRITICAL(&pool_mux);
    return blk;
}

void pool_free_safe(void *p)
{
    portENTER_CRITICAL(&pool_mux);
    pool_free(p);
    portEXIT_CRITICAL(&pool_mux);
}

/* З обробника переривань (ISR) — варіанти ...FromISR():       */
/* portENTER_CRITICAL_ISR / portEXIT_CRITICAL_ISR(&pool_mux)  */
