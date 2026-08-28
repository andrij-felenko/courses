/* ============================================================================
 * Інтеграція з FreeRTOS на C99 через Direct-to-Task Notifications
 * ============================================================================ */
#include "driver_core.h"

/* Структура контексту синхронного очікування */
typedef struct {
    void* task_to_notify; /* TaskHandle_t */
    driver_status_t final_status;
    size_t transferred;
} rtos_sync_ctx_t;

static void rtos_sync_callback(driver_handle_t h, driver_status_t st, size_t bytes, void* user_data) {
    (void)h;
    rtos_sync_ctx_t* ctx = (rtos_sync_ctx_t*)user_data;
    ctx->final_status = st;
    ctx->transferred = bytes;

    /* На реальній FreeRTOS:
     * BaseType_t xHigherPriorityTaskWoken = pdFALSE;
     * vTaskNotifyGiveFromISR((TaskHandle_t)ctx->task_to_notify, &xHigherPriorityTaskWoken);
     * portYIELD_FROM_ISR(xHigherPriorityTaskWoken);
     */
}

driver_status_t driver_transfer_sync(driver_handle_t h, const driver_transaction_t* trans) {
    if (h == NULL || trans == NULL) return DRIVER_ERR_INVALID_PARAM;

    rtos_sync_ctx_t sync_ctx;
    /* sync_ctx.task_to_notify = xTaskGetCurrentTaskHandle(); */
    sync_ctx.final_status = DRIVER_ERR_TIMEOUT;
    sync_ctx.transferred = 0;

    driver_transaction_t local_trans = *trans;
    local_trans.callback = rtos_sync_callback;
    local_trans.user_data = &sync_ctx;

    driver_status_t st = driver_submit_async(h, &local_trans);
    if (st != DRIVER_OK) {
        return st;
    }

    /* На реальній FreeRTOS:
     * uint32_t timeout_ticks = pdMS_TO_TICKS(trans->timeout_us / 1000);
     * if (ulTaskNotifyTake(pdTRUE, timeout_ticks) == 0) {
     *     return DRIVER_ERR_TIMEOUT;
     * }
     */
    return sync_ctx.final_status;
}
