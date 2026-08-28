static portTASK_FUNCTION(prvIdleTask, pvParameters)
{
    (void)pvParameters;

    for (;;)
    {
        // 1. Звільнення динамічної пам'яті видалених задач
        prvCheckTasksWaitingTermination();

        #if (configUSE_PREEMPTION == 1)
        {
            // 2. Кооперативна поступка часу задачам однакового пріоритету
            #if (configIDLE_SHOULD_YIELD == 1)
            {
                if (listCURRENT_LIST_LENGTH(&(pxReadyTasksLists[tskIDLE_PRIORITY])) > (UBaseType_t)1)
                {
                    taskYIELD();
                }
            }
            #endif
        }
        #endif

        #if (configUSE_IDLE_HOOK == 1)
        {
            // 3. Виклик користувацького зворотного виклику
            vApplicationIdleHook();
        }
        #endif

        #if (configUSE_TICKLESS_IDLE != 0)
        {
            // 4. Розрахунок інтервалу простою та безтиковий сон
            TickType_t xExpectedIdleTime = prvGetExpectedIdleTime();

            if (xExpectedIdleTime >= configEXPECTED_IDLE_TIME_BEFORE_SLEEP)
            {
                vTaskSuspendAll();
                {
                    if (prvGetExpectedIdleTime() >= configEXPECTED_IDLE_TIME_BEFORE_SLEEP)
                    {
                        portSUPPRESS_TICKS_AND_SLEEP(xExpectedIdleTime);
                    }
                }
                (void)xTaskResumeAll();
            }
        }
        #else
        {
            // 5. Звичайне низькорівневе очікування переривання
            portTASK_FUNCTION_ENTER_LOW_POWER_MODE(); // Типово виконує __WFI()
        }
        #endif
    }
}
