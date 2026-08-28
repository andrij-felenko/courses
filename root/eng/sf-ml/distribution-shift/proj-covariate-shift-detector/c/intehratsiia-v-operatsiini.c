/* Приклад архітектури взаємодії задач у FreeRTOS на C99 */
static ShiftDetector g_detector;
static StaticQueue_t g_static_queue;
static uint8_t g_queue_storage[sizeof(float) * SHIFT_MAX_DIM * 8];
static QueueHandle_t g_sample_queue;

void vControlLoopTask(void *pvParameters) {
    float current_features[SHIFT_MAX_DIM];
    for (;;) {
        read_sensors_and_run_inference(current_features);
        xQueueSend(g_sample_queue, current_features, 0);
        execute_actuator_commands();
        vTaskDelay(pdMS_TO_TICKS(2));
    }
}

void vShiftMonitorTask(void *pvParameters) {
    float incoming_sample[SHIFT_MAX_DIM];
    ShiftDiagnosticReport report;
    for (;;) {
        if (xQueueReceive(g_sample_queue, incoming_sample, portMAX_DELAY) == pdTRUE) {
            shift_detector_push_sample(&g_detector, incoming_sample);
            if (shift_detector_evaluate(&g_detector, &report) == SHIFT_ERR_OK) {
                if (report.safety_status == SHIFT_STATUS_CRITICAL) {
                    safety_supervisor_trigger_failsafe(report.mmd_squared);
                }
            }
        }
    }
}
