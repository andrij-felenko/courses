#include <Arduino.h>

class HardwareResetDiagnostics {
public:
    static void printResetReason() {
        rst_info* rtcInfo = ESP.getResetInfoPtr();
        Serial.print(F("Код скидання reset cause: "));
        Serial.println(rtcInfo->reason);

        switch (rtcInfo->reason) {
            case REASON_DEFAULT_RST:
                Serial.println(F("Старт: нормальна подача живлення (POR)"));
                break;
            case REASON_WDT_RST:
                Serial.println(F("Старт: переповнення апаратного вартового таймера WDT"));
                break;
            case REASON_EXT_SYS_RST:
                Serial.println(F("Старт: імпульс на лінії RST або супервізорі"));
                break;
            default:
                Serial.println(F("Старт: інша апаратна причина"));
                break;
        }
    }
};
