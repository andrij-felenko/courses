static int idx = 0;   // поточний рядок таблиці

// Вічний цикл живе у власній задачі FreeRTOS — решта системи вільна.
static void motor_task(void *arg) {
  for (;;) {
    apply_step(idx);              // виставити обмотки
    idx = (idx + 1) % 8;          // наступний рядок; по колу через % 8
    vTaskDelay(pdMS_TO_TICKS(2)); // 2 мс — потрібен тік 1 кГц
  }                               // (CONFIG_FREERTOS_HZ=1000, інакше вийде 0)
}

// у кінці app_main():
// xTaskCreate(motor_task, "motor", 2048, NULL, 5, NULL);
