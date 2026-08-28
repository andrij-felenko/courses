/* Ініціалізація внутрішніх структур арбітра та черг пріоритетів */
int arbiter_init(const arbiter_config_t *config);

/* Реєстрація фізичного носія у пулі доступних інтерфейсів */
int arbiter_register_bearer(bearer_interface_t *bearer);

/* Маршрутизація та відправка пакета з урахуванням поточного активного каналу та QoS */
int arbiter_transmit(const uint8_t *payload, size_t len, qos_priority_t prio);

/* Регулярний крок автомата станів: перевірка таймаутів, оновлення PER та гістерезису */
void arbiter_tick(uint32_t current_mono_ms);

/* Отримання поточної діагностики стану диспетчера */
arbiter_state_t arbiter_get_state(void);
bearer_id_t     arbiter_get_active_bearer(void);

/* Реєстрація функції зворотного виклику при зміні активного носія */
typedef void (*on_bearer_switched_cb_t)(bearer_id_t prev_bearer, bearer_id_t new_bearer, arbiter_state_t state);
void arbiter_set_switch_callback(on_bearer_switched_cb_t cb);

/* Реєстрація функції зворотного виклику при переході в аварійну автономію (Failsafe) */
typedef void (*on_emergency_autonomy_cb_t)(uint32_t silent_duration_ms);
void arbiter_set_autonomy_callback(on_emergency_autonomy_cb_t cb);
