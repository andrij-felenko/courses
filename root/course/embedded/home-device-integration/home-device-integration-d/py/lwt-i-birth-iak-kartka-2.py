# Підписка на birth-топік Home Assistant: коли HA стартує, він кричить сюди.
# paho кличе on_connect одразу по успішному під'єднанні.
def on_mqtt_connected(client, userdata, flags, rc):
    announce_alive(client)
    announce_to_home_assistant(client)     # візитівка (з попереднього кроку)
    client.subscribe("homeassistant/status", qos=1)

# Прийшло щось у homeassistant/status — HA щойно ожив і просить рекомендуватися.
def on_message(client, userdata, msg):
    if msg.topic == "homeassistant/status" and msg.payload == b"online":
        announce_to_home_assistant(client)  # переоголошуємо себе
        publish_current_state(client)       # і одразу свіже число
