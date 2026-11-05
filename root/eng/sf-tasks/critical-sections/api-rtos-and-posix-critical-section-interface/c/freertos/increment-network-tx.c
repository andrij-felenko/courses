#include "FreeRTOS.h"
#include "task.h"
#include "semphr.h"

/* Глобальний спільний ресурс та лічильник */
typedef struct {
    uint32_t tx_packets;
    uint32_t rx_packets;
    uint32_t errors;
} network_stats_t;

static network_stats_t g_net_stats;

/* Безпечна модифікація статистики у контексті задачі RTOS */
void increment_network_tx(uint32_t bytes_sent) {
    /* Вхід у критичну секцію RTOS: блокування переривань до configMAX_SYSCALL_INTERRUPT_PRIORITY */
    taskENTER_CRITICAL();
    
    g_net_stats.tx_packets++;
    /* Вкладений виклик критичної секції перевіряє лічильник uxCriticalNesting */
    
    taskEXIT_CRITICAL();
}

/* Безпечна модифікація статистики з обробника апаратного переривання (ISR) */
void DMA1_Stream0_IRQHandler(void) {
    UBaseType_t saved_interrupt_status;
    
    /* Збереження стану регістра пріоритетів переривань */
    saved_interrupt_status = taskENTER_CRITICAL_FROM_ISR();
    
    g_net_stats.rx_packets++;
    
    /* Відновлення початкового стану регістрів переривань */
    taskEXIT_CRITICAL_FROM_ISR(saved_interrupt_status);
}
