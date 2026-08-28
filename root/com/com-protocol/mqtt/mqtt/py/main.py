# Той самий клієнт мовою Python — бібліотека paho-mqtt.
import paho.mqtt.client as mqtt

# на з'єднання: підписуємось на топік команд і публікуємо показання
def on_connect(client, userdata, flags, rc):
    client.subscribe("home/room/cmd", qos=1)          # 1) топік команд (QoS 1)
    # 2) показання: QoS 1, retain=True (брокер запам'ятає як останнє значення)
    client.publish("home/room/temp", "23.4", qos=1, retain=True)
    print("під'єднано: підписались і опублікували")

# прийшло повідомлення на топік, на який ми підписані
def on_message(client, userdata, msg):
    # тут payload — це bytes, тож декодуємо в рядок
    print(f"топік {msg.topic} = {msg.payload.decode()}")

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

# "остання воля": брокер опублікує, якщо ми зникнемо раптово
client.will_set("home/room/status", "offline", qos=1, retain=True)

client.connect("192.168.1.10", 1883, keepalive=60)    # адреса брокера, keepalive 60 с
client.loop_forever()   # під'єднатись і крутити обмін (пінги — сама бібліотека)
