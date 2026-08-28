import paho.mqtt.client as mqtt

def on_message(client, userdata, msg):
    # Обробка виконується в тому ж потоці, що й мережевий цикл
    print(f"Отримано: {msg.topic} -> {msg.payload.decode('utf-8')}")

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.on_message = on_message
client.connect("mqtt.internal.iot", 1883, keepalive=60)

# Потік блокується, обслуговуючи з'єднання та зворотні виклики
client.loop_forever()
