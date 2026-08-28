import json, time
import paho.mqtt.client as mqtt

hub = mqtt.Client(client_id="hub-42")
hub.connect("broker.digitalhomes.io", 1883)
hub.loop_start()   # мережа крутиться у фоновому потоці; publish НЕ блокує

def on_reading(dev_id: str, value: float) -> None:
    topic = f"dh/home/42/{dev_id}/reading"
    payload = json.dumps({"v": value, "at": int(time.time() * 1000)})
    hub.publish(topic, payload, qos=1)   # поклав у буфер і повернувся — відповіді не чекаємо
