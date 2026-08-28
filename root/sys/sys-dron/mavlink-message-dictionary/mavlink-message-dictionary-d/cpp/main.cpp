#include <iostream>
#include <array>
#include <span>
#include <cstdint>
#include <cstring>

// Підключення згенерованих заголовків MAVLink v2 для діалекту common
#include <common/mavlink.h>

// Приклад ідіоматичного пакування та відправки телеметрії навігації
void send_navigation_telemetry(uint8_t sys_id, uint8_t comp_id) {
    mavlink_message_t msg{};
    std::array<uint8_t, MAVLINK_MAX_PACKET_LEN> buffer{};

    // Заповнення структури повідомлення GLOBAL_POSITION_INT (#33)
    mavlink_global_position_int_t pos{};
    pos.time_boot_ms = 125400;          // 125.4 секунди від старту
    pos.lat = 504501000;                // 50.4501000 градусів широти (x 1e7)
    pos.lon = 305234000;                // 30.5234000 градусів довготи (x 1e7)
    pos.alt = 185200;                   // 185.2 м над рівнем моря (в мм)
    pos.relative_alt = 45500;           // 45.5 м над точкою зльоту (в мм)
    pos.vx = 450;                       // 4.5 м/с на північ (у см/с)
    pos.vy = -120;                      // 1.2 м/с на захід (у см/с)
    pos.vz = -50;                       // 0.5 м/с набір висоти (Down = -50 см/с)
    pos.hdg = 18050;                    // Курс 180.50 градусів (cdeg)

    // Пакування повідомлення в канонічний кадр MAVLink v2
    const uint16_t len = mavlink_msg_global_position_int_encode(
        sys_id, comp_id, &msg, &pos
    );

    // Серіалізація кадру в двійковий буфер для передачі через UART/Socket
    const uint16_t bytes_to_send = mavlink_msg_to_send_buffer(buffer.data(), &msg);

    std::span<const uint8_t> wire_bytes{buffer.data(), bytes_to_send};
    std::cout << "[C++] Згенеровано кадр MAVLink ID=" << static_cast<int>(msg.msgid)
              << ", довжина на дроті=" << wire_bytes.size() << " байтів.\n";
}

// Приклад розбору вхідного байтового потоку
void parse_incoming_byte(uint8_t byte) {
    mavlink_message_t msg{};
    mavlink_status_t status{};

    // Потоковий парсер MAVLink з автоматичною перевіркою CRC та CRC_EXTRA
    if (mavlink_parse_char(MAVLINK_COMM_0, byte, &msg, &status) == MAVLINK_FRAMING_OK) {
        if (msg.msgid == MAVLINK_MSG_ID_GLOBAL_POSITION_INT) {
            mavlink_global_position_int_t decoded_pos{};
            mavlink_msg_global_position_int_decode(&msg, &decoded_pos);

            const double lat_deg = static_cast<double>(decoded_pos.lat) / 1e7;
            const double lon_deg = static_cast<double>(decoded_pos.lon) / 1e7;
            const double alt_m = static_cast<double>(decoded_pos.relative_alt) / 1000.0;

            std::cout << "[C++] Отримано координати: широта=" << lat_deg
                      << "°, довгота=" << lon_deg << "°, висота=" << alt_m << " м.\n";
        }
    }
}
