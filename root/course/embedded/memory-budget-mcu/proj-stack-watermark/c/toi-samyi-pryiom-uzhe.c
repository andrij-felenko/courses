// Періодична діагностика: пройти всі задачі й показати запас стека кожної.
void stacks_report(void) {
    UBaseType_t n = uxTaskGetNumberOfTasks();
    TaskStatus_t *arr = pvPortMalloc(n * sizeof(TaskStatus_t));
    if (arr == NULL) return;

    n = uxTaskGetSystemState(arr, n, NULL);
    for (UBaseType_t i = 0; i < n; ++i) {
        // у TaskStatus_t water-mark теж у СЛОВАХ
        size_t free_b = (size_t)arr[i].usStackHighWaterMark * sizeof(StackType_t);
        printf("%-16s запас стека: %u Б\n", arr[i].pcTaskName, (unsigned)free_b);
        if (free_b < 256) {
            printf("   !!! %s близько до переповнення\n", arr[i].pcTaskName);
        }
    }
    pvPortFree(arr);
}
