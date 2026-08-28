// Скласти кадр. Аргументи полів ідуть у порядку ОПИСУ, не кадру.
uint16_t mavlink_msg_perimeter_beacon_status_pack(
        uint8_t system_id, uint8_t component_id, mavlink_message_t *msg,
        uint16_t beacon_id, float range_m, uint8_t quality, uint64_t time_usec,
        uint8_t target_system, uint8_t target_component, float bearing_deg);

// Те саме, але номер послідовності береться зі стану каналу chan.
uint16_t mavlink_msg_perimeter_beacon_status_pack_chan(
        uint8_t system_id, uint8_t component_id, uint8_t chan,
        mavlink_message_t *msg, /* ...ті самі поля... */);

// Те саме, але стан кодувальника передано явно, без глобальної таблиці каналів.
uint16_t mavlink_msg_perimeter_beacon_status_pack_status(
        uint8_t system_id, uint8_t component_id, mavlink_status_t *_status,
        mavlink_message_t *msg, /* ...ті самі поля... */);

// Три обгортки, що беруть готову структуру замість переліку полів.
uint16_t mavlink_msg_perimeter_beacon_status_encode(
        uint8_t system_id, uint8_t component_id, mavlink_message_t *msg,
        const mavlink_perimeter_beacon_status_t *st);
uint16_t mavlink_msg_perimeter_beacon_status_encode_chan(
        uint8_t system_id, uint8_t component_id, uint8_t chan,
        mavlink_message_t *msg, const mavlink_perimeter_beacon_status_t *st);
uint16_t mavlink_msg_perimeter_beacon_status_encode_status(
        uint8_t system_id, uint8_t component_id, mavlink_status_t *_status,
        mavlink_message_t *msg, const mavlink_perimeter_beacon_status_t *st);

// Розібрати кадр у структуру. Нічого не повертає — кадр уже перевірено сумою.
void mavlink_msg_perimeter_beacon_status_decode(
        const mavlink_message_t *msg, mavlink_perimeter_beacon_status_t *st);

// Геттер на кожне поле — читає просто з навантаження, без розбору цілого.
uint64_t mavlink_msg_perimeter_beacon_status_get_time_usec(const mavlink_message_t *msg);
float    mavlink_msg_perimeter_beacon_status_get_bearing_deg(const mavlink_message_t *msg);
