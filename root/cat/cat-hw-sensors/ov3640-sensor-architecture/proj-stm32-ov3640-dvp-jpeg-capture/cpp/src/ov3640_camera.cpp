#include "ov3640_camera.hpp"
#include <iostream>

namespace camera {

constexpr size_t DMA_BUFFER_CHUNK_SIZE = 16 * 1024; // 16 KB буфер Ping-Pong

Ov3640Camera::Ov3640Camera(uint8_t sccb_address)
    : sccb_bus_(sccb_address),
      jpeg_parser_(512 * 1024) {}

Ov3640Camera::~Ov3640Camera() {
    stop();
}

bool Ov3640Camera::apply_register_settings(const std::vector<RegisterSetting>& settings) {
    for (const auto& setting : settings) {
        if (!sccb_bus_.write_bank_register(setting.bank, setting.reg, setting.val)) {
            return false;
        }
    }
    return true;
}

bool Ov3640Camera::init() {
    if (!sccb_bus_.init()) {
        return false;
    }

    uint16_t sensor_id = 0;
    if (!sccb_bus_.verify_sensor_id(sensor_id)) {
        return false;
    }

    // Завантаження базовї таблиці ініціалізації регістрів OV3640
    if (!apply_register_settings(registers::get_init_table())) {
        return false;
    }

    // Налаштування умовчальної роздільності та формату
    if (!set_resolution(current_resolution_) || !set_format(current_format_)) {
        return false;
    }

    // Конфігурація DCMI та DMA буферизації
    if (!dcmi_dma_.init(DMA_BUFFER_CHUNK_SIZE)) {
        return false;
    }

    // Прив'язка колбека DMA до обробника камери
    dcmi_dma_.register_callback([this](const uint8_t* buf, size_t sz, uint8_t idx) {
        this->handle_dma_buffer(buf, sz, idx);
    });

    return true;
}

bool Ov3640Camera::set_resolution(Resolution res) {
    if (!apply_register_settings(registers::get_resolution_table(res))) {
        return false;
    }
    current_resolution_ = res;
    return true;
}

bool Ov3640Camera::set_format(ImageFormat fmt) {
    if (!apply_register_settings(registers::get_format_table(fmt))) {
        return false;
    }
    current_format_ = fmt;
    return true;
}

bool Ov3640Camera::set_auto_exposure(bool enable) {
    uint8_t val = 0;
    if (!sccb_bus_.read_bank_register(registers::BANK_0, registers::REG_COM8, val)) {
        return false;
    }
    val = enable ? (val | registers::COM8_AEC) : (val & ~registers::COM8_AEC);
    return sccb_bus_.write_bank_register(registers::BANK_0, registers::REG_COM8, val);
}

bool Ov3640Camera::set_auto_gain(bool enable) {
    uint8_t val = 0;
    if (!sccb_bus_.read_bank_register(registers::BANK_0, registers::REG_COM8, val)) {
        return false;
    }
    val = enable ? (val | registers::COM8_AGC) : (val & ~registers::COM8_AGC);
    return sccb_bus_.write_bank_register(registers::BANK_0, registers::REG_COM8, val);
}

bool Ov3640Camera::set_auto_white_balance(bool enable) {
    uint8_t val = 0;
    if (!sccb_bus_.read_bank_register(registers::BANK_0, registers::REG_COM8, val)) {
        return false;
    }
    val = enable ? (val | registers::COM8_AWB) : (val & ~registers::COM8_AWB);
    return sccb_bus_.write_bank_register(registers::BANK_0, registers::REG_COM8, val);
}

bool Ov3640Camera::start() {
    jpeg_parser_.reset();
    streaming_ = dcmi_dma_.start_capture();
    return streaming_;
}

bool Ov3640Camera::stop() {
    streaming_ = false;
    return dcmi_dma_.stop_capture();
}

void Ov3640Camera::on_frame_ready(OnFrameReadyHandler handler) {
    frame_handler_ = std::move(handler);
}

void Ov3640Camera::handle_dma_buffer(const uint8_t* buffer, size_t size, uint8_t buffer_index) {
    if (current_format_ == ImageFormat::JPEG) {
        jpeg_parser_.process_dma_chunk(buffer, size);
        if (jpeg_parser_.has_complete_frame()) {
            FrameBuffer frame = jpeg_parser_.get_latest_frame();
            if (frame_handler_ && frame.is_valid) {
                frame_handler_(frame);
            }
            jpeg_parser_.reset();
        }
    } else {
        // Обробка нестисненого YUV422 потоку
        if (frame_handler_) {
            FrameBuffer frame;
            frame.data = buffer;
            frame.size = size;
            frame.format = ImageFormat::YUV422;
            frame.is_valid = true;
            frame_handler_(frame);
        }
    }
}

void Ov3640Camera::inject_dma_data(const uint8_t* data, size_t size, uint8_t buffer_index) {
    dcmi_dma_.handle_dma_interrupt(buffer_index);
}

} // namespace camera
