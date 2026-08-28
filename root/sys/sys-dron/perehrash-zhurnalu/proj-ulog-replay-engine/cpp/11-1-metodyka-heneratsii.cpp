#include <iostream>
#include <fstream>
#include <cassert>
#include <filesystem>
#include <cstring>

static void generateSyntheticULogCpp(const std::string& filename) {
    std::ofstream out(filename, std::ios::binary);
    assert(out.is_open());

    // 1. Заголовок ULog (16 байтів)
    uint8_t header[16] = {
        0x55, 0x4C, 0x6F, 0x67, 0x01, 0x12, 0x35, 0x00,
        0x00, 0x00, 0x10, 0x00, 0x00, 0x00, 0x00, 0x00
    };
    out.write(reinterpret_cast<const char*>(header), 16);

    // 2. Схема формату
    std::string fmt = "sensor_combined:uint64_t timestamp;float[3] gyro_rad;float[3] accel_m_s2;";
    uint16_t fmt_len = static_cast<uint16_t>(fmt.size());
    uint8_t fmt_hdr[3] = { static_cast<uint8_t>(fmt_len & 0xFF), static_cast<uint8_t>(fmt_len >> 8), 'F' };
    out.write(reinterpret_cast<const char*>(fmt_hdr), 3);
    out.write(fmt.data(), fmt_len);

    // 3. Підписка
    std::string topic = "sensor_combined";
    std::vector<uint8_t> sub_payload;
    sub_payload.push_back(0); // multi_id
    sub_payload.push_back(1); // msg_id low
    sub_payload.push_back(0); // msg_id high
    sub_payload.insert(sub_payload.end(), topic.begin(), topic.end());
    uint16_t sub_len = static_cast<uint16_t>(sub_payload.size());
    uint8_t sub_hdr[3] = { static_cast<uint8_t>(sub_len & 0xFF), static_cast<uint8_t>(sub_len >> 8), 'A' };
    out.write(reinterpret_cast<const char*>(sub_hdr), 3);
    out.write(reinterpret_cast<const char*>(sub_payload.data()), sub_len);

    // 4. Повідомлення даних з немонотонними мітками часу
    uint64_t timestamps[4] = { 1048600, 1048580, 1048650, 1048620 };
    for (uint64_t ts : timestamps) {
        std::vector<uint8_t> data(34, 0);
        data[0] = 1; // msg_id low
        data[1] = 0; // msg_id high
        std::memcpy(&data[2], &ts, sizeof(uint64_t));

        uint16_t d_len = static_cast<uint16_t>(data.size());
        uint8_t d_hdr[3] = { static_cast<uint8_t>(d_len & 0xFF), static_cast<uint8_t>(d_len >> 8), 'D' };
        out.write(reinterpret_cast<const char*>(d_hdr), 3);
        out.write(reinterpret_cast<const char*>(data.data()), d_len);
    }
}

int main() {
    const std::string test_file = "test_synthetic_flight_cpp.ulg";
    generateSyntheticULogCpp(test_file);

    uint64_t last_time = 0;
    size_t verified_count = 0;

    auto callback = [&](uint64_t t_sim, std::string_view topic, uint8_t instance, std::span<const uint8_t> payload) {
        (void)instance;
        (void)payload;
        std::cout << std::format("  [C++20 Тест] Топік: {}, t_sim = {} мкс\n", topic, t_sim);
        assert(t_sim >= last_time);
        last_time = t_sim;
        verified_count++;
    };

    ULogReplayEngineCpp engine(test_file, callback);
    engine.runReplay();

    assert(verified_count == 4);
    std::cout << "[C++20 Тест] Успішно! Порядок часу повністю відновлено.\n";

    std::filesystem::remove(test_file);
    return 0;
}
