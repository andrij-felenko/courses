#define BLOCKED 1                 // ← що показав калібратор на ЦІЙ платі

// «зубець зайшов у щілину» — це перехід у стан BLOCKED:
//   BLOCKED==1 → POSEDGE; BLOCKED==0 → NEGEDGE.
#define EDGE (BLOCKED ? GPIO_INTR_POSEDGE : GPIO_INTR_NEGEDGE)

gpio_config_t cfg = {
  .pin_bit_mask = 1ULL << PIN_S,
  .mode         = GPIO_MODE_INPUT,
  .intr_type    = EDGE,
};
ESP_ERROR_CHECK(gpio_config(&cfg));
// фронт можна перезадати й потім, не переписуючи весь конфіг:
ESP_ERROR_CHECK(gpio_set_intr_type(PIN_S, EDGE));
