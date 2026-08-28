#include "sensor_driver.hpp"

namespace driver {

template <BusTransport Transport>
uint8_t SensorDevice<Transport>::compute_crc8(std::span<const uint8_t> data) noexcept {
    constexpr uint8_t POLYNOMIAL = 0x31;
    uint8_t crc = 0xFF;
    for (uint8_t byte : data) {
        crc ^= byte;
        for (uint8_t bit = 0; bit < 8; ++bit) {
            if ((crc & 0x80) != 0) {
                crc = static_cast<uint8_t>((crc << 1) ^ POLYNOMIAL);
            } else {
                crc = static_cast<uint8_t>(crc << 1);
            }
        }
    }
    return crc;
}

template <BusTransport Transport>
Status SensorDevice<Transport>::init() noexcept {
    uint8_t id = 0;
    std::span<uint8_t> rx_span(&id, 1);
    Status status = m_bus.read(REG_CHIP_ID, rx_span);
    if (status != Status::Ok) {
        m_bus.recover();
        m_state = State::Error;
        return Status::BusIo;
    }

    if (id != EXPECTED_CHIP_ID) {
        m_state = State::Error;
        return Status::ChipIdMismatch;
    }

    m_state = State::Idle;
    return Status::Ok;
}

template <BusTransport Transport>
Status SensorDevice<Transport>::start_measurement() noexcept {
    if (m_state != State::Idle && m_state != State::DataReady) {
        return Status::InvalidState;
    }

    const uint8_t cmd = 0xB6;
    const std::span<const uint8_t> tx_span(&cmd, 1);
    Status status = m_bus.write(REG_MEAS_START, tx_span);
    if (status != Status::Ok) {
        m_state = State::Error;
        return Status::BusIo;
    }

    m_conv_start_us = m_bus.get_time_us();
    m_state = State::Converting;
    return Status::Ok;
}

template <BusTransport Transport>
std::expected<SensorData, Status> SensorDevice<Transport>::poll() noexcept {
    if (m_state != State::Converting) {
        return std::unexpected(Status::InvalidState);
    }

    const uint32_t now = m_bus.get_time_us();
    if ((now - m_conv_start_us) < CONV_DURATION_US) {
        return std::unexpected(Status::NotReady);
    }

    std::span<uint8_t> rx_span(m_raw_buf);
    Status status = m_bus.read(REG_DATA_BURST, rx_span);
    if (status != Status::Ok) {
        m_state = State::Error;
        return std::unexpected(Status::BusIo);
    }

    /* Перевірка CRC температури (перші 2 байти) */
    if (compute_crc8(rx_span.subspan(0, 2)) != m_raw_buf[2]) {
        m_state = State::Error;
        return std::unexpected(Status::CrcMismatch);
    }

    /* Перевірка CRC тиску (байти 3 і 4) */
    if (compute_crc8(rx_span.subspan(3, 2)) != m_raw_buf[5]) {
        m_state = State::Error;
        return std::unexpected(Status::CrcMismatch);
    }

    SensorData data{};
    const auto raw_temp = static_cast<int16_t>(
        (static_cast<uint16_t>(m_raw_buf[0]) << 8) | m_raw_buf[1]
    );
    data.temperature_mdeg_c = static_cast<int32_t>(
        -45000 + (static_cast<int64_t>(raw_temp) * 175000) / 65535
    );

    const auto raw_press = static_cast<uint16_t>(
        (static_cast<uint16_t>(m_raw_buf[3]) << 8) | m_raw_buf[4]
    );
    data.pressure_pa = static_cast<uint32_t>(
        30000 + (static_cast<uint64_t>(raw_press) * 80000) / 65535
    );
    data.timestamp_us = now;

    m_state = State::DataReady;
    return data;
}

template <BusTransport Transport>
void SensorDevice<Transport>::reset_fsm() noexcept {
    m_state = State::Idle;
    m_conv_start_us = 0;
}

template <BusTransport Transport>
Status SensorDevice<Transport>::recover_bus() noexcept {
    return m_bus.recover();
}

} // namespace driver
