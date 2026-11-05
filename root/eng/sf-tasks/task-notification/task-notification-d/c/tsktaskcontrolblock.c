typedef struct tskTaskControlBlock
{
    volatile StackType_t *pxTopOfStack; /* Покажчик на верхівку стека задачі */
    ListItem_t xStateListItem;           /* Елемент списку станів (Ready, Blocked, Suspended) */
    ListItem_t xEventListItem;           /* Елемент списку подій */
    UBaseType_t uxPriority;              /* Пріоритет задачі */
    StackType_t *pxStack;                /* Покажчик на початок стека */

    #if ( configUSE_TASK_NOTIFICATIONS == 1 )
        volatile uint32_t ulNotifiedValue[ configTASK_NOTIFICATION_ARRAY_ENTRIES ];
        volatile uint8_t ucNotifyState[ configTASK_NOTIFICATION_ARRAY_ENTRIES ];
    #endif

    /* Інші системні поля TCB */
} tskTCB;
