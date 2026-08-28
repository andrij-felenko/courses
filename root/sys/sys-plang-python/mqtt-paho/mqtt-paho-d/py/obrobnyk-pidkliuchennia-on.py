from paho.mqtt.client import Client, CallbackAPIVersion, ConnectFlags
from paho.mqtt.enums import ReasonCode
from paho.mqtt.properties import Properties

def on_connect(
    client: Client,
    userdata: dict,
    flags: ConnectFlags,
    reason_code: ReasonCode,
    properties: Properties | None
) -> None:
    if reason_code.is_failure:
        print(f"Помилка авторизації або підключення до брокера: {reason_code}")
        return

    print(f"Успішне підключення. Відновлення сесії: {flags.session_present}")

    # Оформлення підписок завжди виконується всередині on_connect!
    # Це гарантує поновлення підписок при автоматичному перепідключенні
    client.subscribe("tenants/+/devices/+/telemetry", qos=1)
