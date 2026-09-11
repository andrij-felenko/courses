#include <cstdint>

class AudioPowerAmplifier {
public:
    enum class ShutdownPolarity {
        ActiveHigh,  // 1 переводить у сон (SD / SHUTDOWN)
        ActiveLow    // 0 переводить у сон (~SHDN / SHDN_N)
    };

    AudioPowerAmplifier(ShutdownPolarity polarity, uint32_t startup_delay_ms = 150)
        : polarity_(polarity), startup_delay_ms_(startup_delay_ms), is_running_(false) {
        setShutdownPin(true); // Старт у стані сну
    }

    ~AudioPowerAmplifier() {
        powerDown();
    }

    // Безшумна активація з витримкою часу заряду C_BYPASS
    void powerUp() {
        if (is_running_) {
            return;
        }

        setShutdownPin(false);
        platformDelayMs(startup_delay_ms_); // Стабілізація VDD/2 на виходах BTL

        platformStartAudioDac();
        is_running_ = true;
    }

    // Безшумна зупинка без індуктивного викиду на котушці
    void powerDown() {
        if (!is_running_) {
            return;
        }

        platformStopAudioDac(); // Зупинка звуку перед знеструмленням
        platformDelayMs(20);    // Згасання залишкового струму котушки

        setShutdownPin(true);   // Переведення силових ключів у Hi-Z
        is_running_ = false;
    }

    bool isRunning() const { return is_running_; }

private:
    ShutdownPolarity polarity_;
    uint32_t startup_delay_ms_;
    bool is_running_;

    void setShutdownPin(bool shutdown_active) {
        bool pin_state = (polarity_ == ShutdownPolarity::ActiveHigh)
            ? shutdown_active
            : !shutdown_active;
        platformWriteGpio(pin_state);
    }

    // Апаратні виклики мікроконтролерної платформи
    static void platformWriteGpio(bool high);
    static void platformDelayMs(uint32_t ms);
    static void platformStartAudioDac();
    static void platformStopAudioDac();
};
