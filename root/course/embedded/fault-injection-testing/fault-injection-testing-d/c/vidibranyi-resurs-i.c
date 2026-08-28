void worker_task(void *arg) {
    esp_task_wdt_add(NULL);              // підписали задачу під сторожа

    for (;;) {
        esp_task_wdt_reset();            // «я жива» — годуємо сторожа

#ifdef FAULT_INJECTION
        if (fault_active(FAULT_TASK_HANG)) {
            // вкидаємо несправність: задача застрягла й більше не годує сторожа
            while (1) { /* нічого — імітуємо заклинення */ }
        }
#endif
        do_work();
        vTaskDelay(pdMS_TO_TICKS(100));
    }
}
