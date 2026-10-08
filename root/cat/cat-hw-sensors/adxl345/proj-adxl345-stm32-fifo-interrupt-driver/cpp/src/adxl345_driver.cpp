#include "adxl345_driver.hpp"

namespace adxl345 {

Adxl345Driver::Adxl345Driver(IBus& bus)
    : bus_(bus) {}

bool Adxl345Driver::write_register(uint8_t reg, uint8_t val) {
    BusGuard guard(bus_);
    return bus_.write_register(reg, val);
}

bool Adxl345Driver::read_registers(uint8_t reg, uint8_t* buffer, size_t len) {
    BusGuard guard(bus_);
    return bus_.read_registers(reg, buffer, len);
}

bool Adxl345Driver::init(Range range, bool full_res) {
    uint8_t dev_id = 0;
    if (!read_registers(Register::DEVID, &dev_id, 1) || dev_id != ADXL345_EXPECTED_DEVID) {
        return false; // Помилка зчитування або невірний ID пристрою
    }

    current_range_ = range;
    full_resolution_ = full_res;

    // Налаштування BW_RATE: 100 Гц вибірок (код 0x0A), звичайне живлення
    if (!write_register(Register::BW_RATE, 0x0A)) {
        return false;
    }

    // Налаштування DATA_FORMAT: діапазон + прапорець FULL_RES
    uint8_t data_format = static_cast<uint8_t>(range) & 0x03;
    if (full_res) {
        data_format |= Mask::DATA_FORMAT_FULL_RES;
    }
    if (!write_register(Register::DATA_FORMAT, data_format)) {
        return false;
    }

    // Переведення в режим вимірювання (POWER_CTL -> MEASURE = 1)
    if (!write_register(Register::POWER_CTL, Mask::POWER_CTL_MEASURE)) {
        return false;
    }

    return true;
}

bool Adxl345Driver::configure_fifo_watermark(uint8_t watermark_samples, uint8_t int_pin) {
    if (watermark_samples > 31) {
        watermark_samples = 31; // Максимальний розмір Watermark у FIFO ADXL345 — 31 вибірка
    }

    // Режим Stream: FIFO постійно заповнюється, переповнення витісняє старі дані
    uint8_t fifo_ctl = Mask::FIFO_MODE_STREAM | (watermark_samples & 0x1F);
    if (!write_register(Register::FIFO_CTL, fifo_ctl)) {
        return false;
    }

    // Налаштування маршрутизації переривань у INT_MAP (0 = INT1, 1 = INT2)
    uint8_t int_map = 0;
    if (int_pin == 2) {
        int_map |= Mask::INT_WATERMARK; // Маршрутизувати Watermark на вивід INT2
    }
    if (!write_register(Register::INT_MAP, int_map)) {
        return false;
    }

    // Дозволити переривання заповнення Watermark
    if (!write_register(Register::INT_ENABLE, Mask::INT_WATERMARK)) {
        return false;
    }

    return true;
}

bool Adxl345Driver::read_raw_accel(RawVector3& raw) {
    uint8_t buffer[6] = {0};
    if (!read_registers(Register::DATAX0, buffer, 6)) {
        return false;
    }

    // Формування 16-бітних значень зі старшого та молодшого байтів (Little-Endian)
    raw.x = static_cast<int16_t>((buffer[1] << 8) | buffer[0]);
    raw.y = static_cast<int16_t>((buffer[3] << 8) | buffer[2]);
    raw.z = static_cast<int16_t>((buffer[5] << 8) | buffer[4]);

    return true;
}

size_t Adxl345Driver::read_fifo_burst(RawVector3* out_buffer, size_t max_samples) {
    if (!out_buffer || max_samples == 0) {
        return 0;
    }

    // Перевірка кількості доступних елементів у FIFO_STATUS (біти 5:0)
    uint8_t fifo_status = 0;
    if (!read_registers(Register::FIFO_STATUS, &fifo_status, 1)) {
        return 0;
    }

    uint8_t entries_available = fifo_status & 0x3F;
    size_t samples_to_read = (entries_available < max_samples) ? entries_available : max_samples;

    size_t read_count = 0;
    for (size_t i = 0; i < samples_to_read; ++i) {
        if (read_raw_accel(out_buffer[i])) {
            read_count++;
        } else {
            break;
        }
    }

    return read_count;
}

void Adxl345Driver::set_watermark_callback(WatermarkCallback cb) {
    watermark_cb_ = cb;
}

void Adxl345Driver::handle_watermark_event() {
    if (watermark_cb_) {
        watermark_cb_();
    }
}

} // namespace adxl345
