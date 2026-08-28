#define PIN_S    GPIO_NUM_4
#define N_SLOTS  20
#define GUARD_US 800
static const char *TAG = "ky010";

static volatile int64_t lastEdge = 0;
static QueueHandle_t    q;            // ISR → задача: свіжий вимір періоду

static void IRAM_ATTR on_edge(void *arg) {
  int64_t  t  = esp_timer_get_time();
  uint32_t dt = (uint32_t)(t - lastEdge);   // проміжок від попереднього фронту
  if (dt >= GUARD_US) {               // мертвий час: відкидаємо дрижання
    lastEdge = t;
    BaseType_t woken = pdFALSE;
    xQueueSendFromISR(q, &dt, &woken);      // ← ось воно, T у мікросекундах
    if (woken) portYIELD_FROM_ISR();
  }
}

void app_main(void) {
  q = xQueueCreate(4, sizeof(uint32_t));
  gpio_config_t cfg = { .pin_bit_mask = 1ULL << PIN_S,
                        .mode      = GPIO_MODE_INPUT,
                        .intr_type = GPIO_INTR_POSEDGE };
  ESP_ERROR_CHECK(gpio_config(&cfg));
  ESP_ERROR_CHECK(gpio_install_isr_service(0));
  ESP_ERROR_CHECK(gpio_isr_handler_add(PIN_S, on_edge, NULL));

  uint32_t T;
  while (1) {
    xQueueReceive(q, &T, portMAX_DELAY);    // задача спить, поки нема виміру
    // об/хв = 60 000 000 / (N · T);  60e6 бо T у мкс
    ESP_LOGI(TAG, "миттєво: %.0f об/хв", 60e6f / (N_SLOTS * (float)T));
  }
}
