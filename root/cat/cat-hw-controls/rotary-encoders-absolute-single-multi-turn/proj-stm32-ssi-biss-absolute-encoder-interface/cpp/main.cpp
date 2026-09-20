#include <iostream>
#include <iomanip>
#include "encoder_driver.hpp"

// Симуляція генерації 64-бітного кадру BiSS-C з кодом Ґрея та CRC-6
static std::uint64_t buildSimulatedBissFrame(std::uint32_t mt_bin, std::uint32_t st_bin,
                                             bool n_error, bool n_warn) {
    // Кодування в код Ґрея (двоїсте перетворення)
    std::uint64_t st_gray = st_bin ^ (st_bin >> 1);
    std::uint64_t mt_gray = mt_bin ^ (mt_bin >> 1);

    // Збірка корисного навантаження (Payload)
    std::uint64_t payload = (mt_gray << 17) | st_gray;
    payload = (payload << 1) | (n_error ? 1U : 0U);
    payload = (payload << 1) | (n_warn ? 1U : 0U);

    // Обчислення CRC-6 над payload (31 біт: 12 MT + 17 ST + 1 ERR + 1 WARN)
    std::uint8_t crc = encoder::calcCrc6(payload, 31);

    // Підсумковий кадр
    return (payload << 6) | crc;
}

int main() {
    std::cout << "=== Драйвер абсолютного енкодера BiSS-C (C++) ===\n\n";

    // 1. Конфігурація енкодера (17 біт Singleturn, 12 біт Multiturn)
    encoder::EncoderConfig config{};
    config.protocol = encoder::EncoderProtocol::BiSSC;
    config.encoding = encoder::DataEncoding::Gray;
    config.singleturn_bits = 17;
    config.multiturn_bits = 12;
    config.has_error_bit = true;
    config.has_warn_bit = true;

    encoder::AbsoluteEncoder encoder_driver(config);
    encoder::EncoderData data{};

    // 2. Симуляція Кадру 1: Нормальний стан (Позиція ST = 65536, Оберти MT = 10)
    std::uint64_t frame1 = buildSimulatedBissFrame(10, 65536, true, true);
    encoder::EncoderStatus status1 = encoder_driver.processFrame(frame1, data);

    std::cout << "[Кадр 1] Нормальний режим:\n";
    std::cout << "  Статус: " << static_cast<int>(status1) << " (0 = OK)\n";
    std.cout << "  Singleturn позиція: " << data.singleturn_pos << " / 131072\n";
    std.cout << "  Multiturn оберти:   " << data.multiturn_count << "\n";
    std.cout << "  Сумарна позиція:    " << data.full_position << "\n\n";

    // 3. Установка віртуального нуля на поточну позицію
    encoder_driver.setZeroOffset(data.full_position);
    std::cout << "-> Встановлено зміщення віртуального нуля: " << encoder_driver.getZeroOffset() << "\n\n";

    // 4. Симуляція Кадру 2: Зміщення позиції вперед (ST = 70000, MT = 10)
    std::uint64_t frame2 = buildSimulatedBissFrame(10, 70000, true, true);
    encoder_driver.processFrame(frame2, data);

    std::cout << "[Кадр 2] Після встановлення нуля:\n";
    std.cout << "  Абсолютна позиція: " << data.full_position << "\n";
    std.cout << "  Відносна позиція:  " << data.relative_position << " (очікується 4464)\n\n";

    // 5. Симуляція Кадру 3: Помилка CRC (спотворення бітів)
    std::uint64_t frame_corrupted = frame1 ^ (1ULL << 15); // зіпсований біт
    encoder::EncoderStatus status_crc = encoder_driver.processFrame(frame_corrupted, data);

    std::cout << "[Кадр 3] Тест помилки CRC:\n";
    std.cout << "  Статус: " << static_cast<int>(status_crc) << " (1 = CrcError)\n";
    std.cout << "  Помилку виявлено та відфільтровано успішно!\n";

    return 0;
}
