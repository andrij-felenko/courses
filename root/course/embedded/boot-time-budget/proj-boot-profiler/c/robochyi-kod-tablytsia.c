#include "esp_timer.h"
#include "esp_log.h"
#include "esp_system.h"
#include "esp_cpu.h"

static const char *TAG = "bootprof";

// Калібрування з одноразового заміру аналізатором на столі (див. вище).
// Голова ланцюга (ПЗП+стрепи) стала, тож зберігаємо її як константу.
#define T_PZP_US        6000    // ПЗП+стрепи, мкс (решта від цілого, заміряно раз)

typedef struct {
    const char *link;     // назва ланки
    int64_t     us;       // її час, мкс
    const char *lever;    // чим коротшати
} prof_row_t;

void boot_profile_report(void)
{
    // 1. Звідки прокинулись — від цього залежить, що взагалі виконувалось.
    const char *kind;
    bool from_sleep = false;
    switch (esp_reset_reason()) {
        case ESP_RST_DEEPSLEEP: kind = "пробудження зі сну"; from_sleep = true; break;
        case ESP_RST_POWERON:   kind = "холодний boot";                         break;
        default:                kind = "інше скидання";                          break;
    }

    // 2. Внутрішні числа.
    int64_t t_app  = esp_timer_get_time();              // старт ESP-IDF → зараз
    uint32_t cyc   = esp_cpu_get_cycle_count();         // такти від старту ядра
    // груба оцінка межі завантажувача зсередини (наближено, див. пастки):
    int64_t t_bl_est = (int64_t)cyc / 160 - t_app;      // 160 тактів/мкс при 160 МГц
    if (t_bl_est < 0) t_bl_est = 0;

    // 3. Зібрати таблицю. Для пробудження зі стабом дорогі ланки зрізано.
    prof_row_t rows[] = {
        { "ПЗП + стрепи",        from_sleep ? 0 : T_PZP_US,
          "майже сталий; при сні — оминається стабом" },
        { "завантажувач (образ+SHA)", from_sleep ? 0 : t_bl_est,
          "швидша/ширша Flash (QIO, 80 МГц); пропуск SHA при сні" },
        { "старт ESP-IDF → app_main", t_app,
          "менше ініціалізаторів і конструкторів; тихіший лог" },
    };

    // 4. Надрукувати як таблицю «ланка → час → важіль».
    ESP_LOGI(TAG, "==== профіль завантаження: %s ====", kind);
    int64_t total = 0;
    for (size_t i = 0; i < sizeof(rows)/sizeof(rows[0]); ++i) {
        ESP_LOGI(TAG, "%-26s %6lld мкс  | %s",
                 rows[i].link, rows[i].us, rows[i].lever);
        total += rows[i].us;
    }
    ESP_LOGI(TAG, "%-26s %6lld мкс  (%.1f мс)", "РАЗОМ", total, total / 1000.0);
    ESP_LOGI(TAG, "================================");
}
