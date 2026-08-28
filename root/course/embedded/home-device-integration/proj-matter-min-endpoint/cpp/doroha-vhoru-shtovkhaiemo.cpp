// Викликати з нашого циклу/таймера, коли давач дав свіже число.
static void publish_temperature(float celsius)
{
    // Перетворення в модельні одиниці — соті градуса. 21.37 °C -> 2137.
    // lroundf, а не (int): щоб 21.375 не «обрізалось» униз, а округлилось.
    int16_t hundredths = (int16_t) lroundf(celsius * 100.0f);

    // Значення для моделі. nullable — бо LocalTemperature має право бути
    // «невідомою» (null), поки давач не прогрівся; тут даємо конкретне число.
    esp_matter_attr_val_t val = esp_matter_nullable_int16(hundredths);

    // 1) У кластер вимірювання (0x0402), атрибут MeasuredValue (0x0000).
    attribute::update(s_endpoint_id,
                      TemperatureMeasurement::Id,
                      TemperatureMeasurement::Attributes::MeasuredValue::Id,
                      &val);

    // 2) У сам термостат (0x0201), атрибут LocalTemperature (0x0000) —
    //    щоб картка термостата показувала «поточну» біля «цільової».
    attribute::update(s_endpoint_id,
                      Thermostat::Id,
                      Thermostat::Attributes::LocalTemperature::Id,
                      &val);
}
