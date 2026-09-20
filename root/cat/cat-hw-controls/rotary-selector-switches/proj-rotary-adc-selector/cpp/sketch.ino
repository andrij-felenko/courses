#include <Arduino.h>
#include "RotarySelector.h"

static const uint8_t ROTARY_ADC_PIN = A0;

static RotarySelector selector(ROTARY_ADC_PIN, 30);

void onSelectorPositionChanged(const SelectorEvent& event) {
    if (event.status == SelectorStatus::OK) {
        Serial.print(F("[SELECTOR] Нова позиція: "));
        Serial.print(event.position);
        Serial.print(F(" (АЦП: "));
        Serial.print(event.rawAdc);
        Serial.println(F(")"));
    } else if (event.status == SelectorStatus::FAULT_OPEN_CIRCUIT) {
        Serial.print(F("[ERROR] Аварія: Обрив лінії селектора! АЦП = "));
        Serial.println(event.rawAdc);
    } else if (event.status == SelectorStatus::FAULT_SHORT_CIRCUIT) {
        Serial.print(F("[ERROR] Аварія: Коротке замикання селектора! АЦП = "));
        Serial.println(event.rawAdc);
    }
}

void setup() {
    Serial.begin(115200);
    while (!Serial) {
        ;
    }

    Serial.println(F("=== Ініціалізація 12-позиційного галетного перемикача ==="));
    analogReadResolution(12);

    selector.setCallback(onSelectorPositionChanged);
}

void loop() {
    uint32_t currentMs = millis();
    uint16_t rawAdc = analogRead(ROTARY_ADC_PIN);

    selector.update(currentMs, rawAdc);

    delay(2);
}
