// platform.h — вимощена дорога: один перевірений старт для всіх команд.
// Продуктова команда не вникає в регістри — просто кличе platform_boot().
typedef struct {
    uint32_t cpu_hz;          // бажана частота ядра
    bool     watchdog;        // увімкнути вартовий таймер
    uint16_t log_baud_kbps;   // швидкість журнального UART, 0 = без журналу
} platform_cfg_t;

// Значення за замовчуванням — та сама «золота стежка» для всіх.
#define PLATFORM_DEFAULT_CFG ((platform_cfg_t){ .cpu_hz = 72000000u, \
                               .watchdog = true, .log_baud_kbps = 115u })

// Повертає 0, якщо система піднялася коректно, інакше — код помилки.
int platform_boot(const platform_cfg_t *cfg);
