#include <stdbool.h>
#include <stdint.h>

#define AMP_STARTUP_DELAY_MS   150  // Затримка заряду C_BYPASS (t_startup ≈ 4.6 * tau)
#define AMP_MUTE_SETTLE_MS      20  // Пауза згасання струму котушки перед вимкненням

// Апаратні виклики платформи
void platform_gpio_write_shutdown(bool level_high);
void platform_audio_dac_start(void);
void platform_audio_dac_stop(void);
void platform_delay_ms(uint32_t ms);

typedef struct {
    bool is_active_high;  // true: активний високий (SD); false: активний низький (~SHDN)
    bool is_powered;      // Поточний стан живлення
} AudioAmp;

// Початковий перехід у сон для збереження заряду батареї
void audio_amp_init(AudioAmp *amp, bool active_high) {
    amp->is_active_high = active_high;
    amp->is_powered = false;
    platform_gpio_write_shutdown(amp->is_active_high ? true : false);
}

// Безшумне пробудження: затримка заряду C_BYPASS перед запуском аудіо
void audio_amp_power_on(AudioAmp *amp) {
    if (amp->is_powered) {
        return;
    }

    platform_gpio_write_shutdown(amp->is_active_high ? false : true);
    platform_delay_ms(AMP_STARTUP_DELAY_MS); // Очікування стабілізації VDD/2 на виходах

    platform_audio_dac_start();
    amp->is_powered = true;
}

// Безпечне вимкнення: глушіння аудіо перед знеструмленням кристала
void audio_amp_power_off(AudioAmp *amp) {
    if (!amp->is_powered) {
        return;
    }

    platform_audio_dac_stop();                // 1. Зупинка звуку
    platform_delay_ms(AMP_MUTE_SETTLE_MS);    // 2. Згасання струму котушки
    platform_gpio_write_shutdown(amp->is_active_high ? true : false); // 3. Перехід у Hi-Z

    amp->is_powered = false;
}
