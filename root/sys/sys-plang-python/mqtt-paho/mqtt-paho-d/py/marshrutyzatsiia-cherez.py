def handle_telemetry(client, userdata, msg):
    # Обробка даних вимірювань
    pass

def handle_alerts(client, userdata, msg):
    # Пріоритетна обробка критичних тривог
    pass

client.message_callback_add("tenants/+/devices/+/telemetry", handle_telemetry)
client.message_callback_add("tenants/+/devices/+/alerts", handle_alerts)
