import json
import paho.mqtt.client as mqtt

# Візитівка пристрою для Home Assistant. Це dict, який серіалізуємо в JSON:
# у ньому імена вузла й полів, топіки стану/команди та одиниці. Home Assistant
# прочитає його й сам збудує картку термостата.
DISCOVERY_TOPIC = "homeassistant/climate/livingroom_thermostat/config"

DISCOVERY_PAYLOAD = {
    "name": "Термостат вітальні",                # як підписати картку
    "unique_id": "livingroom_thermostat",        # щоб не задвоївся при переоголошенні
    "temperature_state_topic": "home/livingroom/thermostat/state",
    "temperature_command_topic": "home/livingroom/thermostat/set",
    "availability_topic": "home/livingroom/thermostat/status",
    "temperature_unit": "C",                     # градуси Цельсія, не Фаренгейта
    "min_temp": 5, "max_temp": 35,               # межі повзунка в застосунку
}

# Викликати ОДРАЗУ після успішного під'єднання до брокера.
def announce_to_home_assistant(client: mqtt.Client) -> None:
    # retain=True — критично: візитівка має «висіти» на брокері, щоб
    # Home Assistant знайшов пристрій навіть якщо перезапуститься ПІЗНІШЕ,
    # коли вузол уже давно оголосився й замовк.
    client.publish(DISCOVERY_TOPIC, json.dumps(DISCOVERY_PAYLOAD),
                   qos=1, retain=True)
