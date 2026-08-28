static void on_valve_command(const mqtt_message_t *msg, void *user_ctx) {
    (void)user_ctx;
    if (msg->token_count < 1) return;

    const mqtt_token_t *valve_token = &msg->tokens[0];
    /* Обробка команди без модифікації рядка */
    if (valve_token->len == 7 && memcmp(valve_token->ptr, "valve01", 7) == 0) {
        if (msg->payload_len == 4 && memcmp(msg->payload, "OPEN", 4) == 0) {
            /* Відкриття апаратного клапана */
        }
    }
}

static void on_config_update(const mqtt_message_t *msg, void *user_ctx) {
    (void)user_ctx;
    /* msg->tokens[0] містить залишок шляху конфігурації після '#' */
}

void app_mqtt_setup(mqtt_router_t *router) {
    mqtt_router_init(router);
    mqtt_router_add(router, "agro-corp/site-01/node-42/cmd/+", on_valve_command, NULL);
    mqtt_router_add(router, "agro-corp/site-01/node-42/config/#", on_config_update, NULL);
}
