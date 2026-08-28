// Замовити потік із заданою частотою: переклад Гц → інтервал(мкс) → команда.
// f_hz береться з бюджету швидкостей (щоб Σ Fᵢ·fᵢ ≤ C).
void request_stream(mavlink_conn_t *m, uint32_t msg_id, float f_hz)
{
    uint32_t interval_us = (uint32_t)(1000000.0f / f_hz);   // 25 Гц → 40000
    command_long_send(m, m->target_system, m->target_component,
                      MAV_CMD_SET_MESSAGE_INTERVAL,
                      0,                    // confirmation
                      (float)msg_id,        // param1: ЯКЕ повідомлення (за ID)
                      (float)interval_us,   // param2: інтервал, мкс
                      0, 0, 0, 0, 0);
    // ВАЖЛИВО: це команда — летить у COMMAND_LONG і мусить іти НАДІЙНО
    // (з повторами й розбором COMMAND_ACK), інакше замовлення може загубитись.
}

// Застосувати спланований бюджет одним викликом:
void apply_rate_budget(mavlink_conn_t *m)
{
    request_stream(m, MAVLINK_MSG_ID_ATTITUDE,            25.0f);  // 1000 Б/с
    request_stream(m, MAVLINK_MSG_ID_GLOBAL_POSITION_INT,  4.0f);  //  160 Б/с
    request_stream(m, MAVLINK_MSG_ID_HEARTBEAT,            1.0f);  //   21 Б/с
    // сума 1181 Б/с ≈ 30% каналу 4000 Б/с — запас на команди лишається
}
