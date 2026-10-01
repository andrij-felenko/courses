#include <ESP.h>

void setup() {
    Serial.begin(74880);
    
    struct rst_info *rtc_info = ESP.getResetInfoPtr();
    Serial.print("Reset reason: ");
    Serial.println(ESP.getResetReason());
    
    if (rtc_info->reason == REASON_EXCEPTION_RST) {
        Serial.printf("Fatal Exception epc1=0x%08x excvaddr=0x%08x\n",
                      rtc_info->epc1, rtc_info->excvaddr);
    }
}

void loop() {}
