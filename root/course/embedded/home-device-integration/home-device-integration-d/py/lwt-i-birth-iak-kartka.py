STATUS_TOPIC = "home/livingroom/thermostat/status"

# Заповіт РЕЄСТРУЄМО в момент з'єднання з брокером — ще ДО publish.
# will_set кладе ці поля в пакет CONNECT; брокер притримає їх у себе.
def mqtt_connect_with_will(client):
    client.will_set(
        STATUS_TOPIC,
        payload="offline",   # це брокер опублікує ЗА нас, коли ми зникнемо
        qos=1,
        retain=True,         # щоб «offline» теж пережив підписку HA пізніше
    )
    # тиша довша за 1.5×30 с → брокер вважає нас мертвими
    client.connect("broker.local", 1883, keepalive=30)

# А ЦЕ — одразу після успішного під'єднання: перекриваємо заповіт живим «online».
def announce_alive(client):
    client.publish(STATUS_TOPIC, "online", qos=1, retain=True)
