from paho.mqtt.client import Client, DisconnectFlags
from paho.mqtt.enums import ReasonCode
from paho.mqtt.properties import Properties

def on_disconnect(
    client: Client,
    userdata: dict,
    flags: DisconnectFlags,
    reason_code: ReasonCode,
    properties: Properties | None
) -> None:
    if reason_code == 0:
        print("Штатне завершення сесії за командою client.disconnect().")
    else:
        print(f"Аварійний обрив TCP-з'єднання ({reason_code}). Запуск процедури reconnect...")
