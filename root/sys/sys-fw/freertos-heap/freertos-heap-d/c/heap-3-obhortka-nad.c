#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

void *pvPortMalloc( size_t xWantedSize )
{
    void *pvReturn;

    /* Призупиняємо планувальник: перемикання задач заблоковано */
    vTaskSuspendAll();
    {
        pvReturn = malloc( xWantedSize );
    }
    /* Відновлюємо планувальник */
    ( void ) xTaskResumeAll();

    return pvReturn;
}

void vPortFree( void *pv )
{
    if( pv != NULL )
    {
        vTaskSuspendAll();
        {
            free( pv );
        }
        ( void ) xTaskResumeAll();
    }
}
