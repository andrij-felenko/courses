#include "ov2640_driver.hpp"
#include "ov2640_registers.hpp"
#include <iostream>
#include <thread>
#include <chrono>

namespace ov2640 {

Ov2640Driver::Ov2640Driver(SccbBus& sccb, DcmiDmaBuffer& dcmi_dma)
    : sccb_(sccb),
      dcmi_dma_(dcmi_dma),
      current_resolution_(FrameResolution::SVGA_800x600),
      current_format_(PixelFormat::JPEG),
      jpeg_quality_(12),
      is_streaming_(false) {}

Ov2640Driver::~Ov2640Driver() {
    stopStreaming();
}

bool Ov2640Driver::init() {
    if (sccb_.init() != SccbStatus::Ok) {
        return false;
    }

    if (!reset()) {
        return false;
    }

    uint8_t pid = 0;
    uint8_t ver = 0;
    if (sccb_.verifyDeviceId(pid, ver) != SccbStatus::Ok) {
        return false;
    }

    if (!loadInitTable()) {
        return false;
    }

    if (!dcmi_dma_.init()) {
        return false;
    }

    return setResolution(FrameResolution::SVGA_800x600);
}

bool Ov2640Driver::reset() {
    // Програмне скидання через регістр COM7 у банку Sensor (0x01)
    if (sccb_.selectBank(RegisterBank::Sensor) != SccbStatus::Ok) {
        return false;
    }

    if (sccb_.writeRegister(REG_SENSOR_COM7, COM7_SOFT_RESET) != SccbStatus::Ok) {
        return false;
    }

    // Затримка для стабілізації системної генерації камери після скидання
    std::this_thread::sleep_for(std::chrono::milliseconds(100));

    return sccb_.selectBank(RegisterBank::DSP) == SccbStatus::Ok;
}

bool Ov2640Driver::setResolution(FrameResolution res) {
    if (!configureResolution(res)) {
        return false;
    }
    current_resolution_ = res;
    return true;
}

bool Ov2640Driver::setPixelFormat(PixelFormat format) {
    if (sccb_.selectBank(RegisterBank::DSP) != SccbStatus::Ok) {
        return false;
    }

    uint8_t bypass_val = (format == PixelFormat::JPEG) ? 0x00 : 0x01;
    if (sccb_.writeRegister(REG_DSP_R_BYPASS, bypass_val) != SccbStatus::Ok) {
        return false;
    }

    current_format_ = format;
    return true;
}

bool Ov2640Driver::setJpegQuality(uint8_t quality) {
    if (quality < 1) quality = 1;
    if (quality > 63) quality = 63;

    if (sccb_.selectBank(RegisterBank::DSP) != SccbStatus::Ok) {
        return false;
    }

    if (sccb_.writeRegister(REG_DSP_QS, quality) != SccbStatus::Ok) {
        return false;
    }

    jpeg_quality_ = quality;
    return true;
}

bool Ov2640Driver::setBrightness(int8_t level) {
    if (level < -2 || level > 2) return false;

    if (sccb_.selectBank(RegisterBank::DSP) != SccbStatus::Ok) {
        return false;
    }

    // Оновлення регістрів яскравості у банку DSP
    uint8_t brightness_val = static_cast<uint8_t>(level + 2) * 0x20;
    return sccb_.writeRegister(0x55, brightness_val) == SccbStatus::Ok;
}

bool Ov2640Driver::setContrast(int8_t level) {
    if (level < -2 || level > 2) return false;

    if (sccb_.selectBank(RegisterBank::DSP) != SccbStatus::Ok) {
        return false;
    }

    uint8_t contrast_val = static_cast<uint8_t>(level + 2) * 0x18;
    return sccb_.writeRegister(0x56, contrast_val) == SccbStatus::Ok;
}

bool Ov2640Driver::setSpecialEffect(SpecialEffect effect) {
    if (sccb_.selectBank(RegisterBank::DSP) != SccbStatus::Ok) {
        return false;
    }

    uint8_t effect_code = static_cast<uint8_t>(effect);
    return sccb_.writeRegister(0x67, effect_code) == SccbStatus::Ok;
}

bool Ov2640Driver::startStreaming(DcmiDmaBuffer::FrameReadyCallback callback) {
    dcmi_dma_.setFrameCallback(callback);
    if (!dcmi_dma_.startCapture()) {
        return false;
    }
    is_streaming_ = true;
    return true;
}

void Ov2640Driver::stopStreaming() {
    dcmi_dma_.stopCapture();
    is_streaming_ = false;
}

void Ov2640Driver::process() {
    if (!is_streaming_) return;

    // Симуляція генерації апаратного кадру та виклику переривання DCMI Frame Interrupt
    // Створюємо валідний JPEG заголовок (SOI 0xFF 0xD8, EOI 0xFF 0xD9)
    const size_t sim_frame_size = 8192;
    const FrameBuffer& buf = dcmi_dma_.getBuffer(0);

    if (buf.data != nullptr) {
        buf.data[0] = 0xFF;
        buf.data[1] = 0xD8; // JPEG Start of Image (SOI)
        
        // Заповнення фейковими даними зображення
        for (size_t i = 2; i < sim_frame_size - 2; ++i) {
            buf.data[i] = static_cast<uint8_t>(i & 0xFF);
        }

        buf.data[sim_frame_size - 2] = 0xFF;
        buf.data[sim_frame_size - 1] = 0xD9; // JPEG End of Image (EOI)

        dcmi_dma_.handleDcmiFrameInterrupt(sim_frame_size);
    }
}

bool Ov2640Driver::loadInitTable() {
    size_t sensor_init_count = sizeof(OV2640_SENSOR_INIT) / sizeof(OV2640_SENSOR_INIT[0]);
    if (sccb_.writeRegisterList(OV2640_SENSOR_INIT, sensor_init_count) != SccbStatus::Ok) {
        return false;
    }

    size_t dsp_init_count = sizeof(OV2640_DSP_INIT) / sizeof(OV2640_DSP_INIT[0]);
    if (sccb_.writeRegisterList(OV2640_DSP_INIT, dsp_init_count) != SccbStatus::Ok) {
        return false;
    }

    return true;
}

bool Ov2640Driver::configureResolution(FrameResolution res) {
    const uint8_t (*config_table)[2] = nullptr;
    size_t count = 0;

    switch (res) {
        case FrameResolution::UXGA_1600x1200:
            config_table = OV2640_JPEG_UXGA_CONFIG;
            count = sizeof(OV2640_JPEG_UXGA_CONFIG) / sizeof(OV2640_JPEG_UXGA_CONFIG[0]);
            break;

        case FrameResolution::SVGA_800x600:
            config_table = OV2640_JPEG_SVGA_CONFIG;
            count = sizeof(OV2640_JPEG_SVGA_CONFIG) / sizeof(OV2640_JPEG_SVGA_CONFIG[0]);
            break;

        case FrameResolution::CIF_352x288:
            config_table = OV2640_JPEG_CIF_CONFIG;
            count = sizeof(OV2640_JPEG_CIF_CONFIG) / sizeof(OV2640_JPEG_CIF_CONFIG[0]);
            break;

        default:
            return false;
    }

    return sccb_.writeRegisterList(config_table, count) == SccbStatus::Ok;
}

} // namespace ov2640
