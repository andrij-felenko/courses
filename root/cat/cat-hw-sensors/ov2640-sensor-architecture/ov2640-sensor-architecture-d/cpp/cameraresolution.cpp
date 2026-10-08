#include <stdint.h>

enum class CameraResolution { UXGA, SVGA, VGA, QVGA };
enum class CameraFormat { RGB565, YUV422, JPEG };

class OV2640Configurator {
private:
    OV2640BankManager& m_bankMgr;

public:
    OV2640Configurator(OV2640BankManager& bankMgr) : m_bankMgr(bankMgr) {}

    bool configureFormat(CameraFormat fmt) {
        if (fmt == CameraFormat::JPEG) {
            // Перемикаємось у Bank 1 для налаштування DSP та JPEG
            if (!m_bankMgr.writeRegister(1, 0xDA, 0x10)) return false; // JPEG Mode
            if (!m_bankMgr.writeRegister(1, 0xE0, 0x00)) return false; // DSP Reset
            if (!m_bankMgr.writeRegister(1, 0x44, 0x08)) return false; // Quality factor
        } else if (fmt == CameraFormat::RGB565) {
            if (!m_bankMgr.writeRegister(1, 0xDA, 0x09)) return false; // RGB565 Mode
            if (!m_bankMgr.writeRegister(1, 0xE0, 0x00)) return false;
        }
        return true;
    }
};
