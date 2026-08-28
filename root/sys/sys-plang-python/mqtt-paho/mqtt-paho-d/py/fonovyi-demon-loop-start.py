import time
import queue
import paho.mqtt.client as mqtt

# Потокобезпечна черга для ізоляції фонового потоку від головного
telemetry_queue: queue.Queue = queue.Queue(maxsize=10000)

def on_message(client, userdata, msg):
    # Цей код виконується у фоновому потоці paho-mqtt
    try:
        telemetry_queue.put_nowait((msg.topic, msg.payload))
    except queue.Full:
        # Стратегія протитиску: скидання найстарішого пакета або логування
        pass

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.on_message = on_message
client.connect("mqtt.internal.iot", 1883, keepalive=60)

# Запуск фонового мережевого демона
client.loop_start()

try:
    while True:
        # Головний потік займається важкою обробкою та записом на диск
        topic, payload = telemetry_queue.get()
        # Тривала операція запису в БД чи аналітики
        time.sleep(0.005)
        telemetry_queue.task_done()
finally:
    # Коректна зупинка фонового потоку та очікування завершення його join()
    client.loop_stop()
    client.disconnect()
