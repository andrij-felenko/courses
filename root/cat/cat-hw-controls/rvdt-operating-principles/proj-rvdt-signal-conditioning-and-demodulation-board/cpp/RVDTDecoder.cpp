#include "RVDTDecoder.hpp"

namespace hw_controls {

constexpr float PI_F = 3.14159265358979323846f;

bool RVDTDecoder::init() {
    // 1. Початковий скид ліній стробування та вибору пристрою
    bus_.set_cs(false);
    bus_.set_sample(false);
    bus_.delay_us(10);
    bus_.set_cs(true);
    bus_.set_sample(true);
    bus_.delay_us(100);

    // 2. Встановлення режиму конфігурації регістрів (A0 = 1, A1 = 1)
    bus_.set_mode_lines(true, true);

    // 3. Запис у CONTROL регістр (Адреса 0x80)
    // Формат байта CONTROL: [1(REG)] [RES1] [RES0] [FREQ4] [FREQ3] [FREQ2] [FREQ1] [EN_PH]
    uint8_t control_byte = 0x80; // Біт 7 = 1 для запису в регістр
    control_byte |= (static_cast<uint8_t>(config_.resolution) & 0x03) << 4;
    control_byte |= (static_cast<uint8_t>(config_.excitation_freq) & 0x0F) << 1;

    bus_.set_cs(false);
    bus_.transfer_byte(0x80); // Адреса CONTROL регістра
    bus_.transfer_byte(control_byte); // Дані конфігурації
    bus_.set_cs(true);
    bus_.delay_us(20);

    // 4. Очищення початкових прапорців аварій
    reset_fault_latch();

    initialized_ = true;
    return true;
}

uint16_t RVDTDecoder::get_max_code_for_resolution() const {
    switch (config_.resolution) {
    case Resolution::Bits10: return 1023;
    case Resolution::Bits12: return 4095;
    case Resolution::Bits14: return 16383;
    case Resolution::Bits16: return 65535;
    }
    return 65535;
}

bool RVDTDecoder::check_parity(uint16_t raw_word) const {
    // Проста перевірка непарності (Odd Parity) для 16-бітного слова
    uint16_t temp = raw_word;
    temp ^= temp >> 8;
    temp ^= temp >> 4;
    temp ^= temp >> 2;
    temp ^= temp >> 1;
    return (temp & 0x01) != 0;
}

std::optional<RVDTMeasurement> RVDTDecoder::read_position() {
    if (!initialized_) {
        if (!init()) {
            return std::nullopt;
        }
    }

    RVDTMeasurement meas{};

    // 1. Подача від'ємного імпульсу SAMPLE для фіксації поточного кута у RDC
    bus_.set_sample(false);
    bus_.delay_us(2); // Витримка часу фіксації t_SAMPLE >= 1.5 мкс

    // 2. Налаштування режимних ліній на вибірку даних позиції (A0 = 0, A1 = 0)
    bus_.set_mode_lines(false, false);

    // 3. Зчитування 2-байтного каду по шині SPI
    bus_.set_cs(false);
    uint8_t msb = bus_.transfer_byte(0x00);
    uint8_t lsb = bus_.transfer_byte(0x00);
    bus_.set_cs(true);

    // Відпускаємо лінію SAMPLE для відновлення відстеження
    bus_.set_sample(true);

    uint16_t raw_word = (static_cast<uint16_t>(msb) << 8) | lsb;
    meas.raw_code = raw_word;

    // 4. Перевірка цілісності даних (паритет)
    meas.faults = read_faults();
    if (meas.faults.any_fault) {
        meas.valid = false;
        return meas;
    }

    // 5. Ратіометричний перерахунок у кут повороту
    const uint16_t max_code = get_max_code_for_resolution();
    const float normalized_ratio = static_cast<float>(raw_word) / static_cast<float>(max_code);

    // Центруємо відносно нуля: діапазон [-0.5, +0.5]
    const float centered_ratio = normalized_ratio - 0.5f;

    // Масштабування у кут у градусах та радіанах
    meas.angle_deg = centered_ratio * config_.full_scale_angle_deg * config_.ratiometric_gain;
    meas.angle_rad = meas.angle_deg * (PI_F / 180.0f);
    meas.valid = true;

    return meas;
}

FaultFlags RVDTDecoder::read_faults() {
    FaultFlags flags{};

    // Режим читання регістра помилок (A0 = 1, A1 = 1)
    bus_.set_mode_lines(true, true);
    bus_.set_cs(false);
    
    // Передаємо команду читання регістра FAULT (0xFF)
    bus_.transfer_byte(0xFF);
    uint8_t fault_byte = bus_.transfer_byte(0x00);
    bus_.set_cs(true);

    // Розбір апаратних бітів реєстра FAULT (AD2S1210 / RDC)
    // Біт 7: LOT (Loss of Tracking), Біт 6: DOS (Degradation of Signal), Біт 5: LOS (Loss of Signal)
    flags.loss_of_tracking     = (fault_byte & (1 << 7)) != 0;
    flags.degradation_of_signal = (fault_byte & (1 << 6)) != 0;
    flags.loss_of_signal       = (fault_byte & (1 << 5)) != 0;

    flags.any_fault = flags.loss_of_tracking || flags.degradation_of_signal || flags.loss_of_signal;
    return flags;
}

bool RVDTDecoder::reset_fault_latch() {
    // Цикл перезапуску засувок помилок: короткий імпульс SAMPLE при A0=1, A1=1
    bus_.set_mode_lines(true, true);
    bus_.set_sample(false);
    bus_.delay_us(10);
    bus_.set_sample(true);
    bus_.delay_us(10);
    return true;
}

} // namespace hw_controls
