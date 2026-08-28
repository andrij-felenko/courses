#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

/* Визначення адрес фізичних банків пам'яті */
#define SRAM1_START_ADDR    ( ( uint8_t * ) 0x20000000UL )
#define SRAM1_SIZE_BYTES    ( 64 * 1024 )

#define SRAM2_START_ADDR    ( ( uint8_t * ) 0x20040000UL )
#define SRAM2_SIZE_BYTES    ( 128 * 1024 )

#define EXT_RAM_START_ADDR  ( ( uint8_t * ) 0x60000000UL )
#define EXT_RAM_SIZE_BYTES  ( 4 * 1024 * 1024 )

/* Масив дескрипторів регіонів */
const HeapRegion_t xHeapRegions[] =
{
    { SRAM1_START_ADDR,   SRAM1_SIZE_BYTES },
    { SRAM2_START_ADDR,   SRAM2_SIZE_BYTES },
    { EXT_RAM_START_ADDR, EXT_RAM_SIZE_BYTES },
    { NULL,               0 } /* Обов'язковий кінцевий сентинел */
};

void system_memory_init( void )
{
    /* Ініціалізація пулу heap_5 перед запуском ядра */
    vPortDefineHeapRegions( xHeapRegions );
}
