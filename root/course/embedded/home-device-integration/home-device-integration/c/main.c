// Візитівка пристрою для Home Assistant. Це JSON-рядок: у ньому імена
// вузла й полів, топіки стану/команди та одиниці. Home Assistant прочитає
// його й сам збудує картку термостата.
static const char *DISCOVERY_TOPIC =
    "homeassistant/climate/livingroom_thermostat/config";

static const char *DISCOVERY_PAYLOAD =
    "{"
      "\"name\":\"Термостат вітальні\","        // як підписати картку
      "\"unique_id\":\"livingroom_thermostat\"," // щоб не задвоївся при переоголошенні
      "\"temperature_state_topic\":\"home/livingroom/thermostat/state\","
      "\"temperature_command_topic\":\"home/livingroom/thermostat/set\","
      "\"availability_topic\":\"home/livingroom/thermostat/status\","
      "\"temperature_unit\":\"C\","             // градуси Цельсія, не Фаренгейта
      "\"min_temp\":5,\"max_temp\":35"           // межі повзунка в застосунку
    "}";

// Викликати ОДРАЗУ після успішного під'єднання до брокера.
static void announce_to_home_assistant(void) {
    // retain=true — критично: візитівка має «висіти» на брокері, щоб
    // Home Assistant знайшов пристрій навіть якщо перезапуститься ПІЗНІШЕ,
    // коли вузол уже давно оголосився й замовк.
    mqtt_publish(DISCOVERY_TOPIC, DISCOVERY_PAYLOAD,
                 strlen(DISCOVERY_PAYLOAD), /*qos=*/1, /*retain=*/true);
}
