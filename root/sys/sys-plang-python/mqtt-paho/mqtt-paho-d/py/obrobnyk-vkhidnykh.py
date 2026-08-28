from paho.mqtt.client import Client, MQTTMessage

def on_message(client: Client, userdata: dict, message: MQTTMessage) -> None:
    topic: str = message.topic
    payload: bytes = message.payload
    qos: int = message.qos
    retain: bool = message.retain
    mid: int = message.mid

    # Робота з метаданими MQTT 5.0
    if message.properties:
        content_type = getattr(message.properties, "ContentType", "application/json")
        user_properties = getattr(message.properties, "UserProperty", [])
        print(f"Формат: {content_type}, Користувацькі мітки: {user_properties}")

    # Збереження або оновлення стану через переданий контекст
    userdata["counter"] += 1
