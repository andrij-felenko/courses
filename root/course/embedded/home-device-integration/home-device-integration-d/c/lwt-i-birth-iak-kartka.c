static const char *STATUS_TOPIC = "home/livingroom/thermostat/status";

// Заповіт РЕЄСТРУЄМО в момент з'єднання з брокером — ще ДО publish.
// Ці поля йдуть у пакет CONNECT; брокер притримає їх у себе.
static void mqtt_connect_with_will(mqtt_client_t *c) {
    mqtt_connect_options_t opt = {0};
    opt.will_topic   = STATUS_TOPIC;
    opt.will_message = "offline";   // це брокер опублікує ЗА нас, коли ми зникнемо
    opt.will_qos     = 1;
    opt.will_retain  = true;        // щоб «offline» теж пережив підписку HA пізніше
    opt.keep_alive   = 30;          // тиша довша за 1.5×30 с → брокер вважає нас мертвими
    mqtt_connect(c, &opt);
}

// А ЦЕ — одразу після успішного під'єднання: перекриваємо заповіт живим «online».
static void announce_alive(void) {
    mqtt_publish(STATUS_TOPIC, "online", 6, /*qos=*/1, /*retain=*/true);
}
