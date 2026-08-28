#include <mavlink.h>
#include <stdio.h>
#include <math.h>

void generate_and_send_high_latency(uint8_t system_id, uint8_t component_id) {
    mavlink_message_t msg;
    mavlink_high_latency2_t hl = {0};

    // 1. Заповнення системних полів
    hl.timestamp = 3600000; // 1 година польоту (мс)
    hl.type = MAV_TYPE_FIXED_WING;
    hl.autopilot = MAV_AUTOPILOT_PX4;
    hl.custom_mode = 3; // AUTO.MISSION

    // 2. Глобальні координати (Одеса: 46.482526° N, 30.723309° E)
    hl.latitude = (int32_t)round(46.482526 * 1e7);
    hl.longitude = (int32_t)round(30.723309 * 1e7);

    // 3. Навігаційні параметри
    hl.altitude = 450;        // 450 метрів AMSL
    hl.target_altitude = 500; // Ціль: 500 метрів
    hl.heading = (uint8_t)(round(124.0 / 2.0)); // Курс 124° -> значення 62
    hl.target_heading = (uint8_t)(round(130.0 / 2.0));
    hl.target_distance = (uint16_t)round(2450.0 / 10.0); // 2450 м -> 245 декаметрів
    hl.wp_num = 14;

    // 4. Швидкості та тяга
    hl.throttle = 65; // 65% газу
    hl.airspeed = (uint8_t)round(22.4 * 5.0);    // 22.4 м/с -> 112
    hl.airspeed_sp = (uint8_t)round(22.0 * 5.0); // 22.0 м/с -> 110
    hl.groundspeed = (uint8_t)round(24.8 * 5.0); // 24.8 м/с -> 124
    hl.climb_rate = (int8_t)round(1.2 * 10.0);   // +1.2 м/с -> 12 дм/с

    // 5. Живлення та сенсори
    hl.battery = 78; // 78% заряду
    hl.current_battery = (int16_t)round(18.5 * 10.0); // 18.5 А -> 185
    hl.temperature = 42;     // 42 °C всередині фюзеляжу
    hl.temperature_air = 14; // 14 °C за бортом

    // 6. Діагностична маска (все справно, GPS 3D Fix)
    hl.failure_flags = 0; // Немає відмов
    hl.failsafe = 0;

    // Кодування кадру MSG ID 235
    mavlink_msg_high_latency2_encode(system_id, component_id, &msg, &hl);

    // Пакування у двійковий масив для відправки в UART супутникового модема
    uint8_t send_buf[MAVLINK_MAX_PACKET_LEN];
    uint16_t bytes_to_send = mavlink_msg_to_send_buffer(send_buf, &msg);

    // bytes_to_send = 10 (Header) + 65 (Payload) + 2 (CRC) = 77 байтів
    printf("Сформовано кадр HIGH_LATENCY2. Розмір: %u байтів\n", bytes_to_send);
}
