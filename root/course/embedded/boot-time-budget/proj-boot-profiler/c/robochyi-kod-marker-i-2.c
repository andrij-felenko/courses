#include "esp_system.h"

const char *reset_kind(void)
{
    switch (esp_reset_reason()) {
        case ESP_RST_POWERON:   return "холодний (подача живлення)";
        case ESP_RST_DEEPSLEEP: return "пробудження з глибокого сну";
        case ESP_RST_SW:        return "програмне перезавантаження";
        case ESP_RST_PANIC:     return "після аварії (panic)";
        case ESP_RST_BROWNOUT:  return "просідання живлення (brown-out)";
        default:                return "інше";
    }
}
